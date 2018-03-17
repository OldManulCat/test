import asyncio
import decimal
import time
from aiohttp import web
import aiopg
from aiopg.transaction import Transaction, IsolationLevel


dsn = 'dbname=test user=testuser password=testpassword'
rates = {
         'EUR_USD': 01.2400, 'USD_EUR': 0.8165,
         'EUR_RUB': 70.5300, 'RUB_EUR': 0.0142,
         'USD_RUB': 56.8000, 'RUB_USD': 0.0176
        }


async def handle(request):
    a_id = 0
    a_balance = 0.0
    a_currency = 'RUB'
    try:
        c_id = request.match_info.get('id')
        a_id = int(c_id)
        async with request.app['database'].acquire() as connect:
            async with connect.cursor() as cursor:
                await cursor.execute('SELECT currency, balance FROM account WHERE id=%d' % (a_id))
                row  = await cursor.fetchone()
                if row:
                    a_currency = row[0]
                    a_balance = float(row[1])
    except Exception as e:
        print(e)
        raise e
    data = {'currency': a_currency, 'balance': a_balance}
    return web.json_response(data)

async def create_account(request):
    a_id=0
    try:
        data = await request.json()
        ts = time.time()
        dt = '%s.%s' % (time.strftime('%Y-%m-%d %H:%M:%S'), ('%0.6f' % (ts - int(ts)))[2:])
        async with request.app['database'].acquire() as connect:
            async with connect.cursor() as cursor:
                await cursor.execute(
                    'INSERT INTO account (currency, is_overdraft, created) VALUES (\'%s\', %s, \'%s\') RETURNING id' 
                                       % (data['currency'].upper(), data['is_overdraft'].upper()=='TRUE', dt)
                                     )
                row  = await cursor.fetchone()
                a_id = row[0]
        print('%s (%.4f) New account (Carrency: %s, Overdraft: %s) with ID: %d'
              % (dt, ts, data['currency'].upper(), data['is_overdraft'], a_id))
    except Exception as e:
        print(e)
    return web.json_response({'id': a_id})

async def exchange(request):
    result = None
    try:
        data = await request.json()
        o_id = 0
        ts = time.time()
        dt = '%s.%s' % (time.strftime('%Y-%m-%d %H:%M:%S'), ('%0.6f' % (ts - int(ts)))[2:])
        async with request.app['database'].acquire() as connect:
            async with connect.cursor() as cursor:
                await cursor.execute(
                    'INSERT INTO operation (transaction_status, amount, out_account, in_account, started) \
                                            VALUES (\'NEW\', %f, %d, %d,\'%s\') RETURNING id' 
                                       % (data['amount'], data['out'], data['in'], dt)
                                     )
                row  = await cursor.fetchone()
                o_id = row[0]
                print('%s (%.4f) New operation (Transfer account: %d, Debt account: %d, Amount: %.4f) with ID: %d'
                     % (dt, ts, data['out'], data['in'], data['amount'], o_id))
                await cursor.execute('BEGIN')
                await cursor.execute('SELECT id, currency, is_overdraft, balance FROM account \
                                       WHERE id IN (%d, %d) FOR UPDATE' % (data['out'], data['in']))
                row = await cursor.fetchall()
                if len(row)==2:
                    out_balance = 0
                    in_balance = 0
                    if row[0][0]==data['out']:
                        out_balance = row[0][3] - data['amount']
                        if out_balance < 0 and not row[0][2]:
                            result = {'success': False}
                        else:
                            k = rates['%s_%s' % (row[1][1], row[0][1])] if row[0][1] != row[1][1] else 1.0
                            in_balance = row[1][3] + decimal.Decimal((0.0+data['amount'])/k)
                            result = {'success': True}
                    else:
                        out_balance = row[1][3] - data['amount']
                        if out_balance < 0 and not row[1][2]:
                            result = {'success': False}
                        else:
                            k = rates['%s_%s' % (row[0][1], row[1][1])] if row[1][1] != row[0][1] else 1.0
                            in_balance = row[0][3] + decimal.Decimal((0.0+data['amount'])/k)
                            result = {'success': True}
                else:
                    result = {'success': False}
                if result['success']:
                    await cursor.execute('UPDATE account SET balance=%.4f WHERE id=%d' % (out_balance, data['out']))
                    await cursor.execute('UPDATE account SET balance=%.4f WHERE id=%d' % (in_balance, data['in']))
                    await cursor.execute('COMMIT')
                    ts = time.time()
                    dt = '%s.%s' % (time.strftime('%Y-%m-%d %H:%M:%S'), ('%0.6f' % (ts - int(ts)))[2:])
                    await cursor.execute('UPDATE operation SET transaction_status=\'PROCESSED\', ended=\'%s\' \
                                           WHERE id=%d' % (dt, o_id))
                    print('%s (%.4f) operation (Transfer account: %d, Debt account: %d, Amount: %.4f) with ID: %d finished'
                        % (dt, ts, data['out'], data['in'], data['amount'], o_id))
                else:
                    await cursor.execute('ROLLBACK')
                    await cursor.execute('UPDATE operation SET transaction_status=\'DECLINE\' \
                                           WHERE id=%d' % (o_id))
                    print('%s (%.4f) operation (Transfer account: %d, Debt account: %d, Amount: %.4f) with ID: %d declined'
                        % (dt, ts, data['out'], data['in'], data['amount'], o_id))
        
    except Exception as e:
        print(e)
        result = {'success': False}
#        raise e
    
    return web.json_response(result)

async def init_db(application):
    pool = await aiopg.create_pool(dsn)
    application['database'] = pool

async def release_db(application):
    application['database'].close()
    await application['database'].wait_closed()

loop=asyncio.get_event_loop()
app = web.Application(loop=loop)
app.on_startup.append(init_db)
app.on_cleanup.append(release_db)
app.router.add_put('/create', create_account)
app.router.add_post('/exchange', exchange)
app.router.add_get('/{id}', handle)
web.run_app(app)

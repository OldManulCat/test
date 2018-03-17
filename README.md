# Testing of various technologies and programming techniques

Epigraph:
_Autumn_ _2000._ _Project_ _BeeOnLine_

_I (type on the keyboard):_
    $ /opt/bin/java/bin/java test/brodcaster.java
    Broadcaster started...
    Broadcaster ended...
_Sergey Samorodsky:_
_- A great start for broadcaster daemon!!!_


## Python language

### Aserver - web service billing

Working out skills with the following technologies:
* JSON
* HTTP
* async/await in python
* SQL
* Transaction

Install:
    psql -U postgres
    CREATE USER testuser PASSWORD 'testpassword';
    CREATE DATABASE test OWNER testuser;
    \c test
    \i aserver/test.sql
    Ctrl-D

Start:
    python aserver/aserver.py

Testing:
    curl -H "Content-Type: application/json" -X PUT -d '{"currency":"eur","is_overdraft":"True"}' http://localhost:8080/create
    curl -H "Content-Type: application/json" -X PUT -d '{"currency":"usd","is_overdraft":"True"}' http://localhost:8080/create
    curl -H "Content-Type: application/json" -X PUT -d '{"currency":"rub","is_overdraft":"True"}' http://localhost:8080/create
    curl -H "Content-Type: application/json" -X PUT -d '{"currency":"eur","is_overdraft":"False"}' http://localhost:8080/create
    curl -H "Content-Type: application/json" -X PUT -d '{"currency":"usd","is_overdraft":""}' http://localhost:8080/create
    curl -H "Content-Type: application/json" -X PUT -d '{"currency":"rub","is_overdraft":""}' http://localhost:8080/create

    curl -v -H "Content-Type: application/json" -X POST -d "{\"out\": 2, \"in\": 5, \"amount\": 10000}" http://localhost:8080/exchange
    curl -v -H "Content-Type: application/json" -X POST -d "{\"out\": 1, \"in\": 6, \"amount\": 10000}" http://localhost:8080/exchange
    curl -v -H "Content-Type: application/json" -X POST -d "{\"out\": 4, \"in\": 5, \"amount\": 10000}" http://localhost:8080/exchange

account balances can be viewed in the browser at the link _http://localhost:8080/<id>_, where the corresponding account number from the examples above is substituted instead of _<id>_.

--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3
-- Dumped by pg_dump version 10.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: account_id; Type: SEQUENCE; Schema: public; Owner: testuser
--

CREATE SEQUENCE public.account_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_id OWNER TO testuser;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: account; Type: TABLE; Schema: public; Owner: testuser
--

CREATE TABLE public.account (
    id integer DEFAULT nextval('public.account_id'::regclass) NOT NULL,
    currency character(3) NOT NULL,
    is_overdraft boolean DEFAULT false NOT NULL,
    balance numeric(20,4) DEFAULT 0.0 NOT NULL,
    created timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.account OWNER TO testuser;

--
-- Name: operation_id; Type: SEQUENCE; Schema: public; Owner: testuser
--

CREATE SEQUENCE public.operation_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.operation_id OWNER TO testuser;

--
-- Name: operation; Type: TABLE; Schema: public; Owner: testuser
--

CREATE TABLE public.operation (
    id integer DEFAULT nextval('public.operation_id'::regclass) NOT NULL,
    transaction_status character(16) NOT NULL,
    amount numeric(20,4),
    created timestamp without time zone DEFAULT now() NOT NULL,
    out_account integer DEFAULT 0 NOT NULL,
    in_account integer DEFAULT 0 NOT NULL,
    started timestamp without time zone DEFAULT now() NOT NULL,
    ended timestamp without time zone
);


ALTER TABLE public.operation OWNER TO testuser;

--
-- Name: account account_pkey; Type: CONSTRAINT; Schema: public; Owner: testuser
--

ALTER TABLE ONLY public.account
    ADD CONSTRAINT account_pkey PRIMARY KEY (id);


--
-- Name: operation operation_pkey; Type: CONSTRAINT; Schema: public; Owner: testuser
--

ALTER TABLE ONLY public.operation
    ADD CONSTRAINT operation_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


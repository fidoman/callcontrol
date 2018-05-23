--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.6
-- Dumped by pg_dump version 9.6.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
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


SET search_path = public, pg_catalog;

--
-- Name: check_ext_pw(character varying, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION check_ext_pw(ext character varying, pw character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
declare
  r integer;
begin
  select count(*) into r from extensions where ext_n=ext and ext_pw=pw;
  return r;
end;
$$;


ALTER FUNCTION public.check_ext_pw(ext character varying, pw character varying) OWNER TO postgres;

--
-- Name: operators_history(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION operators_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
  -- TG_OP
  if (TG_OP = 'INSERT') then -- insert
    insert into operator_group_history select new.op_id, now(), null, new.op_group;
    insert into operator_ext_history select new.op_id, now(), null, new.op_ext;
    return new;
  elsif (TG_OP = 'DELETE') then -- delete
    insert into operator_group_history select old.op_id, now(), old.op_group, null;
    insert into operator_ext_history select old.op_id, now(), old.op_ext, null;
    return old;
  elsif (TG_OP = 'UPDATE') then
    if (new.op_group <> old.op_group) then
      insert into operator_group_history select new.op_id, now(), old.op_group, new.op_group;
    end if;

    if (new.op_ext <> old.op_ext) then
      insert into operator_ext_history select new.op_id, now(), old.op_ext, new.op_ext;
    end if;
    return new;
  end if;
  return null;
end;
$$;


ALTER FUNCTION public.operators_history() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: call_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE call_log (
    cl_id bigint NOT NULL,
    cl_rand character(32),
    cl_tag integer,
    cl_operator integer,
    cl_rec_uid character varying,
    cl_client_phone character varying,
    cl_shop_phone character varying,
    cl_shop_name character varying,
    cl_ring_time timestamp with time zone,
    cl_answer_time timestamp with time zone,
    cl_end_time timestamp with time zone,
    cl_close_time timestamp with time zone,
    cl_note character varying,
    cl_operator_name character varying,
    cl_order character varying,
    cl_uid character varying,
    cl_direction character varying,
    cl_tagdata character varying,
    cl_shop_lkid character varying
);


ALTER TABLE call_log OWNER TO postgres;

--
-- Name: call_log_cl_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE call_log_cl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE call_log_cl_id_seq OWNER TO postgres;

--
-- Name: call_log_cl_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE call_log_cl_id_seq OWNED BY call_log.cl_id;


--
-- Name: call_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE call_status (
    cs_id bigint NOT NULL,
    cs_op integer,
    cs_phone character varying,
    cs_order character varying,
    cs_note character varying,
    cs_tag integer
);


ALTER TABLE call_status OWNER TO postgres;

--
-- Name: call_status_cs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE call_status_cs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE call_status_cs_id_seq OWNER TO postgres;

--
-- Name: call_status_cs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE call_status_cs_id_seq OWNED BY call_status.cs_id;


--
-- Name: cdr; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE cdr (
    id integer NOT NULL,
    calldate timestamp with time zone DEFAULT now() NOT NULL,
    clid character varying(80),
    src character varying(80),
    dst character varying(80),
    dcontext character varying(80),
    channel character varying(80),
    dstchannel character varying(80),
    lastapp character varying(80),
    lastdata character varying(80),
    duration integer DEFAULT 0 NOT NULL,
    billsec integer DEFAULT 0 NOT NULL,
    disposition character varying(45),
    amaflags integer DEFAULT 0 NOT NULL,
    accountcode character varying(20),
    uniqueid character varying(150),
    userfield character varying(255),
    recordingfile character varying
);


ALTER TABLE cdr OWNER TO postgres;

--
-- Name: cdr_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE cdr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE cdr_id_seq OWNER TO postgres;

--
-- Name: cdr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE cdr_id_seq OWNED BY cdr.id;


--
-- Name: extensions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE extensions (
    ext_n character varying NOT NULL,
    ext_pw character varying
);


ALTER TABLE extensions OWNER TO postgres;

--
-- Name: leads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE leads (
    l_id bigint NOT NULL,
    l_shop_name character varying,
    l_shop_phone character varying,
    l_shop_eid character varying,
    l_client_phone character varying,
    l_note character varying,
    l_order character varying,
    l_when timestamp with time zone,
    l_lock_time timestamp with time zone,
    l_lock_by character varying,
    l_completed boolean DEFAULT false
);


ALTER TABLE leads OWNER TO postgres;

--
-- Name: leads_l_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE leads_l_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE leads_l_id_seq OWNER TO postgres;

--
-- Name: leads_l_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE leads_l_id_seq OWNED BY leads.l_id;


--
-- Name: levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE levels (
    l_id integer NOT NULL,
    l_name character varying,
    l_worktime character varying
);


ALTER TABLE levels OWNER TO postgres;

--
-- Name: levels_l_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE levels_l_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE levels_l_id_seq OWNER TO postgres;

--
-- Name: levels_l_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE levels_l_id_seq OWNED BY levels.l_id;


--
-- Name: operator_ext_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE operator_ext_history (
    op_id integer,
    op_eh_tmstmp timestamp without time zone,
    op_eh_old character varying,
    op_eh_new character varying
);


ALTER TABLE operator_ext_history OWNER TO postgres;

--
-- Name: operator_group_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE operator_group_history (
    op_id integer,
    op_gh_tmstmp timestamp without time zone,
    op_gh_old character varying,
    op_gh_new character varying
);


ALTER TABLE operator_group_history OWNER TO postgres;

--
-- Name: operators; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE operators (
    op_id integer NOT NULL,
    op_name character varying,
    op_group character varying,
    op_ext character varying,
    op_location character varying
);


ALTER TABLE operators OWNER TO postgres;

--
-- Name: operators_op_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE operators_op_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE operators_op_id_seq OWNER TO postgres;

--
-- Name: operators_op_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE operators_op_id_seq OWNED BY operators.op_id;


--
-- Name: scheduled_calls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE scheduled_calls (
    oc_id bigint NOT NULL,
    oc_shop_name character varying,
    oc_shop_phone character varying,
    oc_client_phone character varying,
    oc_after_call character varying,
    oc_order character varying,
    oc_when timestamp with time zone,
    oc_taken_by character varying
);


ALTER TABLE scheduled_calls OWNER TO postgres;

--
-- Name: scheduled_calls_oc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE scheduled_calls_oc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE scheduled_calls_oc_id_seq OWNER TO postgres;

--
-- Name: scheduled_calls_oc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE scheduled_calls_oc_id_seq OWNED BY scheduled_calls.oc_id;


--
-- Name: shop_ext; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE shop_ext (
    shop_id integer,
    shop_ext character varying,
    shop_ext_tmstmp timestamp without time zone
);


ALTER TABLE shop_ext OWNER TO postgres;

--
-- Name: shops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE shops (
    shop_id integer NOT NULL,
    shop_name character varying,
    shop_phone character varying,
    shop_manager character varying,
    shop_script character varying,
    shop_manager2 character varying,
    shop_queue2 character varying,
    shop_queue3 character varying,
    shop_active character varying,
    shop_level character varying,
    shop_eid character varying
);


ALTER TABLE shops OWNER TO postgres;

--
-- Name: shops_shop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE shops_shop_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE shops_shop_id_seq OWNER TO postgres;

--
-- Name: shops_shop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE shops_shop_id_seq OWNED BY shops.shop_id;


--
-- Name: sip_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE sip_users (
    su_id integer NOT NULL,
    su_host character varying,
    su_username character varying,
    su_secret character varying,
    su_myext character varying,
    su_phone character varying
);


ALTER TABLE sip_users OWNER TO postgres;

--
-- Name: sip_ext; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW sip_ext AS
 SELECT sip_users.su_myext AS myext,
    sip_users.su_phone AS phone
   FROM sip_users;


ALTER TABLE sip_ext OWNER TO postgres;

--
-- Name: sip_users_su_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE sip_users_su_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sip_users_su_id_seq OWNER TO postgres;

--
-- Name: sip_users_su_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE sip_users_su_id_seq OWNED BY sip_users.su_id;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE tags (
    tag_id integer NOT NULL,
    tag_name character varying,
    tag_hasdata boolean
);


ALTER TABLE tags OWNER TO postgres;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE tags_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tags_tag_id_seq OWNER TO postgres;

--
-- Name: tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE tags_tag_id_seq OWNED BY tags.tag_id;


--
-- Name: call_log cl_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_log ALTER COLUMN cl_id SET DEFAULT nextval('call_log_cl_id_seq'::regclass);


--
-- Name: call_status cs_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_status ALTER COLUMN cs_id SET DEFAULT nextval('call_status_cs_id_seq'::regclass);


--
-- Name: cdr id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cdr ALTER COLUMN id SET DEFAULT nextval('cdr_id_seq'::regclass);


--
-- Name: leads l_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY leads ALTER COLUMN l_id SET DEFAULT nextval('leads_l_id_seq'::regclass);


--
-- Name: levels l_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY levels ALTER COLUMN l_id SET DEFAULT nextval('levels_l_id_seq'::regclass);


--
-- Name: operators op_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY operators ALTER COLUMN op_id SET DEFAULT nextval('operators_op_id_seq'::regclass);


--
-- Name: scheduled_calls oc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY scheduled_calls ALTER COLUMN oc_id SET DEFAULT nextval('scheduled_calls_oc_id_seq'::regclass);


--
-- Name: shops shop_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY shops ALTER COLUMN shop_id SET DEFAULT nextval('shops_shop_id_seq'::regclass);


--
-- Name: sip_users su_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY sip_users ALTER COLUMN su_id SET DEFAULT nextval('sip_users_su_id_seq'::regclass);


--
-- Name: tags tag_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tags ALTER COLUMN tag_id SET DEFAULT nextval('tags_tag_id_seq'::regclass);


--
-- Name: call_log call_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_log
    ADD CONSTRAINT call_log_pkey PRIMARY KEY (cl_id);


--
-- Name: call_status call_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_status
    ADD CONSTRAINT call_status_pkey PRIMARY KEY (cs_id);


--
-- Name: cdr cdr_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cdr
    ADD CONSTRAINT cdr_pkey PRIMARY KEY (id);


--
-- Name: extensions extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY extensions
    ADD CONSTRAINT extensions_pkey PRIMARY KEY (ext_n);


--
-- Name: levels levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY levels
    ADD CONSTRAINT levels_pkey PRIMARY KEY (l_id);


--
-- Name: operators operators_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY operators
    ADD CONSTRAINT operators_pkey PRIMARY KEY (op_id);


--
-- Name: shops shops_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY shops
    ADD CONSTRAINT shops_pkey PRIMARY KEY (shop_id);


--
-- Name: sip_users sip_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY sip_users
    ADD CONSTRAINT sip_users_pkey PRIMARY KEY (su_id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (tag_id);


--
-- Name: tags tags_tag_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tags
    ADD CONSTRAINT tags_tag_name_key UNIQUE (tag_name);


--
-- Name: billsec; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX billsec ON cdr USING btree (billsec);


--
-- Name: calldate; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX calldate ON cdr USING btree (calldate);


--
-- Name: dst; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dst ON cdr USING btree (dst);


--
-- Name: operators_op_ext_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX operators_op_ext_idx ON operators USING btree (op_ext);


--
-- Name: shops_shop_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX shops_shop_name_idx ON shops USING btree (shop_name);


--
-- Name: src; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX src ON cdr USING btree (src);


--
-- Name: call_log call_log_cl_operator_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_log
    ADD CONSTRAINT call_log_cl_operator_fkey FOREIGN KEY (cl_operator) REFERENCES operators(op_id);


--
-- Name: call_log call_log_cl_tag_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_log
    ADD CONSTRAINT call_log_cl_tag_fkey FOREIGN KEY (cl_tag) REFERENCES tags(tag_id);


--
-- Name: call_status call_status_cs_op_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_status
    ADD CONSTRAINT call_status_cs_op_fkey FOREIGN KEY (cs_op) REFERENCES operators(op_id);


--
-- Name: call_status call_status_cs_tag_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY call_status
    ADD CONSTRAINT call_status_cs_tag_fkey FOREIGN KEY (cs_tag) REFERENCES tags(tag_id);


--
-- Name: leads leads_l_lock_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY leads
    ADD CONSTRAINT leads_l_lock_by_fkey FOREIGN KEY (l_lock_by) REFERENCES operators(op_ext);


--
-- Name: operator_ext_history operator_ext_history_op_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY operator_ext_history
    ADD CONSTRAINT operator_ext_history_op_id_fkey FOREIGN KEY (op_id) REFERENCES operators(op_id);


--
-- Name: operator_group_history operator_group_history_op_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY operator_group_history
    ADD CONSTRAINT operator_group_history_op_id_fkey FOREIGN KEY (op_id) REFERENCES operators(op_id);


--
-- Name: check_ext_pw(character varying, character varying); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION check_ext_pw(ext character varying, pw character varying) TO cc_data;


--
-- Name: call_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE call_log TO cc_data;


--
-- Name: call_log_cl_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE call_log_cl_id_seq TO cc_data;


--
-- Name: cdr; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE cdr TO cdr;
GRANT SELECT ON TABLE cdr TO cc_data;


--
-- Name: cdr_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE cdr_id_seq TO cdr;


--
-- Name: extensions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE extensions TO cc_populate;
GRANT SELECT ON TABLE extensions TO cc_data;


--
-- Name: leads; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE leads TO cc_data;


--
-- Name: levels; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE levels TO cc_populate;


--
-- Name: levels_l_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE levels_l_id_seq TO cc_populate;


--
-- Name: operator_ext_history; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE operator_ext_history TO cc_populate;


--
-- Name: operator_group_history; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE operator_group_history TO cc_populate;


--
-- Name: operators; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE operators TO cc_populate;
GRANT SELECT,DELETE ON TABLE operators TO cc_data;


--
-- Name: operators_op_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE operators_op_id_seq TO cc_populate;


--
-- Name: shops; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE shops TO cc_populate;
GRANT SELECT ON TABLE shops TO cc_data;


--
-- Name: shops_shop_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE shops_shop_id_seq TO cc_populate;


--
-- Name: sip_users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT ON TABLE sip_users TO cc_populate;


--
-- Name: sip_ext; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE sip_ext TO cc_data;


--
-- Name: sip_users_su_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE sip_users_su_id_seq TO cc_populate;


--
-- Name: tags; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE tags TO cc_data;


--
-- PostgreSQL database dump complete
--


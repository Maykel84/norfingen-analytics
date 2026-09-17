"""Database connection handling for the Supabase Postgres instance."""

import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def _get_connection_params() -> dict:
    """Resolve connection params from st.secrets first, then environment variables."""
    try:
        db = st.secrets["db"]
        return {
            "host": db["host"],
            "port": db["port"],
            "dbname": db["dbname"],
            "user": db["user"],
            "password": db["password"],
        }
    except Exception:
        pass

    return {
        "host": os.environ["DB_HOST"],
        "port": os.environ.get("DB_PORT", "5432"),
        "dbname": os.environ.get("DB_NAME", "postgres"),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }


@st.cache_resource
def get_engine() -> Engine:
    params = _get_connection_params()
    url = (
        f"postgresql+psycopg2://{params['user']}:{params['password']}"
        f"@{params['host']}:{params['port']}/{params['dbname']}"
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)


REFRESH_TTL_SECONDS = 8 * 60 * 60  # ~3 refreshes per day


@st.cache_data(ttl=REFRESH_TTL_SECONDS)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def run_query_uncached(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Bypass the cache — used for schema introspection tooling only."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


@st.cache_data(ttl=REFRESH_TTL_SECONDS)
def get_last_refresh_time():
    """Shares the same cache TTL as run_query, so it reflects the last actual refresh."""
    import datetime

    return datetime.datetime.now()

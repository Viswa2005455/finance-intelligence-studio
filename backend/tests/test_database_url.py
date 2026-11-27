import pytest

from app.config import Settings

GOOD = "postgresql+psycopg://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require"


@pytest.mark.parametrize("pasted", [
    "postgresql://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require",
    "postgres://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require",
    "  postgresql://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require\n",
    "'postgresql://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require'",
    '"postgresql://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require"',
    "DATABASE_URL=postgresql://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require",
    "psql 'postgresql://user:pw@ep-x.aws.neon.tech/db?sslmode=require&channel_binding=require'",
])
def test_pasted_postgres_urls_are_cleaned(pasted):
    assert Settings(database_url=pasted).database_url == GOOD


def test_sqlite_is_left_alone():
    assert Settings(database_url="sqlite:///storage/x.db").database_url == "sqlite:///storage/x.db"

from sqlalchemy import create_engine


def get_engine(db_url: str, *, echo: bool = False):
    return create_engine(db_url, future=True, pool_pre_ping=True, echo=echo)

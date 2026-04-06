from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def getDbEngine(
  host: str,
  database: str,
  username: str,
  password: str,
  port: int = 6543,
  sslmode: str = "require",
) -> Engine:
  connStr = (
    f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"
    f"?sslmode={sslmode}"
  )
  return create_engine(connStr)

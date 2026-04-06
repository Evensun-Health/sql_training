from pathlib import Path
import re

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


_TEMPLATE_VAR_PATTERN = re.compile(r"\{\{_([A-Za-z0-9_]+)_\}\}")
_SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def loadSqlFromFile(fp: str | Path) -> str:
  return Path(fp).read_text(encoding="utf-8")


def renderSqlTemplate(sqlText: str, templateVars: dict[str, str] | None = None) -> str:
  if not templateVars:
    return sqlText

  def replace_match(match: re.Match[str]) -> str:
    varName = match.group(1)

    if varName not in templateVars:
      raise KeyError(f"Missing template var: {varName}")

    value = str(templateVars[varName])
    if not _SAFE_IDENTIFIER_PATTERN.fullmatch(value):
      raise ValueError(
        f"Unsafe identifier for template var '{varName}': {value}"
      )
    return value

  return _TEMPLATE_VAR_PATTERN.sub(replace_match, sqlText)


def runSqlToDf(engine: Engine, sqlText: str, params: dict | None = None) -> pd.DataFrame:
  with engine.connect() as conn:
    df = pd.read_sql_query(text(sqlText), conn, params=params)
  return df

# %%
# setup

import pandas as pd
import matplotlib.pyplot as plt


from config import CONNECTION_PASSWORD, DB_HOST, DB_NAME, DB_PORT, DB_USER
from connection import getDbEngine, loadSqlFromFile, renderSqlTemplate, runSqlToDf


# %%
# set connection vars
engine = getDbEngine(
  host=DB_HOST,
  database=DB_NAME,
  username=DB_USER,
  password=CONNECTION_PASSWORD,
  port=DB_PORT,
)


# %%
# load and render sql template
sqlPath = "./sql_templates/t0A_filtered"

templateVars = {
  "schema_name": "public",
  "table_name": "t0A",
}

queryParams = {
  "market_coverage": "Individual",
}

sqlTemplate = loadSqlFromFile(sqlPath)
sqlFinal = renderSqlTemplate(sqlTemplate, templateVars=templateVars)

print(sqlFinal)


# %%
# run query
df = runSqlToDf(engine, sqlFinal, params=queryParams)

df

# %%

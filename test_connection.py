# %%
# setup
from config import CONNECTION_PASSWORD, DB_HOST, DB_NAME, DB_PORT, DB_USER
from connection import getDbEngine, loadSqlFromFile, renderSqlTemplate, runSqlToDf


# %%
# set connection vars
host = DB_HOST
port = DB_PORT
database = DB_NAME
username = DB_USER
password = CONNECTION_PASSWORD

engine = getDbEngine(
  host=host,
  database=database,
  username=username,
  password=password,
  port=port,
)


# %%
# load and render sql template
sqlPath = "./sql_templates/exampleTemplate"

templateVars = {
  "schema_name": "public",
  "table_name": "t0A",
}

sqlTemplate = loadSqlFromFile(sqlPath)
sqlFinal = renderSqlTemplate(sqlTemplate, templateVars=templateVars)

print(sqlFinal)


# %%
# run query
df = runSqlToDf(engine, sqlFinal)

df

# %%

# %%
# setup

import pandas as pd

from config import CONNECTION_PASSWORD, DB_HOST, DB_NAME, DB_PORT, DB_USER
from connection import getDbEngine, loadSqlFromFile, renderSqlTemplate, runSqlToDf


# %%
# load data
engine = getDbEngine(
  host=DB_HOST,
  database=DB_NAME,
  username=DB_USER,
  password=CONNECTION_PASSWORD,
  port=DB_PORT,
)

sqlTemplate = loadSqlFromFile("./sql_templates/t0A_filtered")
sqlFinal = renderSqlTemplate(sqlTemplate, templateVars={"schema_name": "public", "table_name": "t0A"})

df = runSqlToDf(engine, sqlFinal, params={"market_coverage": "Individual"})


# %%
# 1. Sample rows
df.head(20)


# %%
# 2. Schema + dtypes
df.info()


# %%
# 3. Row count
len(df)


# %%
# 4. Distinct values in key columns
df[["business_year", "state_code", "issuer_id", "plan_id", "rating_area_id", "metal_level", "age"]].nunique()


# %%
# 5. Spot-check individual columns
df["business_year"].unique()

# %%
print(df["state_code"].unique())

print(df["metal_level"].value_counts())

# %%

metalList = df["metal_level"].unique()
print(metalList)

# %%
df["age"].unique()

# %%
df["tobacco"].value_counts()

# %%
df["csr_variation_type"].value_counts()


# %%
# values in one big loop

for c in df.columns:
    print(f"Column: {c}")
    print(df[c].value_counts())
    print("\n\n")

# %%
df['individual_rate'].value_counts()

# %%
df.columns
# %%
# 6. Guess the grain — example try

df.groupby(["business_year", "plan_id", "age", "tobacco"]).size().reset_index(name="row_count").sort_values("row_count", ascending=False).head(20)

# len(df)

# %%
cols_of_interest = ['business_year', 'state_code', 'issuer_id', 'plan_id', 'rating_area_id', 'age', 'individual_rate','market_coverage']

# %%
# 6. Guess the grain — refinement (adding rating_area_id)
(
  df
  .groupby(["business_year", "plan_id", "rating_area_id", "age", "tobacco"])
  .size()
  .reset_index(name="row_count")
  .sort_values("row_count", ascending=False)
  .head(20)
)

# %%

# %%
smaller_df = df[cols_of_interest]
smaller_df
# %%
smaller_df = smaller_df[smaller_df["issuer_id"] != '69461']
# %%
len(smaller_df)
# %%

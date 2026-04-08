# %%
# setup

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})

from sqlalchemy import text

from config import CONNECTION_PASSWORD, DB_HOST, DB_NAME, DB_PORT, DB_USER
from connection import getDbEngine, loadSqlFromFile, renderSqlTemplate


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


# breaks the extendablility
issuer_names = {
  "69461": "United",
  "46944": "bcbs of AL",
  "53932": "Centene",
}

with engine.connect() as conn:
  df = pd.read_sql_query(
    text(sqlFinal),
    conn,
    params={"market_coverage": "Individual"},
    dtype={"issuer_id": str},
  )

df["issuer_name"] = df["issuer_id"].map(issuer_names)

df.head(20)


# %%
# 1. Min individual rate within rating area + metal level
# Equivalent to: =MINIFS([individual_rate],[rating_area_id],[@rating_area_id],[metal_level],[@metal_level])
df["min_rate_area_metal"] = (
  df.groupby(["rating_area_id", "metal_level"])["individual_rate"]
  .transform("min")
)

df[["rating_area_id", "metal_level", "individual_rate", "min_rate_area_metal"]].head(20)


# %%
# 1a. Add is_min flag
# rank() method='min' matches SQL RANK() — ties get the same rank
df["rank_area_metal"] = (
  df.groupby(["rating_area_id", "metal_level"])["individual_rate"]
  .rank(method="min", ascending=True)
)

df["is_min"] = (df["rank_area_metal"] == 1).astype(int)

df[["rating_area_id", "metal_level", "individual_rate", "min_rate_area_metal", "is_min"]].head(20)


# %%
# 1b. Add is_slcsp: Second Lowest Cost Silver Plan
# SLCSP = rank 2 within Silver plans for a rating area (ACA benchmark rate)
df["is_slcsp"] = (
  (df["rank_area_metal"] == 2) & (df["metal_level"] == "Silver")
).astype(int)

df[["rating_area_id", "metal_level", "individual_rate", "is_min", "is_slcsp"]].head(20)

# %%

# %%
# 2. Pivot: min individual rate by rating area × metal level
pivot_min_rate = df.pivot_table(
  index="rating_area_id",
  columns="metal_level",
  values="individual_rate",
  aggfunc="min",
)

pivot_min_rate


# %%
# heat map of pivot_min_rate

metal_order = ["Catastrophic", "Bronze", "Silver", "Gold"]

pivot_sorted = (
  pivot_min_rate
  .reindex(columns=metal_order)
  .reindex(sorted(pivot_min_rate.index, key=lambda x: int(x.split(" ")[-1])))
)

fig, ax = plt.subplots(figsize=(7, 8))

im = ax.imshow(pivot_sorted.values, aspect="auto", cmap="copper_r", alpha=1)

ax.set_xticks(range(len(pivot_sorted.columns)))
ax.set_xticklabels(pivot_sorted.columns)
ax.set_yticks(range(len(pivot_sorted.index)))
ax.set_yticklabels(pivot_sorted.index)

for r in range(pivot_sorted.shape[0]):
  for c in range(pivot_sorted.shape[1]):
    val = pivot_sorted.iloc[r, c]
    if pd.notna(val):
      ax.text(c, r, f"${val:,.0f}", ha="center", va="center", fontsize=7)

plt.colorbar(im, ax=ax, label="Min Individual Rate")
ax.set_title("Min Individual Rate by Rating Area × Metal Level")
plt.tight_layout()
plt.show()


# %%
# 3. Pivot: count of issuer appearances at the minimum rate by issuer × metal level
pivot_issuer_min = (
  df[df["is_min"] == 1]
  .pivot_table(
    index="issuer_name",
    columns="metal_level",
    values="individual_rate",
    aggfunc="count",
    fill_value=0,
  )
)

pivot_issuer_min

# %%

issuers_sorted = sorted(pivot_issuer_min.index)
cmap = plt.get_cmap("tab10")
issuer_color = {issuer: cmap(i / 10) for i, issuer in enumerate(issuers_sorted)}


# %%
# small multiples: one subplot per issuer — competitive profile across metal levels

metals = ["Catastrophic", "Bronze", "Silver", "Gold"]
issuers_sorted = sorted(pivot_issuer_min.index)

fig, axes = plt.subplots(1, len(issuers_sorted), figsize=(4 * len(issuers_sorted), 4), sharey=True)

for ax, issuer in zip(axes, issuers_sorted):
  counts = [pivot_issuer_min.loc[issuer, m] for m in metals]
  ax.bar(metals, counts, color=issuer_color[issuer])
  ax.set_title(issuer)
  ax.set_xlabel("Metal Level")
  ax.tick_params(axis="x", rotation=30)

axes[0].set_ylabel("Count at Min Rate")
fig.suptitle("Appearances at Min Rate by Metal Level — per Issuer")
plt.tight_layout()
plt.show()


# %%
# small multiples: one subplot per metal level — issuer comparison within each tier

fig, axes = plt.subplots(1, len(metals), figsize=(3 * len(metals), 4), sharey=True)

for ax, metal in zip(axes, metals):
  counts = [pivot_issuer_min.loc[issuer, metal] for issuer in issuers_sorted]
  colors = [issuer_color[issuer] for issuer in issuers_sorted]
  ax.bar(issuers_sorted, counts, color=colors)
  ax.set_title(metal)
  ax.set_xlabel("Issuer")
  ax.tick_params(axis="x", rotation=30)

axes[0].set_ylabel("Count at Min Rate")
fig.suptitle("Appearances at Min Rate by Issuer — per Metal Level")
plt.tight_layout()
plt.show()


# %%
# 3a. Same with a grand total column
pivot_issuer_min["grand_total"] = pivot_issuer_min.sum(axis=1)

pivot_issuer_min.sort_index()

# %%
# distribution plot: individual_rate by metal level, colored by issuer, one plot per rating area

metal_order = ["Catastrophic", "Bronze", "Silver", "Gold"] # no platinum, "Platinum"]
metal_x = {m: i for i, m in enumerate(metal_order)}

rating_areas = sorted(df["rating_area_id"].unique(), key=lambda x: int(x.split(" ")[-1]))

for area in rating_areas:
  # if area != "Rating Area 10":
  #   continue 
  area_df = df[df["rating_area_id"] == area]

  fig, ax = plt.subplots(figsize=(9, 5))

  for issuer, group in area_df.groupby("issuer_name"):
    x_vals = group["metal_level"].map(metal_x)
    jitter = (pd.Series(range(len(group))) % 5 - 2) * 0.01  # small horizontal spread
    ax.scatter(
      x_vals + jitter.values,
      group["individual_rate"],
      color=issuer_color[issuer],
      label=issuer,
      alpha=0.75,
      s=25,
    )

  ax.set_xticks(range(len(metal_order)))
  ax.set_xticklabels(metal_order)
  ax.set_xlabel("Metal Level")
  ax.set_ylabel("Individual Rate")
  ax.set_title(f"Rate Distribution — {area}")
  ax.legend(title="Issuer", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=7)

  plt.tight_layout()
  plt.show()
# %%

import pandas as pd
import csv
import gc
from collections import defaultdict

VAHAN_FILE = "../Data/Raw/vahan_2020_2025.csv"
RTO_MASTER_FILE = "../Data/Reference/indian_rto_master.csv"
OUTPUT_FILE = "../Data/Processed/city_ev_top1000.csv"

CHUNK_SIZE = 3_000_000

USECOLS = [
    "rtoCode",
    "fuelName",
    "vehicleClassName",
    "vehicleCount"
]

rto_master = pd.read_csv(RTO_MASTER_FILE)

rto_master.columns = (
    rto_master.columns
    .str.lower()
    .str.strip()
)

def find_col(keyword):
    for col in rto_master.columns:
        if keyword in col:
            return col
    raise RuntimeError(f"Column containing '{keyword}' not found")

RTO_CODE_COL = find_col("rto")
LOCATION_COL = find_col("location")

STATE_COL = None
for col in rto_master.columns:
    if "state" in col:
        STATE_COL = col
        break

import re

DIRECTION_WORDS = [
    "NORTH", "SOUTH", "EAST", "WEST",
    "CENTRAL", "RURAL", "URBAN",
    "CITY", "DISTRICT"
]

CITY_REPLACEMENTS = {
    "BENGALURU": "BANGALORE",
    "BENGALORE": "BANGALORE",
    "DELHI NEW": "DELHI",
    "NEW DELHI": "DELHI",
    "CALCUTTA": "KOLKATA",
    "BOMBAY": "MUMBAI",
    "POONA": "PUNE",
    "MYSORE": "MYSURU"
}

def clean_city_name(name):

    if not isinstance(name, str):
        return None

    s = name.upper()
    s = re.sub(r"\(.*?\)", "", s)
    for k, v in CITY_REPLACEMENTS.items():
        s = s.replace(k, v)

    for word in DIRECTION_WORDS:
        s = re.sub(rf"\b{word}\b", "", s)

    s = re.sub(r"[^A-Z ]", " ", s)

    s = re.sub(r"\s+", " ", s).strip()

    if not s:
        return None

    return s.title()

rto_master["city"] = (
    rto_master[LOCATION_COL]
    .astype(str)
    .str.split(",")
    .str[-1]
    .apply(clean_city_name)
)

rto_master[RTO_CODE_COL] = (
    rto_master[RTO_CODE_COL]
    .astype(str)
    .str.upper()
    .str.strip()
)

rto_master_unique = (
    rto_master
    .dropna(subset=["city"])
    .drop_duplicates(subset=RTO_CODE_COL)
)

if STATE_COL:
    rto_to_city = (
        rto_master_unique
        .set_index(RTO_CODE_COL)[["city", STATE_COL]]
        .to_dict("index")
    )
else:
    rto_to_city = (
        rto_master_unique
        .set_index(RTO_CODE_COL)[["city"]]
        .to_dict("index")
    )

print("✅ Unique RTO codes:", len(rto_to_city))

city_totals = defaultdict(int)

gc.disable()

for chunk in pd.read_csv(
    VAHAN_FILE,
    chunksize=CHUNK_SIZE,
    usecols=USECOLS,
    engine="python",
    quoting=csv.QUOTE_NONE,
    on_bad_lines="skip",
    encoding="utf-8",
    encoding_errors="ignore",
):

    chunk.columns = chunk.columns.str.strip()

    chunk["rtoCode"] = (
        chunk["rtoCode"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    chunk = chunk[chunk["rtoCode"].isin(rto_to_city)]

    if chunk.empty:
        continue

    ev_mask = chunk["fuelName"].isin(
        ["ELECTRIC(BOV)", "PURE EV"]
    )
    tw_mask = chunk["vehicleClassName"].isin(
        ["M-Cycle/Scooter", "Moped"]
    )

    df = chunk[ev_mask & tw_mask]

    if df.empty:
        continue

    df["vehicleCount"] = (
        pd.to_numeric(df["vehicleCount"], errors="coerce")
        .fillna(1)
    )
    grp = (
        df.groupby("rtoCode")["vehicleCount"]
        .sum()
        .reset_index()
    )
    for _, row in grp.iterrows():
        rto = row["rtoCode"]
        count = int(row["vehicleCount"])

        city = rto_to_city[rto]["city"]

        state = (
            rto_to_city[rto][STATE_COL]
            if STATE_COL else "Unknown"
        )

        key = (city, str(state).title())
        city_totals[key] += count

gc.enable()

city_df = pd.DataFrame(
    [
        {
            "city": k[0],
            "state": k[1],
            "total_e2w_ev": v
        }
        for k, v in city_totals.items()
    ]
)

top_1000 = (
    city_df
    .sort_values("total_e2w_ev", ascending=False)
    .head(1000)
    .reset_index(drop=True)
)

top_1000.to_csv(OUTPUT_FILE, index=False)

print("Cities:", len(top_1000))

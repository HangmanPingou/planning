import pandas as pd
from datetime import datetime, timedelta, date

df = pd.read_parquet("planning.parquet")

df["nb_heures_pause"] = pd.Series(0, index=df.index, dtype="int64")
df["nb_minutes_pause"] = pd.Series(0, index=df.index, dtype="int64")

df.to_parquet("planning.parquet")
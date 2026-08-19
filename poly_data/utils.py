import json
import pandas as pd 
import os
from dotenv import load_dotenv 


# poly_data/utils.py
import os, json, pandas as pd

def get_sheet_df():
    """
    JSON-basierter Ersatz für die bisherige Sheets-Funktion.
    Erwartet CONFIG_JSON Pfad (ENV) oder ./config.json.
    Rückgabe: (df, params) wie zuvor.
    """
    path = os.getenv("CONFIG_JSON", "config.json")
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    markets = cfg.get("markets", [])
    df = pd.DataFrame(markets)

    # minimale Schema-Sanity
    for col in ("token1", "token2"):
        if col in df.columns:
            df[col] = df[col].astype(str)

    # nur aktive Märkte nehmen, falls Flag vorhanden
    if "active" in df.columns:
        df = df[df["active"].fillna(True)]

    params = cfg.get("hyperparameters", {})
    return df.reset_index(drop=True), params
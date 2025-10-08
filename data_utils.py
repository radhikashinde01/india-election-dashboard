import pandas as pd
import numpy as np

def load_and_clean_india(filepath):
    df = pd.read_csv(filepath)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Detect columns intelligently
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    object_cols = df.select_dtypes(include=object).columns.tolist()

    col_detected = {
        "State": object_cols[0] if len(object_cols) >= 1 else None,
        "Constituency": object_cols[1] if len(object_cols) >= 2 else None,
        "Candidate": object_cols[2] if len(object_cols) >= 3 else None,
        "Party": object_cols[3] if len(object_cols) >= 4 else None,
        "Votes": numeric_cols[0] if len(numeric_cols) >= 1 else None,
        "Total_Votes": numeric_cols[1] if len(numeric_cols) >= 2 else None,
        "Year": numeric_cols[2] if len(numeric_cols) >= 3 else None,
        "Gender": object_cols[4] if len(object_cols) >= 5 else None
    }

    # Rename detected columns
    for key, val in col_detected.items():
        if val:
            df = df.rename(columns={val: key})

    # Convert numeric columns
    if "Votes" in df.columns and "Total_Votes" in df.columns:
        df["Votes"] = pd.to_numeric(df["Votes"], errors='coerce').fillna(0).astype(int)
        df["Total_Votes"] = pd.to_numeric(df["Total_Votes"], errors='coerce').fillna(0).astype(int)
        df["Vote_Share"] = df["Votes"] / df["Total_Votes"] * 100

    # Rank & winner
    if all(col in df.columns for col in ["Votes", "Constituency", "Year"]):
        df["Rank"] = df.groupby(["Year", "Constituency"])["Votes"].rank(ascending=False, method="first")
        df["Winner"] = (df["Rank"] == 1).astype(int)

        second = df[df["Rank"] == 2][["Year", "Constituency", "Votes"]].rename(columns={"Votes": "Second_Votes"})
        df = pd.merge(df, second, on=["Year", "Constituency"], how="left")
        df["Winning_Margin"] = df.apply(lambda r: r["Votes"] - r["Second_Votes"] if r["Winner"] == 1 else None, axis=1)

    return df

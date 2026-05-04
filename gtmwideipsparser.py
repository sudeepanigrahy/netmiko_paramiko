import pandas as pd
import ast
 
# ── CONFIG ──────────────────────────────────────────────────────────────────
SHEET1_PATH = "sheet1.csv"   # APPCODE | FQDN
SHEET2_PATH = "sheet2.csv"   # APPCODE | APPNAME | APPCODE CUSTODIAN | EMAILS
OUTPUT_PATH = "output.csv"
# ────────────────────────────────────────────────────────────────────────────
 
def parse_fqdn_list(raw):
    """Parse the FQDN cell value like [fqdn1, fqdn2, fqdn3] into a Python list."""
    raw = str(raw).strip()
    try:
        # Try ast.literal_eval first (works if values are quoted strings)
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return [str(f).strip() for f in parsed]
    except Exception:
        pass
    # Fallback: strip brackets and split by comma
    raw = raw.lstrip("[").rstrip("]")
    return [f.strip() for f in raw.split(",") if f.strip()]
 
 
def main():
    # Load sheets
    df1 = pd.read_csv(SHEET1_PATH)
    df2 = pd.read_csv(SHEET2_PATH)
 
    # Normalize column names (strip whitespace)
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()
 
    # Build output rows
    rows = []
 
    for _, row in df1.iterrows():
        appcode = str(row["APPCODE"]).strip()
        fqdns = parse_fqdn_list(row["FQDN"])
 
        # Look up matching row in Sheet2
        match = df2[df2["APPCODE"].astype(str).str.strip() == appcode]
 
        if not match.empty:
            appname    = match.iloc[0]["APPNAME"]
            custodian  = match.iloc[0]["APPCODE CUSTODIAN"]
            emails     = match.iloc[0]["EMAILS"]
        else:
            appname = custodian = emails = ""
 
        for i, fqdn in enumerate(fqdns):
            rows.append({
                "APPCODE"           : appcode,
                "FQDN"              : fqdn,
                "APPNAME"           : appname    if i == 0 else "",
                "APPCODE CUSTODIAN" : custodian  if i == 0 else "",
                "EMAILS"            : emails     if i == 0 else "",
            })
 
    # Write output
    output_df = pd.DataFrame(rows, columns=[
        "APPCODE", "FQDN", "APPNAME", "APPCODE CUSTODIAN", "EMAILS"
    ])
    output_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Done! {len(output_df)} rows written to '{OUTPUT_PATH}'")
    print(f"APPCODEs processed: {df1['APPCODE'].nunique()}")
 
 
if __name__ == "__main__":
    main()

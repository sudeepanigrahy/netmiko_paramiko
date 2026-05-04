import pandas as pd
import ast
 
# ── CONFIG ──────────────────────────────────────────────────────────────────
SHEET1_PATH = "sheet1.csv"
SHEET2_PATH = "sheet2.csv"
OUTPUT_PATH = "output.csv"
# ────────────────────────────────────────────────────────────────────────────
 
def parse_fqdn_list(raw):
    """Parse the FQDN cell value like [fqdn1, fqdn2, fqdn3] into a Python list."""
    raw = str(raw).strip()
    try:
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
 
    # DEBUG: print exact column names so we can verify
    print("Sheet1 columns:", df1.columns.tolist())
    print("Sheet2 columns:", df2.columns.tolist())
 
    # Auto-detect the email column (contains 'email' case-insensitive)
    email_col = next((c for c in df2.columns if "email" in c.lower()), None)
    appname_col = next((c for c in df2.columns if "name" in c.lower()), None)
    custodian_col = next((c for c in df2.columns if "custodian" in c.lower()), None)
    appcode_col = next((c for c in df2.columns if "code" in c.lower()), None)
 
    print(f"\nAuto-detected Sheet2 columns:")
    print(f"  App Code col      : {appcode_col}")
    print(f"  App Name col      : {appname_col}")
    print(f"  Custodian col     : {custodian_col}")
    print(f"  Email col         : {email_col}\n")
 
    # Build output rows
    rows = []
 
    for _, row in df1.iterrows():
        appcode = str(row["APPCODE"]).strip()
        fqdns = parse_fqdn_list(row["FQDN"])
 
        # Look up matching row in Sheet2 (case-insensitive)
        match = df2[df2[appcode_col].astype(str).str.strip().str.lower() == appcode.lower()]
 
        if not match.empty:
            appname   = match.iloc[0][appname_col]    if appname_col    else ""
            custodian = match.iloc[0][custodian_col]  if custodian_col  else ""
            emails    = match.iloc[0][email_col]      if email_col      else ""
        else:
            appname = custodian = emails = ""
 
        for i, fqdn in enumerate(fqdns):
            rows.append({
                "APPCODE"           : appcode,
                "FQDN"              : fqdn,
                "App Name"          : appname    if i == 0 else "",
                "AppCode Custodian" : custodian  if i == 0 else "",
                "Emails"            : emails     if i == 0 else "",
            })
 
    # Write output
    output_df = pd.DataFrame(rows, columns=[
        "APPCODE", "FQDN", "App Name", "AppCode Custodian", "Emails"
    ])
    output_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Done! {len(output_df)} rows written to '{OUTPUT_PATH}'")
    print(f"APPCODEs processed: {df1['APPCODE'].nunique()}")
 
 
if __name__ == "__main__":
    main()

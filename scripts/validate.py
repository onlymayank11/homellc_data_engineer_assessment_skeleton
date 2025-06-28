import pandas as pd
import logging
from pathlib import Path

# 🧾 Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 📁 Define paths
base_dir = Path(__file__).resolve().parent
raw_csv_path = base_dir.parent / "sql" / "fake_data.csv"
normalized_dir = base_dir.parent / "normalized_csvs"
report_path = base_dir.parent / "mismatch_report.xlsx"

# 📊 Load raw data
try:
    raw_df = pd.read_csv(raw_csv_path)
    logging.info(f"🔄 Loaded raw data with {len(raw_df)} rows.")
except FileNotFoundError:
    logging.error(f"❌ Raw data file not found at {raw_csv_path}")
    exit(1)

# 📦 Table-wise columns
def filter_columns(possible_cols):
    return [col for col in possible_cols if col in raw_df.columns]

table_columns = {
    "property": filter_columns([
        "Flood", "Highway", "Train", "HTW", "Pool", "Commercial",
        "Water", "Sewage", "BasementYesNo", "Rent_Restricted"
    ] + [col for col in raw_df.columns if col.startswith("Property")]),
    "leads": filter_columns([col for col in raw_df.columns if "Lead" in col]),
    "valuation": filter_columns([
        "Expected_Rent", "ARV", "ValuationDate", "RentPerSqft"
    ] + [col for col in raw_df.columns if "Valuation" in col]),
    "rehab": filter_columns([
        "Paint", "Flooring_Flag", "Foundation_Flag", "Roof_Flag", "HVAC_Flag",
        "Kitchen_Flag", "Bathroom_Flag", "Appliances_Flag", "Windows_Flag",
        "Landscaping_Flag", "Trashout_Flag", "HOA_Flag"
    ]),
    "hoa": filter_columns(["HOA_Flag"]),
    "taxes": filter_columns(["Tax_Rate"]),
}

# 🧹 Normalization helper
def normalize_series(series: pd.Series):
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({
            "true": "1", "false": "0",
            "yes": "1", "no": "0",
            "minimal flood": "1", "flood zone": "0",
            "near": "1", "far": "0",
            "city": "1", "well": "0",
            "septic": "0",
        })
    )

# ✅ Start validation
mismatches_found = False
mismatch_summary = []

for table_name, columns in table_columns.items():
    file_path = normalized_dir / f"{table_name}.csv"

    if not file_path.exists():
        logging.error(f"❌ Missing file: {file_path.name}")
        continue

    try:
        norm_df = pd.read_csv(file_path)
        logging.info(f"✅ Validated {file_path.name} with {norm_df.shape[1]} columns.")

        for col in columns:
            if col not in norm_df.columns:
                logging.warning(f"⚠️  Column '{col}' missing in normalized CSV '{file_path.name}'")
                continue

            raw_col = normalize_series(raw_df[col])
            norm_col = normalize_series(norm_df[col])

            mismatches = (raw_col != norm_col).sum()

            if mismatches > 0:
                mismatches_found = True
                logging.warning(f"⚠️  Column mismatch in {table_name} -> {col}")
                logging.warning(f"    → Mismatched values: {mismatches}")

                mismatch_rows = raw_col != norm_col
                mismatch_df = pd.DataFrame({
                    "raw": raw_col[mismatch_rows].head(5).values,
                    "normalized": norm_col[mismatch_rows].head(5).values
                })

                logging.warning(f"    → Top mismatches:\n{mismatch_df}")
                
                # Save to summary
                mismatch_summary.append({
                    "Table": table_name,
                    "Column": col,
                    "Total Mismatches": mismatches,
                    "Sample Mismatch Raw": "; ".join(mismatch_df['raw'].astype(str)),
                    "Sample Mismatch Normalized": "; ".join(mismatch_df['normalized'].astype(str))
                })

    except Exception as e:
        logging.error(f"❌ Error processing {file_path.name}: {e}")

# 🎯 Summary
if mismatches_found:
    logging.warning("🔍 Some mismatches were found. Review the log above.")
    
    summary_df = pd.DataFrame(mismatch_summary)
    summary_df.to_excel(report_path, index=False)
    logging.info(f"📝 Mismatch summary exported to: {report_path}")
else:
    logging.info("🎉 All normalized CSVs match expected raw values!")

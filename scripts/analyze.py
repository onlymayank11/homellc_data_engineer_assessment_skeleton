import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ---------------------
# Setup
# ---------------------
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "normalized_csvs"
output_dir = base_dir / "analysis_outputs"
output_dir.mkdir(parents=True, exist_ok=True)

tables = ["property", "leads", "valuation", "rehab", "hoa", "taxes"]
dfs = {}

# Load CSVs
for name in tables:
    path = data_dir / f"{name}.csv"
    if path.exists():
        dfs[name] = pd.read_csv(path)
    else:
        print(f"⚠️ {name}.csv not found.")
        dfs[name] = pd.DataFrame()

# ---------------------
# Summary Analysis
# ---------------------
summary = {}

# PROPERTY TABLE
df = dfs["property"]
summary["Total Properties"] = len(df)
if "Property_Type" in df:
    summary["Unique Property Types"] = df["Property_Type"].nunique()
    summary["Top Property Types"] = df["Property_Type"].value_counts().head(3).to_dict()
if "Pool" in df:
    summary["Pool - Yes Count"] = df["Pool"].astype(str).str.lower().eq("yes").sum()
if "Flood" in df:
    summary["Flood Zone - Count"] = df["Flood"].astype(str).str.lower().eq("flood zone").sum()

# LEADS TABLE
df = dfs["leads"]
if "Reviewed_Status" in df:
    summary["Reviewed_Status Breakdown"] = df["Reviewed_Status"].value_counts().to_dict()
if "Lead_Source" in df:
    summary["Top 5 Lead Sources"] = df["Lead_Source"].value_counts().head(5).to_dict()

# VALUATION TABLE
df = dfs["valuation"]
if "Expected_Rent" in df:
    summary.update({
        "Expected Rent - Mean": df["Expected_Rent"].mean(),
        "Expected Rent - Median": df["Expected_Rent"].median(),
        "Expected Rent - Max": df["Expected_Rent"].max(),
        "Expected Rent - Min": df["Expected_Rent"].min(),
        "Expected Rent - Std Dev": df["Expected_Rent"].std(),
        "Expected Rent - Total Sum": df["Expected_Rent"].sum()
    })

if "ARV" in df:
    summary["ARV - Average"] = df["ARV"].mean()

# Add Rent to ARV Ratio if both columns exist
if "Expected_Rent" in df and "ARV" in df:
    df["rent_to_arv_ratio"] = df["Expected_Rent"] / df["ARV"].replace({0: pd.NA})
    summary.update({
        "Rent to ARV Ratio - Mean": df["rent_to_arv_ratio"].mean(),
        "Rent to ARV Ratio - Median": df["rent_to_arv_ratio"].median(),
        "Rent to ARV Ratio - Max": df["rent_to_arv_ratio"].max(),
        "Rent to ARV Ratio - Min": df["rent_to_arv_ratio"].min()
    })
    dfs["valuation"] = df  # update back with new column

# HOA TABLE
df = dfs["hoa"]
if "HOA" in df:
    summary["Properties with HOA Info"] = df["HOA"].notna().sum()
    summary["HOA Breakdown"] = df["HOA"].value_counts().to_dict()

# REHAB TABLE
df = dfs["rehab"]
rehab_flags = df.select_dtypes(include="object").apply(lambda col: col.str.lower().eq("true").sum())
summary["Rehab Flags True Counts"] = rehab_flags.to_dict()

# TAXES TABLE
df = dfs["taxes"]
if "Taxes" in df:
    summary.update({
        "Taxes - Mean": df["Taxes"].mean(),
        "Taxes - Median": df["Taxes"].median(),
        "Taxes - Max": df["Taxes"].max(),
        "Taxes - Min": df["Taxes"].min(),
        "Taxes - Std Dev": df["Taxes"].std()
    })

# ---------------------
# Write Summary to Excel
# ---------------------
with pd.ExcelWriter(output_dir / "full_summary_report_detailed.xlsx") as writer:
    for name, df in dfs.items():
        df.to_excel(writer, sheet_name=name, index=False)

    flat_summary = []
    for k, v in summary.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                flat_summary.append((f"{k} - {subk}", subv))
        else:
            flat_summary.append((k, v))

    pd.DataFrame(flat_summary, columns=["Metric", "Value"]).to_excel(writer, sheet_name="Summary", index=False)

# ---------------------
# Visualizations
# ---------------------

# Expected Rent Histogram
if "Expected_Rent" in dfs["valuation"]:
    plt.figure(figsize=(8, 5))
    sns.histplot(dfs["valuation"]["Expected_Rent"], kde=True, bins=30, color="skyblue", edgecolor="black")
    plt.title("Expected Rent Distribution")
    plt.xlabel("Expected Rent")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_dir / "expected_rent_distribution.png")
    plt.close()

# Rehab Flags Barplot
if not rehab_flags.empty:
    plt.figure(figsize=(10, 6))
    rehab_flags.sort_values(ascending=False).plot(kind="bar", color="cornflowerblue")
    plt.title("Rehab Flags - True Value Counts")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "rehab_flags.png")
    plt.close()

# Correlation Heatmap for Valuation
if not dfs["valuation"].empty:
    plt.figure(figsize=(12, 10))
    corr = dfs["valuation"].corr(numeric_only=True)
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Valuation Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_dir / "valuation_correlation_heatmap.png")
    plt.close()

print("✅ Enhanced analysis complete. Check /analysis_outputs.")

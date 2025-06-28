"""
ETL Script for Home.LLC Data Engineering Assessment

This script performs the following:
- Reads a flat CSV containing property-related data
- Normalizes it into structured relational dataframes
- Loads the data into a MySQL database with normalized schema

Author: Mayank Mathur
"""

import pandas as pd
import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



from pathlib import Path
import os
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=env_path)
logging.info(f"✅ Loaded MYSQL_PORT from env: {os.getenv('MYSQL_PORT')}")






# ----------------------------------------------
# Function to normalize various boolean-like inputs
# ----------------------------------------------
def parse_boolean(value):
    """
    Convert a variety of truthy/falsy text representations to Python booleans.
    Accepts values like 'yes', 'true', '1', 'minimal flood', etc.
    Returns:
        bool or None: True/False or None if value is NaN
    """
    if pd.isna(value):
        return None
    value_str = str(value).strip().lower()
    return value_str in ['yes', 'true', '1', 'minimal flood', 'no flooding']

# ----------------------------------------------
# Load the input dataset
# ----------------------------------------------


csv_path = base_dir / "sql" / "fake_data.csv"
df = pd.read_csv(csv_path)

# df = pd.read_csv("/Users/mkmathur/Desktop/homellc_data_engineer_assessment_skeleton/sql/fake_data.csv")

# ----------------------------------------------
# Define column mappings per normalized table
# ----------------------------------------------

property_columns = [
    'Property_Title', 'Address', 'Market', 'Flood', 'Street_Address', 'City',
    'State', 'Zip', 'Property_Type', 'Highway', 'Train', 'Tax_Rate',
    'SQFT_Basement', 'HTW', 'Pool', 'Commercial', 'Water', 'Sewage',
    'Year_Built', 'SQFT_MU', 'SQFT_Total', 'Parking', 'Bed', 'Bath',
    'BasementYesNo', 'Layout', 'Rent_Restricted', 'Neighborhood_Rating',
    'Latitude', 'Longitude', 'Subdivision', 'School_Average'
]
leads_columns = [
    'Reviewed_Status', 'Most_Recent_Status', 'Source', 'Occupancy',
    'Net_Yield', 'IRR', 'Selling_Reason', 'Seller_Retained_Broker',
    'Final_Reviewer'
]
valuation_columns = [
    'Previous_Rent', 'List_Price', 'Zestimate', 'ARV', 'Expected_Rent',
    'Rent_Zestimate', 'Low_FMR', 'High_FMR', 'Redfin_Value'
]
rehab_columns = [
    'Underwriting_Rehab', 'Rehab_Calculation', 'Paint', 'Flooring_Flag', 'Foundation_Flag',
    'Roof_Flag', 'HVAC_Flag', 'Kitchen_Flag', 'Bathroom_Flag', 'Appliances_Flag',
    'Windows_Flag', 'Landscaping_Flag', 'Trashout_Flag'
]
hoa_columns = ['HOA', 'HOA_Flag']
taxes_columns = ['Taxes']


# ----------------------------------------------
# Extract & Transform: Property Table
# ----------------------------------------------

# ----------------------------------------------
# Extract & Transform: Property Table
# ----------------------------------------------

df_property = df[property_columns].copy()

# Custom normalization mappings
custom_mappings = {
    "Flood": {"minimal flood": 1, "flood zone": 0},
    "Highway": {"near": 1, "far": 0},
    "Train": {"near": 1, "far": 0},
    "HTW": {"yes": 1, "no": 0},
    "Pool": {"yes": 1, "no": 0},
    "Commercial": {"yes": 1, "no": 0},
    "Water": {"city": 1, "well": 0},
    "Sewage": {"city": 1, "septic": 0},
    "BasementYesNo": {"yes": 1, "no": 0},
    "Rent_Restricted": {"yes": 1, "no": 0}
}

# Apply mappings or fallback to generic boolean parsing
for col in custom_mappings:
    df_property[col] = df_property[col].map(lambda x: custom_mappings[col].get(str(x).strip().lower(), None))
    df_property[col] = df_property[col].astype("Int64")  # Ensure 0/1 instead of 0.0/1.0


# Replace any remaining NaNs with None
df_property = df_property.astype(object).where(pd.notnull(df_property), None)



# ----------------------------------------------
# Leads Table
# ----------------------------------------------

df_leads = df[leads_columns].copy().astype(object).where(pd.notnull(df[leads_columns]), None)

# ----------------------------------------------
# Valuation Table
# ----------------------------------------------
df_valuation = df[valuation_columns].copy().astype(object).where(pd.notnull(df[valuation_columns]), None)

# ----------------------------------------------
# Rehab Table (includes many boolean flags)
# ----------------------------------------------
df_rehab = df[rehab_columns].copy()
for col in rehab_columns[2:]:
    df_rehab[col] = df_rehab[col].map(parse_boolean)
    df_rehab[col] = df_rehab[col].astype("Int64")

df_rehab = df_rehab.astype(object).where(pd.notnull(df_rehab), None)

# ----------------------------------------------
# HOA Table
# ----------------------------------------------
df_hoa = df[hoa_columns].copy()
df_hoa['HOA_Flag'] = df_hoa['HOA_Flag'].map(parse_boolean)
df_hoa['HOA_Flag'] = df_hoa['HOA_Flag'].astype("Int64")
df_hoa = df_hoa.astype(object).where(pd.notnull(df_hoa), None)

# ----------------------------------------------
# Taxes Table
# ----------------------------------------------
df_taxes = df[taxes_columns].copy().astype(object).where(pd.notnull(df[taxes_columns]), None)

# ----------------------------------------------
# Establish connection to MySQL
# ----------------------------------------------
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)
cursor = conn.cursor()

# ----------------------------------------------
# SQL Insert Templates
# ----------------------------------------------
property_insert = """
INSERT INTO property (
    Property_Title, Address, Market, Flood, Street_Address, City,
    State, Zip, Property_Type, Highway, Train, Tax_Rate,
    SQFT_Basement, HTW, Pool, Commercial, Water, Sewage,
    Year_Built, SQFT_MU, SQFT_Total, Parking, Bed, Bath,
    BasementYesNo, Layout, Rent_Restricted, Neighborhood_Rating,
    Latitude, Longitude, Subdivision, School_Average
) VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s
)
"""

lead_insert = """
INSERT INTO leads (
    property_id, Reviewed_Status, Most_Recent_Status, Source,
    Occupancy, Net_Yield, IRR, Selling_Reason,
    Seller_Retained_Broker, Final_Reviewer
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s
)
"""

valuation_insert = """
INSERT INTO valuation (
    property_id, Previous_Rent, List_Price, Zestimate,
    ARV, Expected_Rent, Rent_Zestimate,
    Low_FMR, High_FMR, Redfin_Value
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s
)
"""

rehab_insert = """
INSERT INTO rehab (
    property_id, Underwriting_Rehab, Rehab_Calculation, Paint,
    Flooring_Flag, Foundation_Flag, Roof_Flag, HVAC_Flag,
    Kitchen_Flag, Bathroom_Flag, Appliances_Flag, Windows_Flag,
    Landscaping_Flag, Trashout_Flag
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s
)
"""

hoa_insert = """
INSERT INTO hoa (
    property_id, HOA, HOA_Flag
) VALUES (
    %s, %s, %s
)
"""

tax_insert = """
INSERT INTO taxes (
    property_id, Taxes
) VALUES (
    %s, %s
)
"""

# ----------------------------------------------
# Load: Insert each row into normalized tables
# ----------------------------------------------
try:
    for i in range(len(df)):
        # Insert property and retrieve primary key
        cursor.execute(property_insert, tuple(df_property.iloc[i]))
        property_id = cursor.lastrowid

        # Insert related records
        cursor.execute(lead_insert, (property_id,) + tuple(df_leads.iloc[i]))
        cursor.execute(valuation_insert, (property_id,) + tuple(df_valuation.iloc[i]))
        cursor.execute(rehab_insert, (property_id,) + tuple(df_rehab.iloc[i]))
        cursor.execute(hoa_insert, (property_id,) + tuple(df_hoa.iloc[i]))
        cursor.execute(tax_insert, (property_id,) + tuple(df_taxes.iloc[i]))

        conn.commit()
    logging.info("✅ Data inserted into all tables.")

    # ----------------------------------------------
    # Save normalized dataframes to CSV files
    # ----------------------------------------------
    
    # output_dir = "/Users/mkmathur/Desktop/homellc_data_engineer_assessment_skeleton/normalized_csvs"
    output_dir = base_dir / "normalized_csvs"
    os.makedirs(output_dir, exist_ok=True)


    df_property.to_csv(f"{output_dir}/property.csv", index=False)
    df_leads.to_csv(f"{output_dir}/leads.csv", index=False)
    df_valuation.to_csv(f"{output_dir}/valuation.csv", index=False)
    df_rehab.to_csv(f"{output_dir}/rehab.csv", index=False)
    df_hoa.to_csv(f"{output_dir}/hoa.csv", index=False)
    df_taxes.to_csv(f"{output_dir}/taxes.csv", index=False)

    logging.info("📝 Normalized CSVs saved to /normalized_csvs/")

     
    
except Exception as e:
    logging.error(f"❌ Error occurred: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()





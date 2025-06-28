# 🏡 Home.LLC Data Engineering Assessment

This repository contains a complete data engineering pipeline for ingesting, validating, storing, and analyzing real estate-related data using MySQL, Python, and Docker.
---


## 📌 Table of Contents

- [Project Overview](#project-overview)
- [Schema Design](#schema-design)
- [ETL Pipeline Design](#etl-pipeline-design)
- [Directory Structure](#directory-structure)
- [Setup & Installation](#setup--installation)
- [How to Run the ETL](#how-to-run-the-etl)
- [Assumptions & Design Decisions](#assumptions--design-decisions)
- [Known Issues & Improvements](#known-issues--improvements)
- [Author](#author)


## 📁 Project Overview

**Objective:**  
Normalize a flat CSV dataset containing property information into a relational schema and develop a Python-based ETL pipeline to transform and load it into a MySQL database.

**Assessment Focus:**

- Data normalization  
- Relational schema design  
- ETL implementation  
- Clean code and documentation  

---

---
## 📁 Project Structure

.
├── analysis_outputs/           # Auto-generated plots and Excel reports
├── docs/                       # Documentation (future expansion)
├── normalized_csvs/           # Cleaned CSVs used in the ETL process
├── scripts/                   # Python scripts
│   ├── etl.py                 # ETL pipeline from CSV to MySQL
│   ├── validate.py            # Data validation based on field config
│   └── analyze.py             # Data analysis and visualizations
├── sql/                       # SQL schema and raw data
│   ├── create_tables.sql      # SQL file to create normalized schema
│   ├── fake_data.csv          # Raw source data
│   └── Field Config.xlsx      # Validation rules and expected types
├── docker-compose.initial.yml # Docker config to spin up MySQL
├── Dockerfile.initial_db      # Docker image definition
├── .env                       # MySQL credentials (used in docker-compose)
├── mismatch_report.xlsx       # Output from validation script
├── README.md                  # You're here :)


## 🛠️ Setup Instructions

Start MySQL with Docker
docker-compose -f docker-compose.initial.yml up -d

MySQL Credentials (from .env or docker-compose):
MYSQL_DATABASE = home_db
MYSQL_USER = db_user
MYSQL_PASSWORD = 6equj5_db_user
MYSQL_ROOT_PASSWORD = 6equj5_root

Create Database Schema
mysql -u root -p < sql/create_tables.sql

Run ETL
python scripts/etl.py

Run Validation
python scripts/validate.py

Run Analysis
python scripts/analyze.py

## 🧩 Database Schema

1. property (Primary table)
Primary Key: id

Stores all static property data such as location, type, year built, utilities, ratings, etc.

2. leads
Primary Key: id

Foreign Key: property_id → property.id

Stores sales-related data: yield, IRR, seller info, occupancy.

3. valuation
Primary Key: id

Foreign Key: property_id → property.id

Contains pricing estimates: ARV, Rent, Zestimate, Redfin values, etc.

4. rehab
Primary Key: id

Foreign Key: property_id → property.id

Tracks rehabilitation estimates and boolean flags for components needing repairs.

5. hoa
Primary Key: id

Foreign Key: property_id → property.id

Stores HOA-related info and flags.

6. taxes
Primary Key: id

Foreign Key: property_id → property.id

Stores tax-related values.

## ✅ Validation Rules

Defined in Field Config.xlsx

Applied using validate.py

Checks include:

Required columns exist in the data

Data types match expectations (e.g., float, int, string, boolean)

Value ranges and missing values

Output is saved in mismatch_report.xlsx showing row-wise and field-wise issues.


## 📊 Analysis Performed
Stored in analysis_outputs/ and Excel sheet full_summary_report_detailed.xlsx.

Key Metrics:
Property Type counts

HOA presence and distribution

Reviewed Status & Lead Sources

Expected Rent:

Mean, Median, Max, Min

Distribution Plot

Taxes:

Mean, Max, Min, Std Dev

Rehab flag counts

Correlation heatmap between valuation features

Rent-to-ARV ratio for investment insights

## 📌 Business Insights
Expected Rent varies from X to Y (see plots), with the average around Z

ARV vs Expected Rent correlation highlights underperforming investments

Rehab Flags provide insight into most common renovation needs (e.g., kitchen/bathroom)

Tax & HOA insights help filter profitable zip codes or areas

Valuation Correlation Matrix reveals relationships like:

High positive correlation: Expected_Rent ↔ ARV

Useful for rental yield modeling






## 🧱 Schema Design

The raw CSV contains fields for properties, leads, valuations, rehabs, HOA data, and taxes. These were decomposed into normalized tables:

- `property`: Core property metadata  
- `leads`: Lead information linked to property  
- `valuation`: Estimated and actual values  
- `rehab`: Rehab estimates and flags  
- `hoa`: Homeowners Association details  
- `taxes`: Property tax values  

Each table is linked via a primary key `property_id` to maintain referential integrity.

---

## 🔁 ETL Pipeline Design

The ETL pipeline is designed to perform the following operations:

1. **Extract**  
   Load the CSV file using `pandas`.

2. **Transform**  
   Clean NaNs, sanitize datatypes, split into normalized datasets.

3. **Load**  
   Insert records into corresponding MySQL tables using `mysql-connector-python`.

All transformations follow best practices for clarity, reusability, and performance.

---

## 📂 Directory Structure

homellc_data_engineer_assessment_skeleton/
├── docs/
│ └── images/
│ └── README.md
│
├── sql/
│ ├── create_tables.sql
│ ├── fake_data.csv
│ └── Field Config.xlsx
│
├── scripts/
│ └── etl.py
│
├── docker-compose.initial.yml
├── docker-compose.final.yml
├── Dockerfile.initial_db
├── Dockerfile.final_db
├── requirements.txt
└── README.md


---

## ⚙️ Setup & Installation

### ✅ Prerequisites

- Python 3.9+
- Docker and Docker Compose
- MySQL client (optional, for inspection)

### 📦 Install Dependencies

python -m venv venv
source venv/bin/activate (Windows: venv\Scripts\activate)
pip install -r requirements.txt


---

## 🚀 How to Run the ETL

### Step 1: Start MySQL via Docker

docker-compose -f docker-compose.initial.yml up --build -d


MySQL will be running on:

- Host: `127.0.0.1`  
- Port: `3306`  
- User: `root`  
- Password: `6equj5_root`  
- Database: `home_db`

### Step 2: Run the ETL Script

python scripts/etl.py


A successful run will print:

✅ Data inserted into all tables.



---

## 🧠 Assumptions & Design Decisions

- One-to-one mapping assumed between property and other related entities in the CSV.
- Used `property_id` as a foreign key across all tables to maintain data integrity.
- Nullable values are handled using `None` in Python.
- Boolean fields normalized using flexible mappings (e.g., `yes`, `true`, `minimal flood`, etc.).
- Type casting is done explicitly using `applymap()` for consistency and error handling.

---

## 🧰 Known Issues & Improvements

- Add batch insert operations for performance scaling.
- Introduce structured logging and more granular exception handling.
- Implement schema validation using libraries like `Pydantic` or `Cerberus`.
- Add unit tests to validate ETL logic and transformations.

---

## 👨‍💻 Author

**Mayank Mathur**  
[LinkedIn Profile](https://www.linkedin.com/in/onlymayank11/)  

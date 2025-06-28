CREATE TABLE property (
    id INT PRIMARY KEY AUTO_INCREMENT,
    Property_Title VARCHAR(255),
    Address TEXT,
    Market VARCHAR(100),
    Flood BOOLEAN,
    Street_Address TEXT,
    City VARCHAR(100),
    State VARCHAR(50),
    Zip VARCHAR(20),
    Property_Type VARCHAR(100),
    Highway BOOLEAN,
    Train BOOLEAN,
    Tax_Rate FLOAT,
    SQFT_Basement INT,
    HTW BOOLEAN,
    Pool BOOLEAN,
    Commercial BOOLEAN,
    Water BOOLEAN,
    Sewage BOOLEAN,
    Year_Built INT,
    SQFT_MU INT,
    SQFT_Total INT,
    Parking VARCHAR(50),
    Bed INT,
    Bath INT,
    BasementYesNo BOOLEAN,
    Layout VARCHAR(100),
    Rent_Restricted BOOLEAN,
    Neighborhood_Rating VARCHAR(50),
    Latitude FLOAT,
    Longitude FLOAT,
    Subdivision VARCHAR(100),
    School_Average FLOAT
);
CREATE TABLE leads (
    id INT PRIMARY KEY AUTO_INCREMENT,
    property_id INT,
    Reviewed_Status VARCHAR(100),
    Most_Recent_Status VARCHAR(100),
    Source VARCHAR(100),
    Occupancy VARCHAR(100),
    Net_Yield FLOAT,
    IRR FLOAT,
    Selling_Reason VARCHAR(255),
    Seller_Retained_Broker VARCHAR(255),
    Final_Reviewer VARCHAR(255),
    FOREIGN KEY (property_id) REFERENCES property(id)
);
CREATE TABLE valuation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    property_id INT,
    Previous_Rent FLOAT,
    List_Price FLOAT,
    Zestimate FLOAT,
    ARV FLOAT,
    Expected_Rent FLOAT,
    Rent_Zestimate FLOAT,
    Low_FMR FLOAT,
    High_FMR FLOAT,
    Redfin_Value FLOAT,
    FOREIGN KEY (property_id) REFERENCES property(id)
);
CREATE TABLE rehab (
    id INT PRIMARY KEY AUTO_INCREMENT,
    property_id INT,
    Underwriting_Rehab FLOAT,
    Rehab_Calculation FLOAT,
    Paint BOOLEAN,
    Flooring_Flag BOOLEAN,
    Foundation_Flag BOOLEAN,
    Roof_Flag BOOLEAN,
    HVAC_Flag BOOLEAN,
    Kitchen_Flag BOOLEAN,
    Bathroom_Flag BOOLEAN,
    Appliances_Flag BOOLEAN,
    Windows_Flag BOOLEAN,
    Landscaping_Flag BOOLEAN,
    Trashout_Flag BOOLEAN,
    FOREIGN KEY (property_id) REFERENCES property(id)
);
CREATE TABLE hoa (
    id INT PRIMARY KEY AUTO_INCREMENT,
    property_id INT,
    HOA VARCHAR(100),
    HOA_Flag BOOLEAN,
    FOREIGN KEY (property_id) REFERENCES property(id)
);
CREATE TABLE taxes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    property_id INT,
    Taxes FLOAT,
    FOREIGN KEY (property_id) REFERENCES property(id)
);

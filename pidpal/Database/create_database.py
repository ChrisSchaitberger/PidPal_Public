# This script is currently a standalone script that will make a database 'master.db' within the Database directory (folder)
# You only need to one it one, but it is coded to check if database exists first so you cant mess it up by running it again.
# We do not need to interact with the Properties table right now we can focus on the Parcel Table 
# Most importantly, I made all data types TEXT (str) for now so we can start importing to database with the current str data types we are pulling from the html elements

import sqlite3
import os

# Check for 'Database' then create if it doesn't exist 
database_dir = "Database"
os.makedirs(database_dir, exist_ok=True)

# Path to the database file within the 'Database' directory
db_path = os.path.join(database_dir, "master.db")

# Check if the database already exists
database_exists = os.path.exists(db_path)

# Connect to the database
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key constraints 
cursor = conn.cursor()

if not database_exists:
    # Create Parcels table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Parcels (
        ParcelID TEXT PRIMARY KEY,
        State TEXT,
        County TEXT,
        LandValue TEXT,
        BuildingValue TEXT,
        TotalValue TEXT,
        AssessmentYear TEXT,
        LastScraped TEXT,
        ScreenshotPath TEXT
    );
    ''')

    # Create Properties table linked by ParcelID
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Properties (
        PropertyID TEXT PRIMARY KEY,
        Owner TEXT,
        ParcelID TEXT NOT NULL,
        FOREIGN KEY (ParcelID) REFERENCES Parcels(ParcelID) 
    );
    ''')

    conn.commit()
    print(f"Database and tables created at: {db_path}")
else:
    print(f"Connected to existing database at: {db_path}")

# Close the connection
conn.close()

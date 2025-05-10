# A module for functions (an other doodads as arises)
import os
import sqlite3
import datetime

def insert_initial_parcels(data_list, db_path=r"Database\master.db"):
    """
    Inserts initial parcel data (from the UI table) into the Parcels and Properties tables.
    This function is called before starting the scraping.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for data in data_list:
        parcelID = data.get("ParcelID", "")
        county = data.get("County", "")
        state = data.get("State", "")
        propertyID = data.get("PropertyID", "")
        owner = data.get("Owner", "")
        
        # Insert initial data into the Parcels table.
        # Leaving scraped data values empty
        # Setting LastScraped to the current time
        # Using Insert or replace for now, will work great for one off use (Not collecting data year over year (Could version/partition with this method))
        cursor.execute('''
            INSERT OR REPLACE INTO Parcels (
                ParcelID, State, County, LandValue, BuildingValue, TotalValue, AssessmentYear, LastScraped, ScreenshotPath
            )
            VALUES (:ParcelID, :State, :County, :LandValue, :BuildingValue, :TotalValue, :AssessmentYear, :LastScraped, :ScreenshotPath
            )
        ''',{
            "ParcelID": parcelID,
            "State": state,
            "County": county,
            "LandValue": None,
            "BuildingValue": None,
            "TotalValue": None,
            "AssessmentYear": None,
            "LastScraped": None,
            "ScreenshotPath": None
        })
        
        # If propertyID is provided, insert into the Properties table.
        if propertyID:
            cursor.execute('''
                INSERT OR REPLACE INTO Properties (
                    PropertyID, Owner, ParcelID
                )
                VALUES (:PropertyID, :Owner, :ParcelID)
            ''', {
                "PropertyID": propertyID,
                "Owner": owner,
                "ParcelID": parcelID
            })
    
    conn.commit()
    conn.close()

def insert_scraped_data(scraped_data, db_path=r"Database\master.db"):
    """
    Updates the Parcels table with the scraped data from the scrape all data objects (and the current time).
    Assumes scraped_data is a list of DataObject instances that have attributes:
    ParcelID, LandValue, BuildingValue, TotalValue, AssessmentYear, ScreenshotPath.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Set a new timestamp for LastScraped.
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for obj in scraped_data:
        cursor.execute('''
            UPDATE Parcels 
            SET LandValue = ?,
                BuildingValue = ?,
                TotalValue = ?,
                AssessmentYear = ?,
                LastScraped = ?,
                ScreenshotPath = ?
            WHERE ParcelID = ?
        ''', (
            obj.LandValue,
            obj.BuildingValue,
            obj.TotalValue,
            obj.AssessmentYear,
            now,
            obj.ScreenshotPath,
            obj.ParcelID
        ))
    
    conn.commit()
    conn.close()


DB_PATH = os.path.join("Database", "master.db")


def query_parcels(filters=None, sort_by=None, sort_order="ASC"):
    """
    Dynamically queries parcel data joined with the 'Properties' table in master.db.
    Returns rows with columns:
       ParcelID, State, County, LandValue, BuildingValue, TotalValue,
       AssessmentYear, LastScraped, PropertyID, Owner

    :param filters: dict of {column_name: value} for exact matches 
                    e.g. {"State": "OH", "County": "Franklin"}.
                    Allowed filter keys: [ParcelID, State, County, PropertyID, Owner].
                    If None or empty, no WHERE clause is used.
    :param sort_by: column name to sort by (optional). Must be one of:
                    [ParcelID, State, County, LandValue, BuildingValue,
                     TotalValue, AssessmentYear, LastScraped, PropertyID, Owner].
    :param sort_order: 'ASC' or 'DESC'. Defaults to 'ASC'.
    :return: A list of dictionaries, each representing a joined row 
             from Parcels + Properties.

    EXAMPLE:
        results = query_parcels(
            filters={"State": "OH", "County": "Franklin"},
            sort_by="ParcelID",
            sort_order="ASC"
        )
    """

    # 1) Base SELECT query with LEFT JOIN on Properties
    query = """
        SELECT 
            p.ParcelID,
            p.State,
            p.County,
            p.LandValue,
            p.BuildingValue,
            p.TotalValue,
            p.AssessmentYear,
            p.LastScraped,
            pr.PropertyID,
            pr.Owner
        FROM Parcels p
        LEFT JOIN Properties pr
            ON p.ParcelID = pr.ParcelID
    """

    # 2) Build WHERE clause if filters provided
    where_clauses = []
    values = []

    # Valid columns we allow filtering on
    valid_filter_keys = {
        "ParcelID": "p.ParcelID",
        "State": "p.State",
        "County": "p.County",
        "PropertyID": "pr.PropertyID",
        "Owner": "pr.Owner"
    }

    if filters:
        for col_name, val in filters.items():
            if col_name in valid_filter_keys:
                where_clauses.append(f"{valid_filter_keys[col_name]} = ?")
                values.append(val)
            else:
                # Ignore any unknown filters or raise an error
                pass

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # 3) Sorting
    valid_sort_columns = {
        "ParcelID": "p.ParcelID",
        "State": "p.State",
        "County": "p.County",
        "LandValue": "p.LandValue",
        "BuildingValue": "p.BuildingValue",
        "TotalValue": "p.TotalValue",
        "AssessmentYear": "p.AssessmentYear",
        "LastScraped": "p.LastScraped",
        "PropertyID": "pr.PropertyID",
        "Owner": "pr.Owner"
    }

    if sort_by and sort_by in valid_sort_columns:
        # Validate sort_order
        sort_order = sort_order.upper()
        if sort_order not in ["ASC", "DESC"]:
            sort_order = "ASC"
        query += f" ORDER BY {valid_sort_columns[sort_by]} {sort_order}"

    # 4) Execute the query
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute(query, values)
    rows = cursor.fetchall()

    # 5) Convert rows to list of dictionaries
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return results


def get_screenshot_path(parcel_id):
    """
    Retrieves the ScreenshotPath for a given ParcelID (if it exists).
    Returns a string path or None.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ScreenshotPath FROM Parcels WHERE ParcelID = ?
    """, (parcel_id,))
    row = cursor.fetchone()

    conn.close()
    if row:
        return row[0]  # might be None if not set
    return None
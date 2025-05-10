import os
import re

# Data Object for scraping collection TODO: Add data transformation functions
class DataObject:
    def __init__(self, ParcelID, LandValue = None, BuildingValue = None, TotalValue = None, AssessmentYear = None, ScreenshotPath = None):
        self.ParcelID = ParcelID # Parcel ID
        self.LandValue = LandValue # Assessed Land Value
        self.BuildingValue = BuildingValue # Asessed building/Improvement Value
        self.TotalValue = TotalValue # Total assessed value
        self.AssessmentYear = AssessmentYear # Assessed year
        self.ScreenshotPath= ScreenshotPath # Path to saved screenshot 
    
    # Function within Dataobject (DO) to transform DO to Dictionary for native python processsing
    def to_dict(self):
        return {
            "ParcelID": self.ParcelID,
            "LandValue": self.LandValue,
            "BuildingValue": self.BuildingValue,
            "TotalValue": self.TotalValue,
            "AssessmentYear": self.AssessmentYear,
            "ScreenshotPath": self.ScreenshotPath
        }


def take_screenshot(driver, screenshot_dir, filename):
    """
    Takes a screenshot of the current page, automatically sanitizing
    any invalid filename characters in 'filename'.

    Arguments:
        driver: The Selenium WebDriver instance
        screenshot_dir: The directory where the screenshot will be saved
        filename: The intended name of the screenshot file.

    Returns:
        str: The full path to the saved screenshot.
    """

    # Create the screenshot directory if it doesn't exist
    os.makedirs(screenshot_dir, exist_ok=True)

    # Inline sanitization of any Windows-invalid characters
    safe_filename = re.sub(r'[\\/:*?"<>|]+', '_', filename)

    # Adjust browser window size dynamically (for a full-page screenshot)
    page_width = driver.execute_script("return document.body.scrollWidth")
    page_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(page_width, page_height)

    # Build the screenshot path and save
    screenshot_path = os.path.join(screenshot_dir, safe_filename)
    driver.save_screenshot(screenshot_path)

    return screenshot_path


import datetime

def clean_record(record):
    """
    Cleans a single record (dictionary) in-place, converting string fields to
    appropriate Python types.

    Expects keys like:
      ParcelID        (string)
      State           (string)
      County          (string)
      LandValue       (string with commas, e.g. "61,000")
      BuildingValue   (string with commas, e.g. "86,900")
      TotalValue      (string with commas, e.g. "155,800")
      AssessmentYear  (string or int)
      LastScraped     (string datetime, e.g. "2025-03-22 13:03:38")
      PropertyID      (string or "None")

    Returns the same dictionary with cleaned values:
      LandValue, BuildingValue, TotalValue => float (or int if you prefer)
      AssessmentYear                       => int
      LastScraped                          => datetime.datetime
      PropertyID                           => None if "None", else original string
    """

    # Helper to parse numeric strings like "61,000" -> 61000.0 (float)
    def parse_numeric(val):
        if not val:
            return 0.0
        val = val.replace(",", "")
        try:
            return float(val)
        except ValueError:
            return 0.0

    # Clean the numeric columns
    if "LandValue" in record:
        record["LandValue"] = parse_numeric(record["LandValue"])
    if "BuildingValue" in record:
        record["BuildingValue"] = parse_numeric(record["BuildingValue"])
    if "TotalValue" in record:
        record["TotalValue"] = parse_numeric(record["TotalValue"])

    # AssessmentYear -> int if possible
    if "AssessmentYear" in record and record["AssessmentYear"] is not None:
        try:
            record["AssessmentYear"] = int(record["AssessmentYear"])
        except ValueError:
            record["AssessmentYear"] = None

    # LastScraped -> datetime
    # e.g. "2025-03-22 13:03:38" -> datetime(2025, 3, 22, 13, 3, 38)
    if "LastScraped" in record and record["LastScraped"]:
        try:
            record["LastScraped"] = datetime.datetime.strptime(record["LastScraped"], "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            record["LastScraped"] = None  # or leave as-is

    # PropertyID -> None if "None"
    if "PropertyID" in record:
        if record["PropertyID"] == "None":
            record["PropertyID"] = None

    return record


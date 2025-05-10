import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

def geocode_counties(input_csv, output_csv):
    """
    Reads 'County/City,State,Status,Link' from input_csv,
    geocodes each row to get latitude & longitude,
    then writes a new CSV with 'lat' and 'lon' columns.
    """
    # Read the CSV (adjust if using different separators or file type)
    df = pd.read_csv(input_csv)

    # Initialize Nominatim geolocator with a custom user-agent
    geolocator = Nominatim(user_agent="pidpal_app")

    latitudes = []
    longitudes = []

    # Loop over each row
    for index, row in df.iterrows():
        # Combine county/city + state into one search string
        location_str = f"{row['County/City']}, {row['State']}"
        print(f"Geocoding: {location_str}")

        try:
            location = geolocator.geocode(location_str)
            if location:
                latitudes.append(location.latitude)
                longitudes.append(location.longitude)
                print(f" -> Found: ({location.latitude}, {location.longitude})")
            else:
                # Couldn't find an exact match
                latitudes.append(None)
                longitudes.append(None)
                print(" -> Not found")
        except Exception as e:
            # In case of connection issues or other errors
            latitudes.append(None)
            longitudes.append(None)
            print(f" -> Error: {e}")

        # Optional: Sleep to respect usage limits
        sleep(1)

    # Add columns for lat/lon
    df['lat'] = latitudes
    df['lon'] = longitudes

    # Save the updated CSV
    df.to_csv(output_csv, index=False)
    print(f"Done! Results saved to {output_csv}")

# If you want to run this file directly (instead of importing), uncomment:
if __name__ == "__main__":
    input_file = "Resources/PidPal Counties Tracker - HTM(L)AP.csv"
    output_file = "Resources/PidPal Counties Tracker.csv"
    geocode_counties(input_file, output_file)

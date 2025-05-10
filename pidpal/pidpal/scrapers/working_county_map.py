# leaflet_map.py

import pandas as pd
import json

def generate_leaflet_map_html(csv_path: str) -> str:
    """
    Reads a CSV expected to have columns:
      - County/City
      - State
      - Status
      - Link
      - lat
      - lon

    Returns a Leaflet-based HTML string with pins
    auto-zoomed to show all valid lat/lon entries.
    """
    # 1) Read the CSV
    df = pd.read_csv(csv_path)
    
    # Optional debug checks
    # print("DataFrame columns:", df.columns)
    # print(df.head())

    # 2) Basic HTML with Leaflet
    # Note: We do NOT use 'integrity' attributes, to avoid SRI mismatches in PyQt
    html_template = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>Leaflet Map</title>
        <style>
          html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
          }
          #map {
            height: 100%;
            width: 100%;
          }
        </style>

        <!-- Leaflet CSS -->
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css"
          crossorigin=""
        />
      </head>
      <body>
        <div id="map"></div>

        <!-- Leaflet JS -->
        <script
          src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"
          crossorigin="">
        </script>

        <script>
          // Create the Leaflet map
          var map = L.map('map');

          // Tile layer from OpenStreetMap (no curly braces for .format needed)
          L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
          }).addTo(map);

          // Create a feature group for markers
          var markerGroup = L.featureGroup().addTo(map);

          {markers_script}

          // Attempt to fit the map to the marker bounds
          var bounds = markerGroup.getBounds();
          if (bounds.isValid()) {{
            map.fitBounds(bounds);
          }} else {{
            // Fallback: center on continental US if no valid markers
            map.setView([37.0902, -95.7129], 4);
          }}
        </script>
      </body>
    </html>
    """

    # 3) Build the markers script
    markers_script_lines = []
    for i, row in df.iterrows():
        county_city = row.get('County/City', '')
        state       = row.get('State', '')
        status      = row.get('Status', '')
        link        = row.get('Link', '')
        lat         = row.get('lat', None)
        lon         = row.get('lon', None)

        # Ensure lat/lon are valid
        if pd.isna(lat) or pd.isna(lon):
            continue  # skip this row if lat/lon is missing

        # Build popup HTML
        popup_content = (
            f"<b>{county_city}, {state}</b><br>"
            f"Status: {status}<br>"
            f"<a href='{link}' target='_blank'>{link}</a>"
        )

        # Escape special chars (apostrophes, quotes) via json.dumps
        popup_content_js = json.dumps(popup_content)

        marker_line = f"""
        L.marker([{lat}, {lon}])
         .bindPopup({popup_content_js})
         .addTo(markerGroup);
        """
        markers_script_lines.append(marker_line.strip())

    # Join all marker lines into one JavaScript block
    markers_script = "\n".join(markers_script_lines)

    # 4) Insert the markers script into the HTML template
    final_html = html_template.replace("{markers_script}", markers_script)
    return final_html

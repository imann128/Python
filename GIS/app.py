import sqlite3
import os
from PIL import Image

# Cross-platform paths for images (in WSL format)
image_paths = {
    'Faisal Mosque Google Maps': '/mnt/c/Users/Hp/Documents/GIS_Lab/images/Faisal Mosque.jpg',
    'Margalla Hills Google Maps': '/mnt/c/Users/Hp/Documents/GIS_Lab/images/Margalla Hills.jpg',
    'F-9 Park Google Maps': '/mnt/c/Users/Hp/Documents/GIS_Lab/images/F-9 park.png',
    'OSM Faisal Mosque OSM': '/mnt/c/Users/Hp/Documents/GIS_Lab/images/OSM Faisal Mosque.png',
    'OSM Trail 5 OSM': '/mnt/c/Users/Hp/Documents/GIS_Lab/images/OSM Trail 5.png',
    'Faisal Mosque NASA Worldview NASA Worldview': '/mnt/c/Users/Hp/Documents/GIS_Lab/images/Faisal Mosque NASA worldview.png'
}

# Get image resolution using Pillow
def get_image_resolution(image_path):
    image = Image.open(image_path)
    return image.size  # returns width, height

# Connect to the SQLite database
conn = sqlite3.connect('gis_metadata.db')
cursor = conn.cursor()

# Create the table (if it doesn’t exist)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS gis_metadata (
        ID INTEGER PRIMARY KEY,
        ImagePath TEXT,
        LandmarkName TEXT,
        Latitude FLOAT,
        Longitude FLOAT,
        Comments TEXT,
        Resolution TEXT,
        Source TEXT
    )
''')

# Data to insert (Landmarks, Coordinates, Comments, and Sources)
landmarks = [
    ('Faisal Mosque', 33.7296, 73.9934, 'A beautiful mosque in Islamabad.', 'Google Maps'),
    ('Margalla Hills', 33.7115, 73.0830, 'A scenic mountain range in Islamabad.', 'Google Maps'),
    ('F-9 Park', 33.6695, 73.0484, 'A popular park in Islamabad.', 'Google Maps'),
    ('OSM Faisal Mosque', 33.7296, 73.9934, 'Faisal Mosque view from OpenStreetMap.', 'OSM'),
    ('OSM Trail 5', 33.6871, 73.0551, 'Trail 5 in Margalla Hills from OpenStreetMap.', 'OSM'),
    ('Faisal Mosque NASA Worldview', 33.7296, 73.9934, 'Satellite view of Faisal Mosque from NASA Worldview.', 'NASA Worldview')
]

# Insert data for each landmark
for landmark_name, lat, lon, comments, source in landmarks:
    # Construct the key explicitly as 'Landmark Source' (e.g., 'Faisal Mosque Google Maps')
    image_key = f'{landmark_name} {source}'  # Correct format like 'Faisal Mosque Google Maps'

    # Get the image path from the dictionary using the constructed key
    image_path = image_paths.get(image_key)  # Use get() to avoid KeyError
    if not image_path:
        print(f"Warning: Image path for '{image_key}' not found.")
        continue

    width, height = get_image_resolution(image_path)  # Get resolution
    resolution = f"{width}x{height}"

    # Insert the data into the database
    cursor.execute('''
        INSERT INTO gis_metadata (ImagePath, LandmarkName, Latitude, Longitude, Comments, Resolution, Source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (image_path, landmark_name, lat, lon, comments, resolution, source))

# Commit the changes to the database
conn.commit()

# Confirm the data insertion
print("Data inserted successfully!")

# Query all rows from the gis_metadata table and print them
cursor.execute('SELECT * FROM gis_metadata')
rows = cursor.fetchall()

# Print each row to verify the data
print("\nData in the table:")
for row in rows:
    print(row)

# Close the connection
conn.close()

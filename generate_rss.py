import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

station_id = "0913TH"
api_url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{station_id}"

try:
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    logging.error(f"Failed to fetch data from API: {e}")
    data = {}

station_name = data.get("items", {}).get("label", f"Station {station_id}")
level = "N/A"
trend = "N/A"
timestamp = datetime.utcnow().isoformat()

# Safely extract latest reading from items > measures > latestReading
measures = data.get("items", {}).get("measures", [])
if measures and isinstance(measures, list):
    latest_reading = measures[0].get("latestReading", {})
    level = latest_reading.get("value", "N/A")
    if level == "N/A":
        logging.warning("Missing 'value' in latest reading.")
    timestamp = latest_reading.get("dateTime", timestamp)
    if timestamp == datetime.utcnow().isoformat():
        logging.warning("Missing 'dateTime' in latest reading.")
    trend = latest_reading.get("trend", "N/A")
    if trend == "N/A":
        logging.warning("Missing 'trend' in latest reading.")
else:
    logging.warning("Missing or invalid 'measures' data.")

# Format timestamp to readable string
try:
    formatted_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
except Exception as e:
    logging.warning(f"Failed to format timestamp: {e}")
    formatted_timestamp = timestamp

# Create RSS feed
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = f"{station_name} River Level"
ET.SubElement(channel, "link").text = api_url
ET.SubElement(channel, "description").text = "Live river level updates"
ET.SubElement(channel, "lastBuildDate").text = formatted_timestamp

item = ET.SubElement(channel, "item")
ET.SubElement(item, "title").text = f"Level: {level}m"
ET.SubElement(item, "description").text = f"Trend: {trend}, Time: {formatted_timestamp}"
ET.SubElement(item, "pubDate").text = formatted_timestamp
ET.SubElement(item, "guid").text = f"{station_id}-{formatted_timestamp}"

tree = ET.ElementTree(rss)
tree.write("shillbrook_river_level.xml", encoding="utf-8", xml_declaration=True)
print("RSS feed generated successfully.")

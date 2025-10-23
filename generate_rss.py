import requests
import xml.etree.ElementTree as ET
from datetime import datetime

station_id = "0913TH"
api_url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{station_id}"

response = requests.get(api_url)
data = response.json()

station_name = data.get("label", f"Station {station_id}")
level = "N/A"
trend = "N/A"
timestamp = datetime.utcnow().isoformat()

# Safely extract latest reading
measures = data.get("measures", [])
if measures and isinstance(measures, list):
    latest_reading = measures[0].get("latestReading", {})
    level = latest_reading.get("value", "N/A")
    timestamp = latest_reading.get("dateTime", timestamp)
    trend = latest_reading.get("trend", "N/A")

# Create RSS feed
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = f"{station_name} River Level"
ET.SubElement(channel, "link").text = api_url
ET.SubElement(channel, "description").text = "Live river level updates"
ET.SubElement(channel, "lastBuildDate").text = timestamp

item = ET.SubElement(channel, "item")
ET.SubElement(item, "title").text = f"Level: {level}m"
ET.SubElement(item, "description").text = f"Trend: {trend}, Time: {timestamp}"
ET.SubElement(item, "pubDate").text = timestamp
ET.SubElement(item, "guid").text = f"{station_id}-{timestamp}"

tree = ET.ElementTree(rss)
tree.write("shillbrook_river_level.xml", encoding="utf-8", xml_declaration=True)

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

station_id = "0913TH"
api_url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{station_id}"

response = requests.get(api_url)
data = response.json()

# Navigate to items > measures > latestReading
items = data.get("items", {})
measures = items.get("measures", {})

latest = measures.get("latestReading", {})
value = latest.get("value", "N/A")
timestamp = latest.get("dateTime", datetime.utcnow().isoformat())

# Format timestamp
try:
    formatted_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
except Exception:
    formatted_timestamp = timestamp

# Create RSS feed
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "Shill Brook River Level"
ET.SubElement(channel, "link").text = api_url
ET.SubElement(channel, "description").text = "Live river level updates from the Environment Agency"
ET.SubElement(channel, "lastBuildDate").text = formatted_timestamp

item = ET.SubElement(channel, "item")
ET.SubElement(item, "title").text = f"Level: {value}m"
ET.SubElement(item, "description").text = f"Observed at: {formatted_timestamp}"
ET.SubElement(item, "pubDate").text = formatted_timestamp
ET.SubElement(item, "guid").text = f"{station_id}-{formatted_timestamp}"

tree = ET.ElementTree(rss)
tree.write("shillbrook_river_level.xml", encoding="utf-8", xml_declaration=True)
print("✅ RSS feed generated successfully.")

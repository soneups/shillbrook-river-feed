import requests
import xml.etree.ElementTree as ET
from datetime import datetime

API_URL = "https://environment.data.gov.uk/flood-monitoring/id/stations/0913TH"

def fetch_latest_reading():
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()

    items = data.get("items", {})
    measures = items.get("measures", [])

    latest = {}
    if isinstance(measures, list) and measures:
        latest = measures[0].get("latestReading", {})
    elif isinstance(measures, dict):
        latest = measures.get("latestReading", {})

    value = latest.get("value")
    timestamp = latest.get("dateTime")

    if not value or not timestamp:
        raise ValueError("Could not extract latest reading from API response.")

    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    formatted_time = dt.strftime("%d/%m/%Y %H:%M")
    rss_pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S %z")
    return value, formatted_time, rss_pub_date

def generate_rss(value, formatted_time, rss_pub_date):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Shill Brook River Level"
    ET.SubElement(channel, "link").text = "https://environment.data.gov.uk/flood-monitoring/id/stations/0913TH"
    ET.SubElement(channel, "description").text = "Latest river level data for Shill Brook"

    item = ET.SubElement(channel, "item")
    title_text = f"{formatted_time} – {value}m"
    ET.SubElement(item, "title").text = title_text
    ET.SubElement(item, "description").text = title_text
    ET.SubElement(item, "pubDate").text = rss_pub_date
    ET.SubElement(item, "guid").text = rss_pub_date

    tree = ET.ElementTree(rss)
    tree.write("shillbrook_river_level.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    value, formatted_time, rss_pub_date = fetch_latest_reading()
    generate_rss(value, formatted_time, rss_pub_date)

import requests
import json
import time
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

API_URL = "https://nameday.abalin.net/api/V2/today/bratislava"
MAX_RETRIES = 5
RETRY_DELAY = 5  # sekúnd

def get_namedays():
    for i in range(MAX_RETRIES):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()  # Vyvolá výnimku pre chybné HTTP status kódy
            data = response.json()
            if "data" in data and "sk" in data["data"]:
                return data["data"]["sk"]
            else:
                print(f"Neočakávaný formát odpovede API. Pokus {i+1} z {MAX_RETRIES}.")
        except requests.exceptions.RequestException as e:
            print(f"Chyba pri volaní API: {e}. Pokus {i+1} z {MAX_RETRIES}.")
        except json.JSONDecodeError:
            print(f"Chyba pri dekódovaní JSON odpovede. Pokus {i+1} z {MAX_RETRIES}.")

        if i < MAX_RETRIES - 1:
            print(f"Čakám {RETRY_DELAY} sekúnd pred ďalším pokusom...")
            time.sleep(RETRY_DELAY)
            RETRY_DELAY *= 2

    print("Všetky pokusy na získanie menín zlyhali.")
    return None

def create_rss_feed(namedays):
    if not namedays:
        return None

    rss = Element('rss', version="2.0")
    channel = SubElement(rss, 'channel')

    title = SubElement(channel, 'title')
    title.text = "Meniny na Slovensku"

    link = SubElement(channel, 'link')
    link.text = "https://github.com/DKR450/workflows/blob/main/meniny.xml"

    description = SubElement(channel, 'description')
    description.text = f"Meniny na Slovensku pre dnešný deň: {namedays}"

    language = SubElement(channel, 'language')
    language.text = "sk"

    item = SubElement(channel, 'item')

    item_title = SubElement(item, 'title')
    item_title.text = f"Dnes má meniny {namedays}"

    item_link = SubElement(item, 'link')
    item_link.text = "https://github.com/DKR450/workflows/blob/main/meniny.xml"

    item_description = SubElement(item, 'description')
    item_description.text = f"Dnes má meniny {namedays}"

    pub_date = SubElement(item, 'pubDate')
    pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

    return tostring(rss, 'utf-8')

def save_to_xml(rss_content, filename="meniny.xml"):
    if rss_content:
        dom = minidom.parseString(rss_content)
        pretty_xml = dom.toprettyxml(indent="  ")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        print(f"RSS súbor bol úspešne uložený do {filename}")
    else:
        print("Nepodarilo sa vytvoriť RSS súbor.")

if __name__ == "__main__":
    namedays = get_namedays()
    if namedays:
        rss_content = create_rss_feed(namedays)
        save_to_xml(rss_content)

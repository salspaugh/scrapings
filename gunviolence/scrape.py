#import argparse
import bs4
import requests
import pandas
import sys

BASE_URL = "http://www.gunviolencearchive.org"
URL_72_HRS = "http://www.gunviolencearchive.org/last-72-hours"

TABLE_COLUMNS = [
    "Incident Date",
    "State",
    "City or County",
    "Address",
    "Number Killed",
    "Number Injured",
    "Operations",
]

DETAIL_COLUMNS = [
    "ID",
    "Location Description",
    "Latitude",
    "Longitude",
    "Characteristics",
    "Notes",
    "Congressional District",
    "State Senate District",
    "State House District"
]

incidents = { c: [] for c in TABLE_COLUMNS + DETAIL_COLUMNS }

participants = {
    "Incident ID": [],
    "Type": [],
    "Name": [],
    "Age": [],
    "Age Group": [],
    "Gender": [],
    "Status": [],
    "Relationship": []
}

def scrape():
    incident_id = 0
    url = URL_72_HRS
    scrape_page(URL_72_HRS, incident_id)
    for p in range(1, 9):
        url = URL_72_HRS + "?page=%s" % p
        scrape_page(url, incident_id)
    characteristics_to_binary(incidents)
    del incidents["Characteristics"]
    del incidents["Operations"]
    #for (attr, vals) in participants.iteritems():
    #    print attr, len(vals)
    incidents_df = pandas.DataFrame(incidents) 
    incidents_df = incidents_df.drop_duplicates()
    participants_df = pandas.DataFrame(participants)

    incidents_df.to_csv("incidents.csv", index=False, na_rep="N/A", encoding='utf-8') 
    participants_df.to_csv("participants.csv", index=False, na_rep="N/A", encoding='utf-8')

def characteristics_to_binary(incidents):
    characteristics = set()
    for c in incidents["Characteristics"]:
        characteristics.update(c)
    for c in characteristics:
        incidents[c] = []
    for c in incidents["Characteristics"]:
        ones = set(c)
        zeros = characteristics.difference(ones)
        for one in ones:
            incidents[one].append(True)
        for zero in zeros:
            incidents[zero].append(False)

def scrape_page(url, incident_id):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text)
    for row in soup.find_all("tr"):
        entries = list(row.find_all("td"))
        if len(entries) > 0:
            href = entries[-1].find_all("a")[0]["href"]
            incident_url = BASE_URL + "%s" % href
            incidents["ID"].append(incident_id)
            scrape_details(incident_url, incident_id)
            incident_id += 1
        for c, e in zip(TABLE_COLUMNS, entries):
            incidents[c].append(e.text)

def scrape_location(div):
    location_description = []
    lat = "N/A"
    long = "N/A"
    for child in div.find_all("span"):
        text = child.text
        if child.text.find("Geolocation") == -1:
            location_description.append(text)
        else:
            geolocation = text
            coords = geolocation.split(":")[1].strip().split(",")
            lat = float(coords[0].strip())
            long = float(coords[1].strip())
    desc = "; ".join(location_description)
    incidents["Location Description"].append(desc)
    incidents["Latitude"].append(lat)
    incidents["Longitude"].append(long)

def scrape_participants(div, incident_id):
    participant = {}
    for child in div.find_all("li"):

        pair = child.text.split(":")
        attr = pair[0].strip()
        val = pair[1].strip()

        if attr == "Type" and len(participant) > 0:
            participant["Incident ID"] = incident_id # set incident ID
            for (k, v) in participant.iteritems(): # add participant data to list
                participants[k].append(v)
            for k in participants.keys(): # add null columns
                if k not in participant.keys():
                    participants[k].append("")
            participant = {} # reset
        participant[attr] = val

    # add last in list in div
    if len(participant) > 0:
        participant["Incident ID"] = incident_id
        for (k, v) in participant.iteritems():
            participants[k].append(v)
        for k in participants.keys():
            if k not in participant.keys():
                participants[k].append("")


def scrape_characteristics(div):
    characteristics = []
    for child in div.find_all("li"):
        characteristics.append(child.text)
    incidents["Characteristics"].append(characteristics)

def scrape_notes(div):
    text = []
    for child in div.find_all("p"):
        text.append(child.text)
    incidents["Notes"].append("; ".join(text))

def scrape_district(div):
    for line in div.text.split("\n"):
        if line.find(":") > -1:
            attr, val = line.split(":")
            attr = attr.strip()
            val = val.strip()
            if len(val) > 0:
                val = int(val)
            else:
                val = "N/A"
            incidents[attr].append(val)


def scrape_details(url, incident_id):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text)
    main = soup.find("div", id="block-system-main")
    for div in main.find_all("div"):
        for h2 in div.find_all("h2"):
            if h2.text == "Location":
                scrape_location(div)
            if h2.text == "Participants":
                attrs = scrape_participants(div, incident_id)
            if h2.text == "Incident Characteristics":
                scrape_characteristics(div)
            if h2.text == "Notes":
                scrape_notes(div)
            if h2.text == "District":
                scrape_district(div)
    all_text = main.text
    if all_text.find("Notes") == -1:
        incidents["Notes"].append("")
    if all_text.find("Incident Characteristics") == -1:
        incidents["Characteristics"].append("")
    if all_text.find("Congressional District") == -1:
        incidents["Congressional District"].append("")
        incidents["State Senate District"].append("")
        incidents["State House District"].append("")

if __name__ == "__main__":
    scrape()

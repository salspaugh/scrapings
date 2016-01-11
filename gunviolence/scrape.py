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
    "Num_killed",
    "Num_injured",
    "Operations",
]

DETAIL_COLUMNS = [
    "ID",
    "Location Description",
    "Latitude",
    "Longitude",
    "Characteristics"
]

incidents = { c: [] for c in TABLE_COLUMNS + DETAIL_COLUMNS }

participants = {
    "Incident": [],
    "Type": [],
    "Name": [],
    "Age": [],
    "Age Group": [],
    "Gender": [],
    "Status": []
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
    incidents_df = pandas.DataFrame(incidents) 
    incidents_df = incidents_df.drop_duplicates()
    participants_df = pandas.DataFrame(participants)
    incidents_df.to_csv("incidents.csv")  
    participants_df.to_csv("participants.csv")

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
            incidents[one].append(1)
        for zero in zeros:
            incidents[zero].append(0)

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
        if child.text.find("Geolocation") == -1:
            location_description.append(child.text)
        else:
            geolocation = child.text
            coords = geolocation.split(":")[1].strip().split(",")
            lat = float(coords[0].strip())
            long = float(coords[1].strip())
    desc = "\n".join(location_description)
    incidents["Location Description"].append(desc)
    incidents["Latitude"].append(lat)
    incidents["Longitude"].append(long)

def scrape_participants(div, incident_id):
    participant = {}
    for child in div.find_all("li"):
        if child.text == "Victim" or child.text == "Perpetrator":
            for (attr, val) in participant.iteritems():
                participants[attr].append(val)
                participants["Incident"] = incident_id
            participant = {}
        pair = child.text.split(":")
        attr = pair[0].strip().lower().replace(" ", "_")
        val = pair[1].strip()
        participant[attr] = val

def scrape_characteristics(div):
    characteristics = []
    for child in div.find_all("li"):
        characteristics.append(child.text)
    incidents["Characteristics"].append(characteristics)

def scrape_notes(div):
    print div.text 

def scrape_district(div):
    pass

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
            #if h2.text == "District":
            #    scrape_district(div)

if __name__ == "__main__":
    scrape()

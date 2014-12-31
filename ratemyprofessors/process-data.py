import csv
import dateutil.parser
import json
import numpy as np
import os
import os.path

PROFESSORS_DIR = "data/professors"
RATINGS_DIR = "data/ratings"
TOP_COLLEGES = "top-colleges.txt"
RATINGS_THRESH = 7
MALE_WORDS = ["he", "him", "his", "himself"]
FEMALE_WORDS = ["she", "her", "hers", "herself"]
OUTPUT = "data.csv"

school_list = None
with open(TOP_COLLEGES) as top_colleges:
    school_list = [line.strip() for line in top_colleges.readlines()]
school_list = [s.lower() for s in school_list]



def fetch_ratings(tid):
    npages = 1
    remaining = True
    ratings = []
    while True:
        fn = "%s-page%03d.json" % (tid, npages)
        fn = os.path.join(RATINGS_DIR, fn)
        print fn
        try:
            fp = open(fn, "r")
            data = json.load(fp)
            remaining = int(data["remaining"]) > 0
            ratings.extend(data["ratings"])
            fp.close()
        except IOError as e:
            break
        npages += 1
    if remaining:
        print "ERROR: Did not download all ratings for %s" % tid
    return ratings



def write_data(prof, ratings, out):
    if len(ratings) < RATINGS_THRESH:
        print "ERROR: Not enough ratings."
        return

    id = prof["tid"] 
    avg_clarity = np.mean([r["rClarity"] for r in ratings])
    avg_easy = np.mean([r["rEasy"] for r in ratings])
    avg_helpful = np.mean([r["rHelpful"] for r in ratings])
    avg_status = np.mean([r["rStatus"] for r in ratings])

    gender, nfemale, nmale = detect_gender(ratings)
    earliest_rating = lookup_earliest(ratings)
    latest_rating = lookup_latest(ratings)

    department = prof["tDept"].encode("utf8")
    institution = prof["institution_name"].encode("utf8")
    first_name = prof["tFname"].encode("utf8")
    last_name = prof["tLname"].encode("utf8")
    num_ratings = prof["tNumRatings"]
    rating_class = prof["rating_class"].encode("utf8")
    overall_ratings = prof["overall_rating"].encode("utf8")
    
    row = [id, avg_clarity, avg_easy, avg_helpful, avg_status,
        gender, nfemale, nmale, earliest_rating, latest_rating,
        department, institution, first_name, last_name, 
        num_ratings, rating_class, overall_ratings]
    out.writerow(row)



def lookup_earliest(ratings):
    times = [r["rDate"] for r in ratings]
    times = [dateutil.parser.parse(t) for t in times]
    return min(times)



def lookup_latest(ratings):
    times = [r["rDate"] for r in ratings]
    times = [dateutil.parser.parse(t) for t in times]
    return max(times)



def detect_gender(ratings):
    comments = [r["rComments"] for r in ratings]
    nmale = 0
    nfemale = 0
    for comment in comments:
        for word in comment.strip().split():
            word = word.lower()
            if word in MALE_WORDS:
                nmale += 1
            if word in FEMALE_WORDS:
                nfemale += 1
    if nmale > 0 and nfemale > 0:
        print "WARNING: Ambiguous gender: %d female words and %d male words for %d." % (nfemale, nmale, tid)
    if nmale == 0 and nfemale == 0:
        return "UNKNOWN", nfemale, nmale
    if nmale > nfemale:
        return "MALE", nfemale, nmale
    if nfemale >= nmale:
        return "FEMALE", nfemale, nmale



schools_seen = set()
nprofs = nfiles = 0
out = open(OUTPUT, "w")
writer = csv.writer(out)
count = 0
for fsitem in os.listdir(PROFESSORS_DIR):
    fsitem = os.path.join(PROFESSORS_DIR, fsitem)
    if not os.path.isfile(fsitem): continue
    with open(fsitem) as prof_list_file:
        data = json.load(prof_list_file)
        for prof in data["professors"]:
            tid = prof["tid"]
            institution = prof["institution_name"].lower()
            institution = institution.replace("st.", "saint") # special case hack
            nratings = prof["tNumRatings"]
            if institution in school_list and nratings > RATINGS_THRESH:
                schools_seen.add(institution)
                nprofs += 1
                ratings = fetch_ratings(tid)
                if len(ratings) > 0:
                    write_data(prof, ratings, writer)
                    count += 1
                #if count > 100: exit()
        nfiles += 1
        print "Processed %d files" % nfiles
out.close()

not_seen = set(school_list).difference(schools_seen)
print not_seen
print "%d qualifying professors" % nprofs
print "%d qualifying schools" % len(schools_seen)

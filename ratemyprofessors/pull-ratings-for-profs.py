import json
import os
import os.path
import time
import urllib2

TOP_COLLEGES = "top-colleges.txt"
school_list = None
with open(TOP_COLLEGES) as top_colleges:
    school_list = [line.strip() for line in top_colleges.readlines()]
school_list = [s.lower() for s in school_list]
 
PROFESSOR_LISTS = "data/professors"
RATING_QUERY_URL = "http://www.ratemyprofessors.com/paginate/professors/ratings?tid=%s&page=%d"
RATINGS_THRESH = 7 # Highest number of ratings such that profs from all schools are still represented

def fetch_ratings(tid):
    page = 1
    while True:
        query = RATING_QUERY_URL % (tid, page)
        results_filename = "data/ratings/%s-page%03d.json" % (tid, page)
        if os.path.isfile(results_filename): continue # Already exists
        time.sleep(2)
        results = urllib2.urlopen(query).read()
        with open(results_filename, "w") as results_file:
            results_file.write(results)
        results = json.loads(results)
        remaining = int(results["remaining"])
        if remaining == 0: break
        page += 1

nprofs = 0
schools_seen = set()
nfiles = 0
for fsitem in os.listdir(PROFESSOR_LISTS):
    fsitem = os.path.join(PROFESSOR_LISTS, fsitem)
    if not os.path.isfile(fsitem): continue
    with open(fsitem) as prof_list_file:
        data = json.load(prof_list_file)
        for prof in data["professors"]:
            tid = prof["tid"]
            institution = prof["institution_name"].lower()
            institution = institution.replace("st.", "saint") # special case hack
            rating_class = prof["rating_class"]
            nratings = prof["tNumRatings"]
            if institution in school_list 
                and rating_class == "good" 
                and nratings > RATINGS_THRESH:
                schools_seen.add(institution)
                nprofs += 1
            ratings = fetch_ratings(tid)
        nfiles += 1
        print "Processed %d files" % nfiles

not_seen = set(school_list).difference(schools_seen)
print not_seen
print "%d qualifying professors" % nprofs
print "%d qualifying schools" % len(schools_seen)

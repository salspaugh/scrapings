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
RATINGS_THRESH = 7 
SLEEP = 1

def fetch_ratings(tid):
    page = 1
    while True:
        query = RATING_QUERY_URL % (tid, page)
        results_filename = "data/ratings/%s-page%03d.json" % (tid, page)
        if os.path.isfile(results_filename): # Already exists
            page += 1
            continue 
        results = urllib2.urlopen(query).read()
        rdict = json.loads(results)
        nratings = len(rdict["ratings"])
        if nratings == 0: break
        with open(results_filename, "w") as results_file:
            results_file.write(results)
        print "Wrote page %d for tid %s" % (page, tid)
        time.sleep(SLEEP)
        rdict = json.loads(results)
        remaining = int(rdict["remaining"])
        if remaining == 0: break
        page += 1

processed_file = open("processed-prof-lists.txt", "r")
processed = [f.strip() for f in processed_file.readlines()]
processed_file.close()

processed_file = open("processed-prof-lists.txt", "a")
nprofs = 0
schools_seen = set()
nfiles = len(processed)
for fsitem in os.listdir(PROFESSOR_LISTS):
    fsitem = os.path.join(PROFESSOR_LISTS, fsitem)
    if not os.path.isfile(fsitem): continue
    #if fsitem in processed: continue
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
                fetch_ratings(tid)
        nfiles += 1
        processed_file.write(fsitem)
        processed_file.write("\n")
        processed_file.flush()
        print "Processed %d files" % nfiles
processed_file.close()

not_seen = set(school_list).difference(schools_seen)
print not_seen
print "%d qualifying professors" % nprofs
print "%d qualifying schools" % len(schools_seen)

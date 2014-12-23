import json
import os
import os.path

PROFESSORS_DIR = "data/professors"
RATINGS_DIR = "data/ratings"
TOP_COLLEGES = "top-colleges.txt"

school_list = None
with open(TOP_COLLEGES) as top_colleges:
    school_list = [line.strip() for line in top_colleges.readlines()]
school_list = [s.lower() for s in school_list]

def fetch_ratings(tid):
    pass

def write_data(prof, ratings, out):
    pass 

schools_seen = set()
nprofs = nfiles = 0
for fsitem in os.listdir(PROFESSOR_DIR):
    fsitem = os.path.join(PROFESSOR_DIR, fsitem)
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
                write_data(prof, ratings)
        nfiles += 1
        print "Processed %d files" % nfiles

not_seen = set(school_list).difference(schools_seen)
print not_seen
print "%d qualifying professors" % nprofs
print "%d qualifying schools" % len(schools_seen)

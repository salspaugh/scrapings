import json
import time
import urllib2

TOP_COLLEGES = "top-colleges.txt"
SCHOOL_QUERY_URL = "http://www.ratemyprofessors.com/find/professor/?institution=%s&page=%d&queryoption=TEACHER&queryBy=schoolDetails"
school_list = None
with open(TOP_COLLEGES) as top_colleges:
    school_list = [line.strip() for line in top_colleges.readlines()]

ut_austin = school_list.index("University of Texas")
for school in school_list[ut_austin:]:
    school_url = school.replace(" ", "+")
    school_file = school.replace(" ", "-").replace("(", "-").replace(")", "-")
    if school == "University of Texas":
        page = 552
    else:    
        page = 1
    while True:
        query = SCHOOL_QUERY_URL % (school_url, page)
        results = urllib2.urlopen(query).read()
        results_filename = "data/%s-page%03d.json" % (school_file, page)
        with open(results_filename, "w") as results_file:
            results_file.write(results)
            print "Wrote page %d" % page
        results = json.loads(results)
        remaining = int(results["remaining"])
        if remaining == 0: break
        page += 1
        time.sleep(2)
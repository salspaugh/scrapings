import bs4
import urllib2

# Read in list of "top 100 colleges".
FORBES_TOP_COLLEGES = "http://www.forbes.com/top-colleges/list/"
page = urllib2.urlopen(FORBES_TOP_COLLEGES).read()
soup = bs4.BeautifulSoup(page)
for tr in soup.find_all("tr"):
    h3 = tr.h3
    if h3 is not None:
        print h3.get_text().encode("utf-8")

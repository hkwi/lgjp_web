import io
import csv
import lgjp_web.wd
import difflib
try:
	from urllib.request import urlopen
	from urllib.parse import urlparse
except:
	from urllib import urlopen
	from urlparse import urlparse

remote = "https://github.com/code4fukui/localgovjp/raw/master/localgovjp-utf8.csv"
base = []
for r in csv.DictReader(io.TextIOWrapper(urlopen(remote))):
	name = r["city"]
	city_pair = name.split()
	if len(city_pair) > 1:
		name = city_pair[1]
	base.append("%s,%s" % (name, r["url"]))
	
ex = ["%s,%s" % (name.value, str(site))
	for qname, code, name, site in lgjp_web.wd.info if code[2:5] != "000"]
with open("docs/codeforfukui.diff","w") as w:
	for l in difflib.unified_diff(base, ex, fromfile="codeforfukui", tofile="wikidata"):
		w.write(l)
		if not l.endswith("\n"):
			w.write("\n")

base = []
for r in csv.DictReader(io.TextIOWrapper(urlopen(remote))):
	name = r["city"]
	city_pair = name.split()
	if len(city_pair) > 1:
		name = city_pair[1]
	base.append("%s,%s" % (name, urlparse(r["url"]).netloc))

ex = []
for qname, code, name, site in lgjp_web.wd.info:
	if code[2:5] == "000":
		continue
	
	netloc = None
	if site:
		netloc = urlparse(str(site)).netloc
	ex.append("%s,%s" % (name.value, netloc))

with open("docs/codeforfukui_dns.diff","w") as w:
	for l in difflib.unified_diff(base, ex, fromfile="codeforfukui", tofile="wikidata"):
		w.write(l)
		if not l.endswith("\n"):
			w.write("\n")


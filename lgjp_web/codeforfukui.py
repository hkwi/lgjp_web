import io
import csv
import lgjp_web.wd
import difflib
try:
	from urllib.request import urlopen
except:
	from urllib import urlopen

remote = "https://raw.githubusercontent.com/codeforfukui/localgovjp/gh-pages/localgovjp-utf8.csv"
base = []
for r in csv.DictReader(io.TextIOWrapper(urlopen(remote))):
	city_pair = r["city"].split()
	if len(city_pair) > 1:
		base.append("%s,%s" % (city_pair[1], r["url"]))
	else:
		base.append("%s,%s" % (r["city"], r["url"]))
	
ex = ["%s,%s" % (name.value, str(site))
	for code, name, site in lgjp_web.wd.info if code[2:5] != "000"]
with open("docs/codeforfukui.diff","w") as w:
	for l in difflib.unified_diff(base, ex, fromfile="codeforfukui", tofile="wikidata"):
		w.write(l)
		if not l.endswith("\n"):
			w.write("\n")

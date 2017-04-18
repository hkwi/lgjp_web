import io
import csv
import lgjp_web.wd
import difflib
try:
	from urllib.request import urlopen
except:
	from urllib import urlopen

remote = "https://raw.githubusercontent.com/codeforfukui/localgovjp/gh-pages/localgovjp-utf8.csv"
base = ["%s,%s" % (r["city"],r["url"])
	for r in csv.DictReader(io.TextIOWrapper(urlopen(remote)))]
ex = ["%s,%s" % (name.value, str(site))
	for code, name, site in lgjp_web.wd.info if code[2:5] != "000"]
with open("docs/codeforfukui.diff","w") as w:
	for l in difflib.unified_diff(base, ex, fromfile="codeforfukui", tofile="wikidata"):
		w.write(l)
		if not l.endswith("\n"):
			w.write("\n")

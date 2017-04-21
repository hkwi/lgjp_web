# coding: UTF-8
# Dbpedia
import rdflib
import lgjp_web.wd
import difflib

g = rdflib.ConjunctiveGraph(store="SPARQLStore")
g.store.endpoint = "http://ja.dbpedia.org/sparql"
info = g.query('''
SELECT ?code,?name,?homepage WHERE {
 ?s <http://dbpedia.org/ontology/areaCode> ?code ;
  <http://ja.dbpedia.org/property/name> ?name .
 OPTIONAL {
  ?s <http://xmlns.com/foaf/0.1/homepage> ?homepage .
 }
 FILTER regex(?code, "[0-9]{5}-[0-9]")
}
ORDER BY ?code
''')
base = []
for code,name,homepage in info:
	base.append("%s,%s" % (code[:5]+code[6:], homepage))

ex = []
for code, name, site in lgjp_web.wd.info:
	if code[2:5] == "000":
		continue
	
	ex.append("%s,%s" % (code.value, site))

with open("docs/dbpedia.diff","w") as w:
	for l in difflib.unified_diff(base, ex, fromfile="dbpedia", tofile="wikidata"):
		w.write(l)
		if not l.endswith("\n"):
			w.write("\n")

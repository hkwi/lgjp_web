import rdflib
import time
t = time.time()

from rdflib.namespace import DCTERMS
JITIS = rdflib.Namespace("http://hkwi.github.com/denshijiti/terms#")
IC = rdflib.Namespace("http://imi.ipa.go.jp/ns/core/rdf#")

jiti = rdflib.Graph()
jiti.load("https://hkwi.github.io/denshijiti/code.ttl", format="turtle")

cs, = next(iter(jiti.query('''
PREFIX jitis: <http://hkwi.github.com/denshijiti/terms#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?cs WHERE {
    ?cs a jitis:CodeSet ;
        dcterms:issued ?d .
}
ORDER BY DESC(?d) LIMIT 1
''')))

info = []
for s in jiti.objects(cs, DCTERMS.hasPart):
	code = jiti.value(s, JITIS["code"])
	if code[2:5]=="000":
		continue
	
	ret = dict(code=code)
	for k,k2 in zip(("ken","si","ku"),("都道府県", "市区町村", "区")):
		o = jiti.value(s, IC[k2])
		if o:
			ret[k] = o
	info.append(ret)


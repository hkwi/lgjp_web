import os.path
import concurrent.futures
import logging
import requests
import rdflib
import datetime
import itertools

from rdflib.namespace import RDF, XSD, DCTERMS, FOAF, RDFS, SKOS
JITI = rdflib.Namespace("http://hkwi.github.com/denshijiti/#")
JITIS = rdflib.Namespace("http://hkwi.github.com/denshijiti/terms#")
IC = rdflib.Namespace("http://imi.ipa.go.jp/ns/core/rdf#")
LGW = rdflib.Namespace("http://hkwi.github.com/lgjp_web/#")
LGWS = rdflib.Namespace("http://hkwi.github.com/lgjp_web/terms#")

def use_ns(g):
	ns = dict(
		dcterms=DCTERMS,
		xsd=XSD,
		rdfs=RDFS,
		foaf=FOAF,
		ic=IC,
		jiti=JITI,
		jitis=JITIS,
		lgw=LGW,
		lgws=LGWS,
	)
	for k,v in ns.items():
		g.bind(k,v)

def build(fn):
	g = rdflib.Graph()
	use_ns(g)
	
	base = rdflib.Graph()
	base.load(fn, format="turtle")
	use_ns(base)
	
	jiti = rdflib.Graph()
	jiti.load("https://hkwi.github.io/denshijiti/code.ttl", format="turtle")
	use_ns(jiti)
	
	q = '''
	SELECT ?d WHERE {
	    ?cs a jitis:CodeSet ;
	        dcterms:issued ?d .
	}
	ORDER BY DESC(?d) LIMIT 1
	'''
	for dt, in jiti.query(q):
		break
	
	q = '''
	SELECT ?s ?c ?p ?n ?k WHERE {
	    ?s a jitis:StandardAreaCode ;
	        ic:都道府県 ?p ;
	        ic:市区町村 ?n ;
	        jitis:code ?c .
	    ?cs a jitis:CodeSet ;
	        dcterms:issued "%s"^^xsd:date ;
	        dcterms:hasPart ?s .
	    OPTIONAL {
	        ?s ic:区 ?k .
	        FILTER (LANG(?k) = "ja")
	    }
	}
	ORDER BY ASC(?c)
	''' % dt
	for s,c,p,n,k in jiti.query(q):
		z = rdflib.BNode(c)
		g.add((z, SKOS["closeMatch"], s))
		g.add((z, DCTERMS["identifier"], rdflib.Literal(c[:5])))
		g.add((z, JITIS["code"], c))
		g.add((z, IC["都道府県"], p))
		g.add((z, IC["市区町村"], n))
		if k:
			g.add((z, IC["区"], k))
		
		url = None
		q = '''
		SELECT ?L WHERE {
			?s jitis:code "%s" ;
				foaf:homepage ?L .
		}
		''' % c
		for l, in base.query(q):
			url = l
		
		if url:
			g.add((z, FOAF["homepage"], url))
	
	return g

def scan_url(urls, hb):
	base = rdflib.Graph()
	use_ns(base)
	base.load(urls, format="turtle")
	if hb and os.path.exists(hb):
		base.load(hb, format="turtle")
	
	g = rdflib.Graph()
	use_ns(g)
	if hb and os.path.exists(hb):
		g.load(hb, format="turtle")
	
	q1 = '''
	SELECT ?c ?L WHERE {
		?s1 jitis:code ?c ;
			foaf:homepage ?L .
		FILTER NOT EXISTS {
			?s a lgws:Poll ;
				jitis:code ?c ;
				lgws:tm ?tm .
		}
	}
	LIMIT 200
	'''
	
	q2 = '''
	SELECT ?c ?L WHERE {
		?s1 jitis:code ?c ;
			foaf:homepage ?L .
		?s a lgws:Poll ;
			jitis:code ?c ;
			lgws:tm ?tm .
	}
	ORDER BY ASC(?tm) LIMIT 200
	'''
	err = {}
	with concurrent.futures.ThreadPoolExecutor(max_workers=4) as wks:
		i = 0
		for c,L in itertools.chain(base.query(q1), base.query(q2)):
			if i > 200:
				break
			
			i += 1
			s = LGW[c]
			for p,v in g.query("SELECT ?p ?v WHERE { <%s> ?p ?v . }" % s):
				g.remove((s,p,v))
			
			dti = int(datetime.datetime.now().timestamp())
			g.add((s, LGWS["tm"], rdflib.Literal(str(dti), datatype=XSD.integer)))
			g.add((s, RDF.type, LGWS["Poll"]))
			g.add((s, JITIS["code"], c))
			info, se = poll_url(L)
			for k,v in info.items():
				if k=="land":
					g.add((s, LGWS[k], rdflib.URIRef(v)))
				else:
					g.add((s, LGWS[k], rdflib.Literal(v)))
			
			if se:
				err[L] = se
				logstr = "%s %s" % (L, repr(se))
				logging.error(logstr)
	
	return g, err

def poll_url(url):
	err_hist = []
	obj = dict()
	for method in ("head", "get"):
		func = getattr(requests, method)
		try:
			o = func(url)
		except Exception as e:
			err_hist.append("%s %s" % (method, repr(e)))
			continue
		
		if o.status_code != 200:
			err_hist.append("%s %d" % (method, o.status_code))
			continue
		
		obj["land"] = o.url
		for k in ("etag", "last-modified"):
			v = o.headers.get(k)
			if v:
				obj[k] = v
		
		return obj, None
	
	return obj, err_hist

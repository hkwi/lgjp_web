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

def scan_url(urls):
	base = rdflib.Graph()
	use_ns(base)
	base.load(urls, format="turtle")
	
	g = rdflib.Graph()
	use_ns(g)
	q = '''
	SELECT ?c ?L WHERE {
		?s jitis:code ?c ;
			foaf:homepage ?L .
	}
	'''
	def proc(args):
		c,L = args
		
		s = LGW[c]
		dts = datetime.datetime.now().isoformat()
		g.add((s, LGWS["tm"], rdflib.Literal(dts, datatype=XSD.datetime)))
		g.add((s, RDF.type, LGWS["Poll"]))
		g.add((s, JITIS["code"], c))
		info, els = poll_url(L)
		for k,v in info.items():
			if k=="land":
				g.add((s, LGWS[k], rdflib.URIRef(v)))
			else:
				g.add((s, LGWS[k], rdflib.Literal(v)))
		
		for err in els:
			logging.error("code=%s url=%s" % (c,L))
			g.add((s, LGWS["fail"], rdflib.Literal(err)))
	
	with concurrent.futures.ThreadPoolExecutor(max_workers=4) as wks:
		[None for z in wks.map(proc, base.query(q))]
	
	return g

def poll_url(url):
	err_hist = []
	obj = dict()
	for method in ("head", "get"):
		func = getattr(requests, method)
		try:
			o = func(url, timeout=2.0)
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
		
		return obj, []
	
	return obj, err_hist

import os
import csv
import json
import logging
import socket
import unittest
import concurrent.futures
import requests
import requests.exceptions
import yaml
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen

class TestDataSet(unittest.TestCase):
	def test_codeset(self):
		'''
		tests that code set is synced with denshijiti
		'''
		import lgjp_web.wd
		import lgjp_web.base
		base = set([r["code"].value for r in lgjp_web.base.info])
		ex = set([code.value for code, name, site in lgjp_web.wd.info if code[2:5] != "000"])
		assert base==ex, repr([base-ex, ex-base])
	
	def test_codeforfukui(self):
		import lgjp_web.codeforfukui
	
	def test_dbpedia(self):
		import lgjp_web.dbpedia

class TestAccess(unittest.TestCase):
	def dns_o_http(self, host):
		q = urlencode(dict(name=host, type="A"))
		f = urlopen("https://dns.google.com/resolve?%s" % q)
		data = f.read().decode("UTF-8")
		assert json.loads(data)["Status"] == 0, data
	
	def test_dns(self):
		import lgjp_web.wd
		def func(arg):
			code, name, site = arg
			host = urlparse(site).netloc
			try:
				socket.gethostbyname(host)
			except Exception as e:
				try:
					self.dns_o_http(host)
				except:
					return [code, name, site, e]

		p = concurrent.futures.ThreadPoolExecutor(10)
		r = p.map(func, lgjp_web.wd.info)
		errors = [x for x in r if x]
		if errors:
			raise Exception(repr(errors))

	@unittest.skipUnless(os.environ.get("FULLSCAN") , "heavy")
	def test_fullscan(self):
		import rdflib
		g = rdflib.ConjunctiveGraph(store="SPARQLStore")
		g.store.endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
		info = g.query('''
		SELECT ?s ?name ?site WHERE {
		 ?s wdt:P429 ?code ; # 全国地方公共団体コード
		    rdfs:label ?name .
		  OPTIONAL {
		    ?s p:P856 ?stmt .
		    ?stmt ps:P856 ?site . # 公式サイト
		    FILTER NOT EXISTS { ?stmt pq:P642 ?x } # ～についての
		    FILTER NOT EXISTS { ?stmt pq:P582 ?y } # 終了日
		  }
		 FILTER ( lang(?name)="ja" )
		 FILTER NOT EXISTS { ?s wdt:P31 wd:Q18663566 } # 分類 日本の廃止市町村
		 FILTER NOT EXISTS { ?s wdt:P31 wd:Q850450 } # 分類 支庁
		} ORDER BY ?code ?site
		''')
		
		def func(arg):
			qname, name, site = arg
			
			info = {"qname": str(qname), "site": str(site), "hint": []}
			try:
				r = requests.get(str(site), timeout=30) # HEAD does not work
				assert r.ok, r.reason
				info["land"] = r.url
				
				a = urlparse(site)
				b = urlparse(r.url)
				
				if a.netloc != b.netloc:
					info["hint"] += ["MOVE"]
				
				if a.scheme=="http" and b.scheme=="https":
					info["hint"] += ["HTTPS"]
				elif a.scheme=="https" and b.scheme=="http":
					info["hint"] += ["HTTP"]
				elif a.scheme != b.scheme:
					info["hint"] += ["SCHEME"]
			except requests.exceptions.SSLError as e:
				info["hint"] += ["SSL"]
				info["reason"] = e
			except Exception as e:
				info["hint"] += ["ERROR"]
				info["reason"] = e
			
			if info["hint"]:
				print(info)
			
			return info
		
		p = concurrent.futures.ThreadPoolExecutor(10)
		r = list(p.map(func, info))
		
		keys = "MOVE HTTPS HTTP SCHEME SSL ERROR".split()
		errors = {}
		for key in keys:
			errors[key] = [
				{k:v for k,v in x.items() if k not in ("hint",)}
				for x in r if key in x["hint"]
			]
		
		if errors:
			raise Exception(yaml.dump(errors))

if __name__=="__main__":
	unittest.main()

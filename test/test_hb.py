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
from selenium import webdriver

class TestDataSet(unittest.TestCase):
	def test_codeset(self):
		'''
		tests that code set is synced with denshijiti
		'''
		import lgjp_web.wd
		import lgjp_web.base
		base = set([r["code"].value for r in lgjp_web.base.info])
		ex = set([r.code.value for r in lgjp_web.wd.info if r.code[2:5] != "000"])
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
			code, name, site = arg.code, arg.name, arg.site
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
		import lgjp_web.wd
		info = lgjp_web.wd.info
		
		web = None
		if os.environ.get("USE_BROWSER"):
			# It would take about 2 hours
			# chrome driver options were taken from ember-cli
			# https://github.com/ember-cli/ember-cli/blob/master/blueprints/app/files/testem.js
			opts = webdriver.ChromeOptions()
			opts.add_argument('--no-sandbox')
			opts.add_argument('--headless')
			opts.add_argument('--disable-dev-shm-usage')
			opts.add_argument('--disable-software-rasterizer')
			opts.add_argument('--mute-audio')
			opts.add_argument('--window-size=1440,900')
			web = webdriver.Chrome(options=opts)
		
		def func(arg):
			qname, name, site = arg.s, arg.name, arg.site
			
			info = {"qname": str(qname), "site": str(site), "hint": []}
			try:
				if web:
					web.get(str(site))
					land_url = web.current_url
				else:
					r = requests.get(str(site), timeout=30) # HEAD does not work
					assert r.ok, r.reason
					land_url = r.url
				
				info["land"] = land_url
				a = urlparse(site)
				b = urlparse(land_url)
				
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
				info["reason"] = str(e)
			
			if info["hint"]:
				print(info)
			
			return info
		
		if web:
			r = [func(arg) for arg in info]
		else:
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

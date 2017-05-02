import os
import csv
import json
import logging
import socket
import unittest
import concurrent.futures
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

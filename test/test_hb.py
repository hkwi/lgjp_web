import os
import csv
import logging
import socket
import unittest
from urllib.parse import urlparse

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
	def test_dns(self):
		import lgjp_web.wd
		errors = []
		for code, name, site in lgjp_web.wd.info:
			host = urlparse(site).netloc
			try:
				socket.gethostbyname(host)
			except Exception as e:
				errors.append([code, name, site, e])
		
		if errors:
			raise Exception(repr(errors))

import os
import logging
import unittest
import lgjp_web

class TestHeartBeat(unittest.TestCase):
	def test_base(self):
		g = lgjp_web.build("docs/urls.ttl")
		q = '''
		SELECT ?c WHERE {
			?s jitis:code ?c .
			FILTER NOT EXISTS {
				?s foaf:homepage ?v .
			}
		}
		'''
		c = list(g.query(q))
		with open("docs/urls.ttl", "wb") as w:
			g.serialize(destination=w, format="turtle")
		
		assert not c, repr(c)
	
	@unittest.skipIf(os.environ.get("TRAVIS"))
	def test_hb(self):
		g = lgjp_web.scan_url("docs/urls.ttl")
		with open("docs/hb.ttl","wb") as w:
			g.serialize(destination=w, format="turtle")

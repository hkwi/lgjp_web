import logging
import unittest
import lgjp_web

class TestHeartBeat(unittest.TestCase):
	def test_hb(self):
		g = lgjp_web.build("docs/urls.ttl")
		with open("docs/urls.ttl", "wb") as w:
			g.serialize(destination=w, format="turtle")
		
		g2 = lgjp_web.scan_url(g)
		with open("docs/hb.ttl","wb") as w:
			g2.serialize(destination=w, format="turtle")

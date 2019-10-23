# coding: UTF-8
# Wikidata to CSV
import rdflib
import csv

g = rdflib.ConjunctiveGraph(store="SPARQLStore")
# https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service
g.store.endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
# https://meta.wikimedia.org/wiki/User-Agent_policy
g.store.agent = "https://github.com/hkwi/lgjp_web"

info = g.query('''
SELECT ?s ?code ?name ?site WHERE {
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
with open("docs/wd.csv","w", encoding="UTF-8") as f:
	csv.writer(f).writerows([
		[r[x] for x in "code name site".split()]
		for r in info])

# How to update the official website:
# - If the item has a new site, add an additional statement with preferred rank. 
#   How to set preferred rank? See Help:Ranking#How_to_apply_ranks.
# - If a website is no longer valid, you could also:
#     qualify the URL with 終了日 (P582). If you don't know the exact date, use the year or "unknown" as date 
#     add the qualifier アーカイブURL (P1065) to link to the former website at web.archive.org
# - Do not delete or replace the former URL.

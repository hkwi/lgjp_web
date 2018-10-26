# coding: UTF-8
# Wikidata to CSV
import rdflib

g = rdflib.ConjunctiveGraph(store="SPARQLStore")
g.store.endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
info = g.query('''
SELECT ?code ?name ?site WHERE {
 ?s wdt:P429 ?code ; # 全国地方公共団体コード
    rdfs:label ?name .
  OPTIONAL {
    ?s wdt:P856 ?site . # 公式サイト
  }
 FILTER ( lang(?name)="ja" )
 FILTER NOT EXISTS { ?s wdt:P31 wd:Q18663566 } # 分類 日本の廃止市町村
 FILTER NOT EXISTS { ?s wdt:P31 wd:Q850450 } # 分類 支庁
} ORDER BY ?code ?site
''')
open("docs/wd.csv","w").write(info.serialize(format="csv").decode("UTF-8"))

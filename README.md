自治体のホームページの一覧を Wikidata から自動ビルドしています。[CSV](https://hkwi.github.io/lgjp_web/wd.csv)を使うのが手っ取り早いです。
[![Build Status](https://travis-ci.org/hkwi/lgjp_web.svg?branch=master)](https://travis-ci.org/hkwi/lgjp_web)

自治体一覧は[全国地方自治体コード](https://github.com/hkwi/denshijiti)と比較して検査しています。

Wikidata から[直接クエリー](https://query.wikidata.org/#SELECT%20%3Fcode%20%3Fname%20%3Fsite%20WHERE%20%7B%0A%20%3Fs%20wdt%3AP429%20%3Fcode%20%3B%20%23%20%E5%85%A8%E5%9B%BD%E5%9C%B0%E6%96%B9%E5%85%AC%E5%85%B1%E5%9B%A3%E4%BD%93%E3%82%B3%E3%83%BC%E3%83%89%0A%20%20%20%20rdfs%3Alabel%20%3Fname%20.%0A%20%20OPTIONAL%20%7B%0A%20%20%20%20%3Fs%20p%3AP856%20%3Fstmt%20.%0A%20%20%20%20%3Fstmt%20ps%3AP856%20%3Fsite%20.%20%23%20%E5%85%AC%E5%BC%8F%E3%82%B5%E3%82%A4%E3%83%88%0A%20%20%7D%0A%20FILTER%20%28%20lang%28%3Fname%29%3D%22ja%22%20%29%0A%20FILTER%20NOT%20EXISTS%20%7B%20%3Fs%20wdt%3AP31%20wd%3AQ18663566%20%7D%20%23%20%E5%88%86%E9%A1%9E%20%E6%97%A5%E6%9C%AC%E3%81%AE%E5%BB%83%E6%AD%A2%E5%B8%82%E7%94%BA%E6%9D%91%0A%20FILTER%20NOT%20EXISTS%20%7B%20%3Fs%20wdt%3AP31%20wd%3AQ850450%20%7D%20%23%20%E5%88%86%E9%A1%9E%20%E6%94%AF%E5%BA%81%0A%20FILTER%20NOT%20EXISTS%20%7B%20%3Fstmt%20pq%3AP642%20%3Fx%20%7D%20%23%20%EF%BD%9E%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6%E3%81%AE%0A%7D%20ORDER%20BY%20%3Fcode%20%3Fsite)することもできます。

```
SELECT ?code ?name ?site WHERE {
 ?s wdt:P429 ?code ; # 全国地方公共団体コード
    rdfs:label ?name .
  OPTIONAL {
    ?s p:P856 ?stmt .
    ?stmt ps:P856 ?site . # 公式サイト
  }
 FILTER ( lang(?name)="ja" )
 FILTER NOT EXISTS { ?s wdt:P31 wd:Q18663566 } # 分類 日本の廃止市町村
 FILTER NOT EXISTS { ?s wdt:P31 wd:Q850450 } # 分類 支庁
 FILTER NOT EXISTS { ?stmt pq:P642 ?x } # ～についての
} ORDER BY ?code ?site
```

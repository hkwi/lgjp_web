---
# You don't need to edit this file, it's empty on purpose.
# Edit theme's home layout instead if you wanna make some changes
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
layout: home
---

<ul id="lgs"></ul>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.8.0/d3.min.js"></script>
<script>
var lgs = d3.select("#lgs");
d3.csv("wd.csv", function(err,data){
	var ken = "";
	var shi = "";
	data.forEach(function(d){
		ename = d.name.substr(-1);
		var name = ken + " " + d.name;
		if(d.code.substr(2, 3)=="000"){
			name = d.name;
		}else if(ken.substr(-1)=="都") {
			name = ken + " " + d.name;
		}else if(ename == "区"){
			name = ken + " " + shi + " " + d.name;
		}
		
		lgs.append("li").text(d.code + " : ").append("a").attr("href", d.site).text(name);
		
		if(d.code.substr(2, 3)=="000"){
			ken = d.name;
		} else if(ename == "市"){
			shi = d.name;
		}
	});
});
</script>

# 説明

wikidata をデータベースとして、全国地方自治体ウェブサイト一覧を自動観測しています。
ウェブサイトは、メンテナンスなどで一時的にアクセスできないこともあります。

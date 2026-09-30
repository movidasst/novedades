#!/usr/bin/env python3
import json, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FEEDS=json.loads((ROOT/"data/feeds.json").read_text(encoding="utf-8"))["feeds"]
OUT=ROOT/"data/updates.json"
try:
    previous={x["id"]:x for x in json.loads(OUT.read_text(encoding="utf-8")).get("items",[])}
except Exception:
    previous={}

def txt(node,tag):
    el=node.find(tag)
    return (el.text or "").strip() if el is not None else ""

def candidates(feed):
    sid=str(feed.get("standard_id","")).strip()
    if not sid:
        return [feed["rss"]] if feed.get("rss") else []
    p=sid.zfill(6)
    return [
        f"https://www.iso.org/cms/render/live/es/sites/isoorg/contents/data/standard/{p[:2]}/{p[2:4]}/{sid}.rss",
        f"https://www.iso.org/cms/render/live/en/sites/isoorg/contents/data/standard/{p[:2]}/{p[2:4]}/{sid}.rss",
    ]

def get_xml(feed):
    last=None
    for url in candidates(feed):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"LaMovidaSST-Radar/2.0 (+https://novedades.movidasst.com)"})
            with urllib.request.urlopen(req,timeout=30) as r:
                return r.read(),url
        except Exception as e:
            last=e
    raise last or RuntimeError("Sin RSS")

def parse_date(pub,old=""):
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",pub or ""): return pub
    for fmt in ("%a, %d %b %Y %H:%M:%S %z","%a, %d %b %Y"):
        try:return datetime.strptime(pub,fmt).date().isoformat()
        except Exception: pass
    return old

def fetch(feed):
    xml,rss=get_xml(feed)
    root=ET.fromstring(xml);ch=root.find("channel");it=ch.find("item")
    desc=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",txt(it,"description"))).strip()
    old=previous.get(feed["id"],{})
    m=re.search(r"(?:etapa|stage)\s+([0-9]{2}\.[0-9]{2})",desc,re.I)
    return {
      "id":feed["id"],"reference":feed["reference"],"topic":feed["topic"],"category":feed.get("category","gestion"),
      "stage":m.group(1) if m else old.get("stage",""),
      "pubDate":parse_date(txt(it,"pubDate"),old.get("pubDate","")),
      "title":txt(it,"title") or feed["reference"],
      "description":desc or old.get("description","Actualización disponible en ISO.org."),
      "link":txt(it,"link") or feed["page"],
      "rss":rss
    }

items=[]
for f in FEEDS:
    try:
        items.append(fetch(f));print("OK",f["reference"])
    except Exception as e:
        print("ERROR",f["reference"],e)
        if f["id"] in previous:
            x=previous[f["id"]]
            x["category"]=f.get("category",x.get("category","gestion"))
            items.append(x)

items.sort(key=lambda x:x.get("pubDate",""),reverse=True)
OUT.write_text(json.dumps({"generated_at":datetime.now(timezone.utc).isoformat(),"items":items},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

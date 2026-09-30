#!/usr/bin/env python3
import json, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEEDS = json.loads((ROOT/"data/feeds.json").read_text(encoding="utf-8"))["feeds"]
OUT = ROOT/"data/updates.json"
try:
    previous = {x["id"]: x for x in json.loads(OUT.read_text(encoding="utf-8")).get("items", [])}
except Exception:
    previous = {}

def text(node, tag):
    el = node.find(tag)
    return (el.text or "").strip() if el is not None else ""

def fetch(feed):
    req = urllib.request.Request(feed["rss"], headers={"User-Agent":"LaMovidaSST-Radar/1.0 (+https://novedades.movidasst.com)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        xml = r.read()
    root = ET.fromstring(xml)
    channel = root.find("channel")
    item = channel.find("item")
    title = text(item, "title")
    link = text(item, "link") or feed["page"]
    desc = re.sub(r"<[^>]+>", " ", text(item, "description"))
    desc = re.sub(r"\s+", " ", desc).strip()
    pub = text(item, "pubDate")
    m = re.search(r"(?:etapa|stage)\s+([0-9]{2}\.[0-9]{2})", desc, re.I)
    stage = m.group(1) if m else previous.get(feed["id"],{}).get("stage","")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", pub):
        pub_date = pub
    else:
        try:
            pub_date = datetime.strptime(pub[:16], "%a, %d %b %Y").date().isoformat()
        except Exception:
            pub_date = previous.get(feed["id"],{}).get("pubDate","")
    return {
      "id":feed["id"],"reference":feed["reference"],"topic":feed["topic"],
      "stage":stage,"pubDate":pub_date,"title":title or feed["reference"],
      "description":desc,"link":link
    }

items=[]
for f in FEEDS:
    try:
        items.append(fetch(f))
        print("OK", f["reference"])
    except Exception as e:
        print("ERROR", f["reference"], e)
        old = previous.get(f["id"])
        if old: items.append(old)

items.sort(key=lambda x:x.get("pubDate",""), reverse=True)
payload={"generated_at":datetime.now(timezone.utc).isoformat(),"items":items}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

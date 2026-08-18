import json
import urllib.request
from pathlib import Path

BASE = "http://aurora.thinkfont.com:8081/operate_web/%E8%A1%A8%E7%9B%98%E7%BB%84/"
ROOT = Path(__file__).parent

def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

manifest = get_json(BASE + "xiaomi-ranking-data/manifest.json")
latest = manifest["latestDate"]
payload = get_json(BASE + "xiaomi-ranking-data/" + latest + ".json")
hot = [r for r in payload["rows"] if r.get("position_type") == "热销榜-周榜"]
versions = ["O66", "N67", "P65", "P67"]
summary = []
for version in versions:
    items = sorted([r for r in hot if r.get("vendor_version") == version], key=lambda r: r.get("position_order", 9999))
    s = payload["summary"][version]
    summary.append({
        "version": version,
        "model": s.get("model"),
        "ownedCount": s.get("ownedCount"),
        "paidCount": s.get("paidCount"),
        "avgPrice": s.get("avgPrice"),
        "top10": [{k: row.get(k) for k in ("position_order", "artwork_name", "author", "current_price", "own")} for row in items[:10]],
    })
terms = ["相册", "自定义", "动态", "情绪", "感知", "换图", "机器人", "小狗", "猫", "天气", "数据", "多功能"]
keywords = [{"name": term, "count": sum(1 for row in hot if row.get("position_order", 9999) <= 100 and term in (row.get("artwork_name") or ""))} for term in terms]
result = {"generatedAt": manifest.get("generatedAt"), "latestDate": latest, "source": BASE, "summary": summary, "keywords": keywords}
(ROOT / "xiaomi-watchface-data.js").write_text("window.XIAOMI_WATCHFACE_DATA=" + json.dumps(result, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print("updated", latest)

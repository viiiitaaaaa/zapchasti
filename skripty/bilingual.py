# Двуязычный отчёт: китайский + ниже русский (как в питче WB). Шаги: extract -> (перевод в perevod/zh_*.json) -> build
import re, sys, json, os, hashlib
from bs4 import BeautifulSoup, NavigableString, Tag
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK = {"p","li","td","th","dt","dd","h1","h2","h3","h4","div","table","ul","ol","dl","tr","tbody","thead","figure","figcaption","button","section","main","body"}
LEAFTAGS = {"p","li","td","th","dt","dd","h1","h2","h3","h4","div","button","figcaption","summary"}
CYR = re.compile(r"[А-Яа-яЁё]")
def candidates(soup):
    out = []
    for el in soup.body.find_all(True):
        if el.name not in LEAFTAGS: continue
        if "q" in (el.get("class") or []) or el.find_parent(class_="q"): continue
        if el.get("id") in ("lb",): continue
        if el.find(class_="zh"): continue
        if any(isinstance(d, Tag) and d.name in BLOCK for d in el.descendants): continue
        if not CYR.search(el.get_text()): continue
        out.append(el)
    return out
def inner(el): return el.decode_contents()
def key(s): return hashlib.md5(s.encode()).hexdigest()[:12]
def extract(src, dst):
    soup = BeautifulSoup(open(src, encoding="utf-8").read(), "html.parser")
    segs = {}
    for el in candidates(soup):
        s = inner(el).strip()
        segs[key(s)] = s
    json.dump(segs, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("сегментов:", len(segs), "символов:", sum(len(v) for v in segs.values()))
def build(src, tr_dir, dst):
    tr = {}
    for f in sorted(os.listdir(tr_dir)):
        if f.startswith("zh_") and f.endswith(".json"):
            tr.update(json.load(open(os.path.join(tr_dir, f), encoding="utf-8")))
    soup = BeautifulSoup(open(src, encoding="utf-8").read(), "html.parser")
    miss = 0
    for el in candidates(soup):
        s = inner(el).strip(); k = key(s)
        if k not in tr: miss += 1; continue
        el.clear()
        z = soup.new_tag("span", **{"class": "zh"}); z.append(BeautifulSoup(tr[k], "html.parser"))
        r = soup.new_tag("span", **{"class": "ru"}); r.append(BeautifulSoup(s, "html.parser"))
        el.append(z); el.append(r)
    css = soup.new_tag("style"); css.string = ".zh{display:block}.ru{display:block;margin-top:3px;font-size:.88em;color:var(--mute,#6b7280);font-weight:400;font-style:normal}th .ru,button .ru{font-size:.8em}"
    soup.head.append(css)
    soup.html["lang"] = "zh"
    open(dst, "w", encoding="utf-8").write(str(soup))
    print("без перевода:", miss)
if __name__ == "__main__":
    if sys.argv[1] == "extract": extract(sys.argv[2], sys.argv[3])
    else: build(sys.argv[2], sys.argv[3], sys.argv[4])

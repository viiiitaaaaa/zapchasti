# Китайский перевод главной таблицы (колонки «Где продают», «Вывод», «Доказательство») и сводной таблицы каналов.
# Китайский текст собирает сам make_proverka.py (gde_prodayut.py) и кладёт в perevod/_cells.json и _gen_pairs.json;
# тут он привязывается к готовому русскому html по md5 (как в bilingual.py). Запуск из корня zapchasti после make_proverka.py.
# Пишет skripty/perevod/zh_status.json. Пометки к деталям (note) берёт из старых переводов (_pairs_status.json) и из NOTE_ZH.
import json, hashlib
from bs4 import BeautifulSoup
P = "skripty/perevod/"
cells = json.load(open(P + "_cells.json", encoding="utf-8"))
pairs = json.load(open(P + "_pairs_status.json", encoding="utf-8"))
gen = json.load(open(P + "_gen_pairs.json", encoding="utf-8"))
LAB = {"кандидат": "候选", "много конкурентов": "竞争者多", "по цене рынка": "按市场价可卖", "можем продавать": "可以卖", "не оценить": "无法评估",
       "нет продавцов": "无卖家", "нет номера": "无零件号", "нет в наличии": "无现货", "не проверяли": "未核查"}
NOTE_ZH = {
 "Вместо номера указан размер.": "清单里写的是尺寸，不是零件号。",
 "Только под заказ; только для механики.": "只能订购；仅适用于手动挡。",
}
mute = {}
for ru, zh in pairs.values():
    r = BeautifulSoup(ru, "html.parser").find(class_="mute"); z = BeautifulSoup(zh, "html.parser").find(class_="mute")
    if r and z: mute[r.get_text()] = z.decode_contents()
key = lambda s: hashlib.md5(s.encode()).hexdigest()[:12]
canon = lambda h: BeautifulSoup(h, "html.parser").decode()
genmap = {key(canon(ru)): zh for ru, zh in gen}
PROOF = [("снимок zzap.ru", "zzap.ru截图"), ("открыть zzap.ru", "打开zzap.ru"), ("карточка со снимками", "详情页（含截图）")]
soup = BeautifulSoup(open("otchet_dlya_chzhana.html", encoding="utf-8").read(), "html.parser")
out, miss = {}, []
for tr in soup.select("#tb tr"):
    tds = tr.find_all("td")
    n = tds[0].get_text().strip(); c = cells[n]
    out[key(tds[3].decode_contents().strip())] = c["where_zh"]
    vz = c["verdict_zh"]
    if c["note"]:
        nz = NOTE_ZH.get(c["note"]) or mute.get(c["note"])
        if nz: vz += " " + nz
        else: miss.append((n, c["note"]))
    out[key(tds[4].decode_contents().strip())] = f'<span class="tag {c["cls"]}">{LAB[c["label"]]}</span><br/><span class="mute">{vz}</span>'
    pr = tds[5].decode_contents().strip()
    if pr:
        for a, b in PROOF: pr = pr.replace(a, b)
        out[key(tds[5].decode_contents().strip())] = pr
for td in soup.find_all("td"):
    k = key(td.decode_contents().strip())
    if k in genmap: out[k] = genmap[k]
json.dump(out, open(P + "zh_status.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("ячеек:", len(out), "пометок без перевода:", miss)

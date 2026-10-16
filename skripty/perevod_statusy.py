# Китайский перевод ячеек «Решение» (метка + пометки + данные Ozon): собирается по шаблону из _cells.json и старых переводов пометок.
# Запуск из корня zapchasti после make_proverka.py. Пишет skripty/perevod/zh_status.json
import json, glob, hashlib, os
from bs4 import BeautifulSoup
P = "skripty/perevod/"
cells = json.load(open(P + "_cells.json", encoding="utf-8"))
pairs = json.load(open(P + "_pairs_status.json", encoding="utf-8"))
LAB = {"кандидат": "候选", "много конкурентов": "竞争者多", "нет на Ozon и WB": "Ozon和WB上都没有", "только на WB": "只在WB上有", "есть на Ozon": "Ozon上有",
       "нет продавцов": "无卖家", "нет номера": "无零件号", "нет в наличии": "无现货", "не проверяли": "未核查"}
OZNOTE = {
 "на Ozon продают 8 продавцов": "Ozon上有8个卖家在卖", "на Ozon продаёт 1 продавец": "Ozon上有1个卖家在卖",
 "на Ozon продают 4 продавца": "Ozon上有4个卖家在卖", "на Ozon продают 7 продавцов": "Ozon上有7个卖家在卖",
 "рулевой вал нижний": "转向下轴", "в выдаче есть ремни других машин — цифра завышена": "搜索结果里混有其他车型的皮带，数字偏高",
 "цепь ГРМ и комплект Gates": "正时链条和Gates套件", "в карточках с номером — карданный вал": "带此零件号的商品页是传动轴",
 "рессора 18 022–25 356 ₽ (449 ₽ — сайлентблок)": "钢板弹簧18022–25356卢布（449卢布是减震衬套）",
 "кронштейн запасного колеса": "备胎支架",
 "ступица; при повторной проверке Ozon написал «Ничего не нашлось»": "轮毂；复查时Ozon显示“Ничего не нашлось”（未找到任何内容）",
 "Ozon: «Ничего не нашлось»": "Ozon显示“Ничего не нашлось”（未找到任何内容）",
 "часть карточек — выхлопные трубы с этим номером в названии": "部分商品页是名称中带此零件号的排气管",
 "в части карточек — рычаги для Tank 300": "部分商品页是Tank 300的控制臂",
}
mute = {}
for ru, zh in pairs.values():
    r = BeautifulSoup(ru, "html.parser").find(class_="mute"); z = BeautifulSoup(zh, "html.parser").find(class_="mute")
    if r and z: mute[r.get_text()] = z.decode_contents()
key = lambda s: hashlib.md5(s.encode()).hexdigest()[:12]
soup = BeautifulSoup(open("otchet_dlya_chzhana.html", encoding="utf-8").read(), "html.parser")
out, miss = {}, []
for tr in soup.select("#tb tr"):
    tds = tr.find_all("td")
    n = tds[0].get_text().strip(); c = cells[n]
    ru = tds[4].decode_contents().strip()
    parts = list(c["oz_zh"])
    if c["oznote"]: parts.append(OZNOTE[c["oznote"]])
    if c["note"]:
        if c["note"] in mute: parts.append(mute[c["note"]])
        else: miss.append((n, c["note"]))
    z = f'<span class="tag {c["cls"]}">{LAB[c["label"]]}</span>' + (f'<br/><span class="mute">{"；".join(parts)}</span>' if parts else "")
    out[key(ru)] = z
json.dump(out, open(P + "zh_status.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("ячеек:", len(out), "пометок без перевода:", miss)

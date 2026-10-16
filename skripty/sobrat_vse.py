# Пересобрать всё: отчёты -> двуязычный (китайский + русский) -> один HTML со снимками внутри. Запуск из корня zapchasti.
import re, os, io, json, base64, subprocess, sys
from PIL import Image
subprocess.run([sys.executable, "skripty/make_proverka.py"], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, "skripty/bilingual.py", "build", "otchet_dlya_chzhana.html", "skripty/perevod", "tmp_bi.html"], check=True)
h = open("tmp_bi.html", encoding="utf-8").read(); os.remove("tmp_bi.html")
D = {}
def uri(p):
    if p in D: return
    im = Image.open(p).convert("RGB")
    if im.width > 1400: im = im.resize((1400, int(im.height * 1400 / im.width)))
    b = io.BytesIO(); im.save(b, "JPEG", quality=72, optimize=True)
    D[p] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
def rep(m):
    p = m.group(2)
    if os.path.exists(p): uri(p); return m.group(1) + '="IMG:' + p + '"'
    return m.group(0)
h = re.sub(r'(src|href|data-big)="((?:dokazatelstva|vhod)/[^"#?]+)"', rep, h)
js = '<script>const IMGS=' + json.dumps(D) + ';document.querySelectorAll("[src^=\'IMG:\'],[href^=\'IMG:\'],[data-big^=\'IMG:\']").forEach(e=>{for(const a of ["src","href","data-big"]){const v=e.getAttribute(a);if(v&&v.startsWith("IMG:"))e.setAttribute(a,IMGS[v.slice(4)])}});</script>\n'
open("otchet_vse_v_odnom_fayle.html", "w", encoding="utf-8").write(h.replace("</body>", js + "</body>", 1))
print("картинок:", len(D))

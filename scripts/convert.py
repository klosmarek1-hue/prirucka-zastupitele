#!/usr/bin/env python3
"""Převod Příručky pro člena zastupitelstva obce (SMO ČR, 2022) z PDF do Markdownu.

Použití:
    pdftotext -bbox-layout prirucka.pdf prirucka.bbox.html
    python3 convert.py prirucka.pdf prirucka.bbox.html vystup/

Potřebuje: poppler-utils (pdftotext), PyMuPDF (pip install pymupdf).

Postup:
- text a pořadí čtení bere z pdftotext (správně zvládá dvousloupcovou sazbu a ligatury),
- PyMuPDF používá jen k nalezení tabulek, poznámek pod čarou a velikosti písma,
- nadpisy hledá podle obsahu příručky (TOC níže),
- schémata a mapy nahrazuje ručně psaným textem z figures.py.
"""
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figures import FIGURES  # noqa: E402
from toc import TOC  # noqa: E402

PDF, BBOX, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3])

SKIP_PAGES = {1, 2, 3, 5, 6, 7, 8, 9}          # obálka, tiráž, obsah
TOC_PAGES = {6, 7, 8, 9}
HEADER_MAX_Y = 62                               # živé záhlaví
FOOTER_MIN_Y = 790                              # číslo stránky
BULLETS = {"", ""}
GLYPH_MAP = {"": "→", "": "", "‐": "-"}
TABLE_PAGES_IGNORE = TOC_PAGES | {135}
# překlepy v číslování poznámek v originále (kap. 22: dvakrát "32)", první má být 31)
NOTE_TEXT_KEY = {"čl. 4 odst. 5 GDPR": "22-31", "body 26 a 28 odůvodnění GDPR": "22-32"}           # 135 = schéma 10.7, řeší figures.py


# ---------------------------------------------------------------- helpers
LOWER = "a-záčďéěíňóřšťúůýž"
CAPTION = r"(Tab\.|Obr\.|Schéma|Mapa|Graf)\s"
LAWLINE = r"(ústavní zákon|zákon|vyhláška|nařízení|směrnice|Nařízení)\b"
ITEM = r"(([a-z]|\d{1,2})\)|\d{1,2}\.)\s"
ABBR = r"(\b(např|písm|odst|č|tzv|tj|resp|zejm|mj|vč|čl|tzn|popř|odd|hl|ul|tř)|\b[IVX]{1,4})\.$"


def is_open(text):
    """True, pokud odstavec zjevně nekončí (není konec věty)."""
    text = re.sub(r"(\[\^[\w-]+\])+$", "", text)
    if text.startswith("Zdroj:"):
        return False
    if len(text) < 40 and re.fullmatch(r"[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\w ]*", text):
        return False   # krátký mezititulek, např. "Kultura"
    if text.endswith("-") or text.endswith("\u00ad"):
        return True
    if re.search(ABBR, text):
        return True
    return not re.search(r"[\.:;!?“”\)]$", text)

def norm(s):
    s = s.replace("­", "")
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"\s+", " ", s).strip()


def fix_glyphs(s):
    for k, v in GLYPH_MAP.items():
        s = s.replace(k, v)
    return s


def join_lines(a, b):
    """Spojí dva řádky jednoho odstavce, včetně rozdělení slov."""
    if not a:
        return b
    if not b:
        return a
    if a.endswith("­"):
        return a[:-1] + b
    if re.search(r"[A-Za-zÁ-ž]-$", a) and re.match(r"[a-zá-ž]", b):
        return a[:-1] + b
    return a + " " + b


def inside(cx, cy, r):
    return r[0] <= cx <= r[2] and r[1] <= cy <= r[3]


# ---------------------------------------------------------------- bbox parse
def load_bbox(path):
    raw = Path(path).read_text(encoding="utf-8")
    raw = re.sub(r"<!DOCTYPE[^>]*>", "", raw)
    raw = raw.replace('xmlns="http://www.w3.org/1999/xhtml"', "")
    root = ET.fromstring(raw)
    pages = []
    for pg in root.iter("page"):
        blocks = []
        for bl in pg.iter("block"):
            lines = []
            for ln in bl.iter("line"):
                words = []
                for w in ln.iter("word"):
                    words.append(dict(x0=float(w.get("xMin")), y0=float(w.get("yMin")),
                                      x1=float(w.get("xMax")), y1=float(w.get("yMax")),
                                      t=fix_glyphs(w.text or "")))
                if words:
                    lines.append(words)
            if lines:
                blocks.append(lines)
        blocks = [[part for ln in bl for part in split_gutter(ln)] for bl in blocks]
        blocks = fold_bullet_lines(blocks)
        pages.append(fold_superscript_lines([unmix_columns(bl) for bl in blocks]))
    return pages


def split_gutter(ln):
    """Rozdělí řádek, který pdftotext slepil přes mezeru mezi sloupci."""
    ln = sorted(ln, key=lambda w: w["x0"])
    for i in range(1, len(ln)):
        a, b = ln[i - 1], ln[i]
        if a["x1"] < 298 < b["x0"] and b["x0"] - a["x1"] > 8:
            return [ln[:i]] + split_gutter(ln[i:])
    return [ln]


def line_col(ln):
    if ln[-1]["x1"] < 300:
        return 0
    if ln[0]["x0"] > 292:
        return 1
    return 2


def unmix_columns(bl):
    """Seřadí řádky bloku po sloupcích shora dolů a slepí úlomky téhož řádku.

    pdftotext občas proloží řádky levého a pravého sloupce nebo rozseká řádek
    kolem obtékaného obrázku na kousky v nesprávném pořadí."""
    def ordered(seg):
        seg = sorted(seg, key=lambda l: (line_col(l), round(min(w["y0"] for w in l) / 4), l[0]["x0"]))
        out = []
        for ln in seg:
            if out and line_col(out[-1]) == line_col(ln) \
                    and abs(min(w["y0"] for w in out[-1]) - min(w["y0"] for w in ln)) < 3 \
                    and ln[0]["x0"] >= out[-1][-1]["x1"] - 1:
                out[-1] = out[-1] + ln
            else:
                out.append(ln)
        return out

    out, seg = [], []
    for ln in bl:
        if line_col(ln) == 2:
            out += ordered(seg)
            out.append(ln)
            seg = []
        else:
            seg.append(ln)
    out += ordered(seg)
    return out


def fold_bullet_lines(blocks):
    """Odrážka (+ první slovo) v jiném bloku než zbytek řádku -> připojit k řádku."""
    all_lines = [(bi, ln) for bi, bl in enumerate(blocks) for ln in bl]
    remove = set()
    for bi, ln in all_lines:
        if not (ln[0]["t"][:1] in BULLETS and len(ln) <= 3):
            continue
        y = min(w["y0"] for w in ln)
        for bj, other in all_lines:
            if other is ln or id(other) in remove:
                continue
            if abs(min(w["y0"] for w in other) - y) < 4 and 0 <= other[0]["x0"] - ln[-1]["x1"] < 14:
                other[:0] = ln
                remove.add(id(ln))
                break
    return [[ln for ln in bl if id(ln) not in remove] for bl in blocks]


def is_sup(w):
    return re.fullmatch(r"\d{1,3}", w["t"]) is not None and (w["y1"] - w["y0"]) < 9.0


def fold_superscript_lines(blocks):
    """Řádky složené jen ze superskriptů vloží do sousedního řádku podle souřadnic."""
    all_lines = [ln for bl in blocks for ln in bl]
    for bi, bl in enumerate(blocks):
        keep = []
        for ln in bl:
            if all(is_sup(w) for w in ln):
                placed = False
                for w in ln:
                    cy = (w["y0"] + w["y1"]) / 2
                    best = None
                    for other in all_lines:
                        if other is ln or all(is_sup(x) for x in other):
                            continue
                        oy0 = min(x["y0"] for x in other)
                        oy1 = max(x["y1"] for x in other)
                        if oy0 - 3 <= cy <= oy1 and other[0]["x0"] - 5 <= w["x0"] <= other[-1]["x1"] + 8:
                            best = other
                            break
                    if best is not None:
                        best.append(w)
                        best.sort(key=lambda x: x["x0"])
                        placed = True
                if not placed:
                    keep.append(ln)
            else:
                keep.append(ln)
        blocks[bi] = keep
    return [bl for bl in blocks if bl]


def words_to_text(words, superscripts=True):
    """Složí slova řádku; drobné číslice nad účařím převede na odkazy [^n]."""
    hs = sorted(w["y1"] - w["y0"] for w in words)
    med = hs[len(hs) // 2] if hs else 10
    out = ""
    prev = None
    for w in words:
        t = w["t"]
        h = w["y1"] - w["y0"]
        if superscripts and prev is not None and re.fullmatch(r"\d{1,3}", t) and (h < 0.8 * med or h < 9.0):
            if t in ("2", "3") and re.fullmatch(r"(km|m|cm)", prev["t"]):
                t = "²" if t == "2" else "³"
            else:
                t = f"[^{t}]"
            out += t
            prev = w
            continue
        if prev is None:
            out = t
        else:
            gap = w["x0"] - prev["x1"]
            out += (" " if gap > 0.9 else "") + t
        prev = w
    return out


# ---------------------------------------------------------------- pymupdf info
def footnote_zones(page):
    """Oblasti s poznámkami pod čarou (písmo ~9 pt, začínají 'n)')."""
    d = page.get_text("dict")
    lines = []
    for b in d["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt:
                continue
            spans = [s for s in l["spans"] if s["text"].strip()]
            size = max(spans, key=lambda s: len(s["text"].strip()))["size"]
            if re.match(r"\d{1,3}\)", txt) and 8.4 <= spans[0]["size"] <= 9.6:
                size = spans[0]["size"]       # značka poznámky rozhoduje
            lines.append((l["bbox"], size, txt))
    two_col = any(bb[0] >= 295 and sz >= 9.8 and bb[1] > HEADER_MAX_Y and bb[3] < FOOTER_MIN_Y
                  for bb, sz, _ in lines)
    zones = []
    lines.sort(key=lambda x: (x[0][1], x[0][0]))
    for bb, sz, txt in lines:
        if not (8.4 <= sz <= 9.6 and re.match(r"\d{1,3}\)", txt)):
            continue
        if two_col and bb[2] < 305:
            xr = (0, 297)
        elif two_col and bb[0] >= 290:
            xr = (297, 600)
        else:
            xr = (0, 600)
        if any(z[0] == xr[0] and z[1] <= bb[1] <= z[3] + 1 for z in zones):
            continue
        # rozšiř dolů přes navazující drobné řádky ve stejném sloupci
        y1 = bb[3]
        for bb2, sz2, _ in lines:
            if bb2[1] < bb[1] or not (xr[0] <= bb2[0] < xr[1]):
                continue
            if bb2[1] > FOOTER_MIN_Y:
                break
            if bb2[1] - y1 > 14:
                break
            if sz2 > 9.6:
                break
            y1 = max(y1, bb2[3])
        zones.append((xr[0], bb[1] - 1, xr[1], y1 + 1))
    # levá zóna, ve které leží poznámka přes celou šířku -> rozšířit
    out = []
    for z in zones:
        if z[2] == 297 and any(sz <= 9.6 and bb[0] < 290 and bb[2] > 305 and z[1] <= bb[1] <= z[3]
                               for bb, sz, _ in lines):
            z = (z[0], z[1], 600, z[3])
        out.append(z)
    return out


def table_cells_md(table, page_words):
    """Postaví Markdown tabulku z buněk; text buněk bere z pdftotext slov."""
    rows = []
    for row in table.rows:
        cells = []
        for c in row.cells:
            if c is None:
                cells.append(None)
                continue
            ws = [w for w in page_words if inside((w["x0"] + w["x1"]) / 2, (w["y0"] + w["y1"]) / 2, c)]
            ws.sort(key=lambda w: (round(w["y0"] / 3), w["x0"]))
            # skupiny do řádků
            lines, cur, cy = [], [], None
            for w in ws:
                if cy is not None and abs(w["y0"] - cy) > 4 and not (w["y1"] - w["y0"] < 8):
                    lines.append(cur)
                    cur = []
                if not cur or not (w["y1"] - w["y0"] < 8):
                    cy = w["y0"] if not cur else cy
                cur.append(w)
            if cur:
                lines.append(cur)
            txt = ""
            for ln in lines:
                ln.sort(key=lambda w: w["x0"])
                txt = join_lines(txt, words_to_text(ln))
            cells.append(norm(txt).replace("|", "\\|"))
        rows.append(cells)
    if not rows:
        return ""
    ncol = max(len(r) for r in rows)
    out = []
    for i, r in enumerate(rows):
        r = r + [None] * (ncol - len(r))
        filled = [x for x in r if x]
        if len([x for x in r if x is not None]) == 1 and r[0] and i > 0:
            # řádek-oddíl přes celou šířku
            r = [f"**{r[0]}**"] + [""] * (ncol - 1)
        else:
            # sloučené buňky (None) – převezmi hodnotu shora
            r = [x if x is not None else (rows[i - 1][j] if i > 0 and j < len(rows[i - 1]) and rows[i - 1][j] else "")
                 for j, x in enumerate(r)]
        out.append("| " + " | ".join(x or "" for x in r) + " |")
        if i == 0:
            out.append("|" + "---|" * ncol)
    return "\n".join(out)


def _nt(t):
    # porovnání odolné vůči ztraceným ligaturám (fi, fl) a interpunkci
    return re.sub(r"[^\w]|[fil_]", "", t.lower())


# Stránky se sazbou v rámečcích, kde je pořadí bloků z pdftotext špatně.
PAGE_ORDER_PAGES = {52, 84, 111, 221, 223, 240}


def page_order(blocks, page, pno):
    """Pořadí čtení pro dvousloupcové stránky: pásy oddělené prvky přes celou šířku,
    v každém pásu nejdřív levý, pak pravý sloupec."""
    lines = [ln for bl in blocks for ln in bl
             if HEADER_MAX_Y < min(w["y0"] for w in ln) < FOOTER_MIN_Y]
    if not lines:
        return blocks
    chars = {0: 0, 1: 0, 2: 0}
    for ln in lines:
        chars[line_col(ln)] += sum(len(w["t"]) for w in ln)
    if chars[1] < 200 or chars[0] + chars[1] < chars[2]:
        return blocks           # jednosloupcová stránka – nechat pořadí pdftotext
    seps = []                   # oddělovače přes celou šířku (y0, y1)
    for im in page.get_image_info():
        r = im["bbox"]
        if r[2] - r[0] > 350:
            seps.append((r[1], r[3]))
    for f in FIGURES.values():
        if f["page"] == pno and f["bbox"][2] - f["bbox"][0] > 350:
            seps.append((f["bbox"][1], f["bbox"][3]))

    def y_of(ln):
        return min(w["y0"] for w in ln)

    def in_sep(ln):
        cy = (min(w["y0"] for w in ln) + max(w["y1"] for w in ln)) / 2
        return any(a - 1 <= cy <= b + 1 for a, b in seps)

    tabs = [] if pno in TABLE_PAGES_IGNORE else [t.bbox for t in page.find_tables().tables]

    def tab_of(ln):
        cx = (ln[0]["x0"] + ln[-1]["x1"]) / 2
        cy = (min(w["y0"] for w in ln) + max(w["y1"] for w in ln)) / 2
        return next((t for t in tabs if inside(cx, cy, t)), None)

    def in_tab(ln):
        return tab_of(ln) is not None

    def tab_col(ln):
        t = tab_of(ln)
        return 0 if (t[2] - t[0] > 350 or (t[0] + t[2]) / 2 < 297) else 1

    # řádky tabulek nejsou oddělovače pásů: patří do sloupce, kde tabulka začíná
    full = sorted([y_of(ln) for ln in lines if (line_col(ln) == 2 or in_sep(ln)) and not in_tab(ln)])

    def key(ln):
        y = y_of(ln)
        if in_tab(ln):
            band = sum(1 for f in full if f < y - 0.5)
            return (2 * band, tab_col(ln), y, ln[0]["x0"])
        if line_col(ln) == 2 or in_sep(ln):
            r = sum(1 for f in full if f < y - 0.5)
            return (2 * r + 1, 0, y, ln[0]["x0"])
        band = sum(1 for f in full if f < y - 0.5)
        return (2 * band, line_col(ln), y, ln[0]["x0"])

    # rozdělit bloky na úseky téhož sloupce; přeřazují se celé úseky, ne řádky
    runs = []
    for bl in blocks:
        cur, cc = [], None
        for ln in bl:
            c = tab_col(ln) if in_tab(ln) else 2 if (line_col(ln) == 2 or in_sep(ln)) else line_col(ln)
            if cur and c != cc:
                runs.append(cur)
                cur = []
            cur.append(ln)
            cc = c
        if cur:
            runs.append(cur)
    hf = [r for r in runs if not (HEADER_MAX_Y < min(w["y0"] for w in r[0]) < FOOTER_MIN_Y)]
    body = [r for r in runs if r not in hf]
    body.sort(key=lambda r: key(r[0]))
    return body + hf


def auto_rows_md(page, bbox):
    """Text oblasti po vizuálních řádcích (y), v řádku zleva doprava."""
    words = [w for w in page.get_text("words", clip=pymupdf.Rect(bbox))]
    words.sort(key=lambda w: (w[1], w[0]))
    rows, cur, cy = [], [], None
    for w in words:
        if cur and w[1] - cy > 4:
            rows.append(cur)
            cur = []
        if not cur:
            cy = w[1]
        cur.append(w)
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        r.sort(key=lambda w: w[0])
        txt = norm(" ".join(w[4] for w in r))
        depth = len(re.match(r"(\d+\.)*", txt).group(0).rstrip(".").split(".")) - 1 if re.match(r"\d", txt) else 0
        out.append("  " * max(depth, 0) + "- " + txt)
    return "\n".join(out)


def drop_hidden(blocks, page):
    """Zahodí slova, která vidí pdftotext, ale ne PyMuPDF (oříznutý/skrytý text)."""
    buckets = {}
    for w in page.get_text("words"):
        r = (w[0] - 2, w[1] - 2, w[2] + 2, w[3] + 2)
        for b in range(int(r[1] // 10), int(r[3] // 10) + 1):
            buckets.setdefault(b, []).append((r, _nt(w[4])))

    def visible(w):
        cx, cy = (w["x0"] + w["x1"]) / 2, (w["y0"] + w["y1"]) / 2
        a = _nt(w["t"])
        for r, m in buckets.get(int(cy // 10), []):
            if inside(cx, cy, r) and (a in m or m in a):
                return True
        return False

    out = []
    for bl in blocks:
        nb = []
        for ln in bl:
            nl = [w for w in ln if visible(w)]
            if nl:
                nb.append(nl)
        if nb:
            out.append(nb)
    return out


# ---------------------------------------------------------------- main flow
def build_stream():
    doc = pymupdf.open(PDF)
    pages = load_bbox(BBOX)
    stream = []   # položky: dict(kind=..., page=...)
    for pi, blocks in enumerate(pages):
        pno = pi + 1
        if pno in SKIP_PAGES:
            continue
        page = doc[pi]
        blocks = drop_hidden(blocks, page)
        blocks = [unmix_columns([part for ln in bl for part in split_gutter(ln)]) for bl in blocks]
        if pno in PAGE_ORDER_PAGES:
            blocks = page_order(blocks, page, pno)
        all_words = [w for bl in blocks for ln in bl for w in ln]
        regions = []  # (rect, kind, id, md)
        if pno not in TABLE_PAGES_IGNORE:
            for ti, t in enumerate(page.find_tables().tables):
                regions.append((tuple(t.bbox), "table", f"t{pno}_{ti}", table_cells_md(t, all_words)))
        for fid, f in FIGURES.items():
            if f["page"] == pno:
                md = auto_rows_md(page, f["bbox"]) if f.get("auto") else f["md"]
                regions.append((tuple(f["bbox"]), "fig", fid, md))
        fzones = footnote_zones(page)
        emitted = set()
        stream.append(dict(kind="page", page=pno))
        foot_lines = []
        for bl in blocks:
            out_lines = []
            for ln in bl:
                keep = []
                for w in ln:
                    cx, cy = (w["x0"] + w["x1"]) / 2, (w["y0"] + w["y1"]) / 2
                    if cy < HEADER_MAX_Y or cy > FOOTER_MIN_Y:
                        continue
                    hit = next((r for r in regions if inside(cx, cy, r[0])), None)
                    if hit:
                        if hit[2] not in emitted:
                            emitted.add(hit[2])
                            if out_lines:
                                stream.append(dict(kind="lines", page=pno, lines=out_lines))
                                out_lines = []
                            stream.append(dict(kind=hit[1], page=pno, id=hit[2], md=hit[3]))
                        continue
                    if any(inside(cx, cy, z) for z in fzones):
                        foot_lines.append(w)
                        continue
                    keep.append(w)
                if keep:
                    out_lines.append(keep)
            if out_lines:
                stream.append(dict(kind="lines", page=pno, lines=out_lines))
        # obrázky/tabulky, které nemají žádný text v toku (rastrové mapy)
        for r in regions:
            if r[2] not in emitted:
                stream.append(dict(kind=r[1], page=pno, id=r[2], md=r[3]))
        if foot_lines:
            stream.append(dict(kind="foot", page=pno, words=foot_lines))
    return stream


def lines_to_paras(lines):
    """Řádky jednoho bloku -> odstavce (dle odsazení, odrážek a konců vět)."""
    left = min(l[0]["x0"] for l in lines)
    right = max(l[-1]["x1"] for l in lines)
    paras = []
    cur, cur_list_x = None, None
    prev = None
    for ln in lines:
        txt = words_to_text(ln)
        x0 = ln[0]["x0"]
        first = txt[:1]
        is_bullet = first in BULLETS
        if is_bullet:
            txt = "- " + txt[1:].lstrip()
        is_item = is_bullet or re.match(r"([a-zA-Z]|\d{1,2}|[ivx]{1,4})[\)\.]\s", txt) is not None
        brk = False
        if cur is None:
            brk = True
        elif is_item:
            brk = True
        else:
            prev_txt = words_to_text(prev)
            ends = not is_open(prev_txt)
            prev_short = prev[-1]["x1"] < right - 25
            indented = x0 > left + 3
            if cur_list_x is not None:
                if x0 > cur_list_x + 2:
                    brk = False
                else:
                    brk = ends or prev_short
            else:
                brk = (indented and ends) or (ends and prev_short) or (indented and prev_short)
        if brk:
            if cur is not None:
                paras.append(cur)
            cur = txt
            cur_list_x = x0 if is_item else None
        else:
            cur = join_lines(cur, txt)
        prev = ln
    if cur is not None:
        paras.append(cur)
    return [p for p in (norm(x) if not x.startswith("- ") else "- " + norm(x[2:]) for x in paras) if p]


def foot_to_notes(words, chap):
    lines = []
    for col in (False, True):
        ws = sorted([w for w in words if (w["x0"] > 297) == col], key=lambda w: w["y0"])
        cur, cy = [], None
        for w in ws:
            if cur and w["y0"] - cy > 3:
                lines.append(sorted(cur, key=lambda w: w["x0"]))
                cur = []
            if not cur:
                cy = w["y0"]
            cur.append(w)
        if cur:
            lines.append(sorted(cur, key=lambda w: w["x0"]))
    notes = []
    for ln in lines:
        t = words_to_text(ln, superscripts=False)
        m = re.match(r"(\d{1,3})\)\s*(.*)", t)
        if m:
            notes.append([m.group(1), m.group(2)])
        elif notes:
            notes[-1][1] = join_lines(notes[-1][1], t)
        else:
            notes.append(["?", t])
    return [(n, norm(t)) for n, t in notes]


def heading_key(s):
    return re.sub(r"[^0-9a-zá-ž]", "", norm(s).lower())


def main():
    stream = build_stream()
    # rozpad na řádky s informací o stránce (kvůli hledání nadpisů)
    items = []
    for it in stream:
        if it["kind"] == "lines":
            items.append(it)
        else:
            items.append(it)
    # ---- odstavce
    flat = []   # (kind, page, payload)
    for it in items:
        if it["kind"] == "lines":
            for ln in it["lines"]:
                pass
            flat.append(["blk", it["page"], it["lines"]])
        else:
            flat.append([it["kind"], it["page"], it])
    # ---- hledání nadpisů v řádcích
    toc = [dict(num=n, title=t, page=p, level=(1 if "." not in n else 2)) for n, t, p in TOC]
    ti = 0
    out = []   # finální položky
    for kind, pno, payload in flat:
        if kind != "blk":
            out.append((kind, pno, payload))
            continue
        lines = payload
        buf = []
        i = 0
        while i < len(lines):
            matched = False
            if ti < len(toc):
                e = toc[ti]
                t = norm(words_to_text(lines[i], superscripts=False))
                num_re = (re.escape(e["num"]).replace(r"\.", r"\.\s?") + r"\.?\s") if e["num"] else ""
                if re.match(num_re, t) and pno >= e["page"] - 6:
                    rest = heading_key(t[len(re.match(num_re, t).group(0)):])
                    want = heading_key(e["title"])
                    if want.startswith(rest[:12]) and rest:
                        # spotřebuj pokračování nadpisu
                        j = i + 1
                        while len(rest) < len(want) and j < len(lines):
                            nxt = heading_key(words_to_text(lines[j], superscripts=False))
                            if not want[len(rest):].startswith(nxt[:6]):
                                break
                            rest += nxt
                            j += 1
                        if buf:
                            out.append(("blk", pno, buf))
                            buf = []
                        out.append(("heading", pno, e))
                        ti += 1
                        i = j
                        matched = True
            if not matched:
                buf.append(lines[i])
                i += 1
        if buf:
            out.append(("blk", pno, buf))
    missing = [e["num"] for e in toc[ti:]]
    if missing:
        print("NENALEZENÉ NADPISY:", missing, file=sys.stderr)
    # ---- odstavce + spojování přes bloky/stránky
    final = []
    chap = None
    for kind, pno, payload in out:
        if kind == "heading":
            if payload["level"] == 1:
                chap = payload["num"]
            final.append(dict(kind="heading", page=pno, entry=payload))
        elif kind == "blk":
            for p in lines_to_paras(payload):
                final.append(dict(kind="para", page=pno, text=p))
        elif kind == "foot":
            final.append(dict(kind="foot", page=pno, notes=foot_to_notes(payload["words"], chap)))
        elif kind in ("table", "fig"):
            final.append(dict(kind=kind, page=pno, id=payload["id"], md=payload["md"]))
        elif kind == "page":
            final.append(dict(kind="page", page=pno))
    # spojit odstavec rozdělený sloupcem, stránkou, obrázkem či tabulkou
    merged = []
    for it in final:
        if it["kind"] == "para":
            k = len(merged) - 1
            crossed = False
            while k >= 0 and (merged[k]["kind"] in ("page", "foot", "fig", "table")
                              or (merged[k]["kind"] == "para" and re.match(CAPTION, merged[k]["text"]))):
                if merged[k]["kind"] != "page" and merged[k]["kind"] != "foot":
                    crossed = True
                k -= 1
            if k >= 0 and merged[k]["kind"] == "para":
                a, b = merged[k]["text"], it["text"]
                lower = re.match(f"[{LOWER}(]", b) and not re.match(ITEM, b)
                a_open = is_open(a)
                if b.startswith("- ") or a.startswith("- "):
                    cont = a_open and (lower or b.startswith("Sb.")) and not b.startswith("- ")
                elif crossed:
                    cont = a_open and (lower or re.match(r"[0-9(„–]", b))
                else:
                    cont = a_open and (re.match(f"[{LOWER}0-9(„–]", b) or b.startswith("Sb.")) \
                        and not re.match(ITEM, b)
                lawlist = re.match(LAWLINE, b) and re.match(LAWLINE, a)
                if not cont and lower and not lawlist:
                    # pokračování může patřit k dřívějšímu nedokončenému odstavci
                    # (sazba v rámečcích: levý sloupec pokračuje až na další straně)
                    seen = 0
                    for j in range(k - 1, -1, -1):
                        if merged[j]["kind"] == "heading":
                            break
                        if merged[j]["kind"] != "para":
                            continue
                        seen += 1
                        if seen > 15:
                            break
                        t = merged[j]["text"]
                        if len(t) > 40 and (t.endswith("-") or re.search(f"[{LOWER},]$", t)):
                            merged[j]["text"] = join_lines(t, b)
                            cont = True
                            break
                    if cont:
                        continue
                    cont = not crossed
                if cont:
                    merged[k]["text"] = join_lines(a, b)
                    continue
        merged.append(it)
    OUT.mkdir(parents=True, exist_ok=True)
    print("položek:", len(merged), "nadpisů:", ti, "/", len(toc))
    build_files(merged)


# ---------------------------------------------------------------- výstupní soubory
SOURCE = ("Příručka pro člena zastupitelstva obce po volbách v roce 2022, "
          "Svaz měst a obcí České republiky, Praha 2022, ISBN 978-80-88375-17-3 (online)")
SOURCE_URL = "https://www.smocr.cz/Shared/Clanky/12158/eprirucka-final.pdf"
STATUS = "Právní stav k roku 2022. Předpisy se od té doby mohly změnit – ověřte aktuální znění."


def slug(s, n=48):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].rstrip("-")


def chap_of(num):
    return num.split(".")[0] if num else "26"


# Zjevné tiskové chyby v originálu, které by mohly zmást model (uvedeno i v README).
TEXT_FIXES = {
    "č.1993/1 Sb.": "č. 1/1993 Sb.",
    "č.1998/110 Sb.": "č. 110/1998 Sb.",
    "č. 84/0190 Sb.": "č. 84/1990 Sb.",
}


def fix_text(t):
    for a, b in TEXT_FIXES.items():
        t = t.replace(a, b)
    return t


def build_files(items):
    for it in items:
        for k in ("text", "md"):
            if isinstance(it.get(k), str):
                it[k] = fix_text(it[k])
        if it.get("kind") == "foot":
            it["notes"] = [(n, fix_text(t)) for n, t in it["notes"]]
    # 1) rozdělit na sekce
    sections = []
    cur = dict(num="0", title="Předmluva", level=1, chapter=("0", "Předmluva"), items=[], pages=set())
    sections.append(cur)
    chapter = ("0", "Předmluva")
    for it in items:
        if it["kind"] == "heading":
            e = it["entry"]
            num = e["num"] or "26"
            if e["level"] == 1:
                chapter = (num, e["title"])
            cur = dict(num=num, title=e["title"], level=e["level"], chapter=chapter, items=[], pages={it["page"]})
            sections.append(cur)
            continue
        cur["items"].append(it)
        if it["kind"] != "page":
            cur["pages"].add(it["page"])

    # 1b) obrázky s ručně určenou sekcí (např. schéma vysázené až za začátkem další podkapitoly)
    for s_ in sections:
        for it in list(s_["items"]):
            if it["kind"] == "fig" and FIGURES.get(it["id"], {}).get("section") \
                    and FIGURES[it["id"]]["section"] != s_["num"]:
                target = next(x for x in sections if x["num"] == FIGURES[it["id"]]["section"])
                s_["items"].remove(it)
                target["items"].append(it)
                target["pages"].add(it["page"])

    # 2) poznámky pod čarou: globální id kapitola-číslo
    notes = {}
    note_home = {}
    for si, s in enumerate(sections):
        c = chap_of(s["num"]) if s["num"] != "0" else "0"
        for it in s["items"]:
            if it["kind"] == "foot":
                for n, t in it["notes"]:
                    key = f"{c}-{n}"
                    if key in notes and notes[key] != t:
                        key = f"{c}-{n}b"
                    key = NOTE_TEXT_KEY.get(t, key)
                    notes[key] = t
                    note_home[key] = si

    def fix_refs(text, c):
        return re.sub(r"\[\^(\d{1,3})\]", lambda m: f"[^{c}-{m.group(1)}]", text)

    # 3) sloučit úvod kapitoly do první podkapitoly
    merged_secs = []
    pending_intro = None
    for s in sections:
        if s["level"] == 1 and s["num"] not in ("0", "1", "26"):
            pending_intro = s
            continue
        if pending_intro is not None and s["level"] == 2:
            s["intro"] = pending_intro
            s["pages"] |= pending_intro["pages"]
            pending_intro = None
        merged_secs.append(s)

    # 4) render
    TITLE = r"(Mgr|JUDr|Ing|PhDr|Bc|doc|prof|RNDr|PaedDr|Dr|MUDr)\."

    def pull_authors(its):
        """Úvodní krátké odstavce se jmény autorů -> jeden řádek 'Autoři kapitoly'."""
        paras = [i for i, it in enumerate(its) if it["kind"] == "para"]
        if not paras or not re.match(TITLE, its[paras[0]]["text"]):
            return its
        names, used = [], []
        for i in paras:
            t = its[i]["text"]
            if len(t) >= 70:
                break
            if re.match(TITLE, t) or not names:
                names.append(t)
            else:
                names[-1] += " " + t          # pokračování jména na dalším řádku
            used.append(i)
        if not used:
            return its
        label = "Autor kapitoly" if len(names) == 1 else "Autoři kapitoly"
        first = dict(its[used[0]], text=f"*{label}: {'; '.join(names)}*")
        return [first if i == used[0] else it for i, it in enumerate(its) if i not in used[1:]]

    def render_items(its, c):
        out, last_page, list_open = [], None, False
        for it in its:
            k = it["kind"]
            if k in ("page", "foot"):
                continue
            if it["page"] != last_page:
                out.append(f"<!-- str. {it['page']} -->")
                last_page = it["page"]
            if k == "para":
                t = fix_refs(it["text"], c)
                if t.startswith("- ") and out and out[-1].startswith("- "):
                    out[-1] += "\n" + t
                else:
                    out.append(t)
            else:
                out.append(fix_refs(it["md"], c))
        return out

    root = OUT
    (root / "kapitoly").mkdir(parents=True, exist_ok=True)
    meta = []
    used_notes = set()
    full = [f"# Příručka pro člena zastupitelstva obce po volbách v roce 2022\n\n"
            f"Zdroj: {SOURCE}. Originál: {SOURCE_URL}\n\n**{STATUS}**\n"]
    all_refs = set()
    for s in sections:
        c = chap_of(s["num"]) if s["num"] != "0" else "0"
        for it in s["items"]:
            t = it.get("text") or it.get("md") or ""
            all_refs.update(f"{c}-{n}" for n in re.findall(r"\[\^(\d{1,3})\]", t))
    for s in merged_secs:
        c = chap_of(s["num"]) if s["num"] != "0" else "0"
        cnum, ctitle = s["chapter"]
        numbered = s["num"] not in ("0", "26")
        label = (s["num"] + " " if numbered else "") + s["title"]
        clabel = (cnum + " " if cnum not in ("0", "26") else "") + ctitle
        intro = render_items(pull_authors(s["intro"]["items"]), c) if s.get("intro") else []
        content = render_items(pull_authors(s["items"]) if s["level"] == 1 else s["items"], c)
        # poznámky: odkazované v sekci + nalezené na jejích stránkách bez odkazu jinde
        text_all = "\n\n".join(intro + content)
        refs = list(dict.fromkeys(re.findall(r"\[\^([\w-]+)\]", text_all)))
        keys = [k for k in refs if k in notes]
        keys += [k for k, si in note_home.items()
                 if k not in all_refs and k not in keys
                 and (sections[si] is s or sections[si] is s.get("intro"))]
        notes_md = "\n".join(f"[^{k}]: {notes[k]}" for k in keys)
        used_notes.update(keys)
        if s["level"] == 1:
            fname = f"{int(cnum):02d}-{slug(s['title'])}.md"
            path = Path("kapitoly") / fname
            file_body = [f"# {label}"] + content
            full_body = [f"# {label}"] + content
        else:
            a, b = s["num"].split(".")
            cdir = f"{int(cnum):02d}-{slug(ctitle, 40)}"
            path = Path("kapitoly") / cdir / f"{int(a):02d}.{int(b):02d}-{slug(s['title'])}.md"
            if intro:
                file_body = [f"# {clabel}"] + intro + [f"## {label}"] + content
                full_body = [f"# {clabel}"] + intro + [f"## {label}"] + content
            else:
                file_body = [f"# {label}"] + content
                full_body = [f"## {label}"] + content
        if notes_md:
            file_body += ["---", notes_md]
            full_body += [notes_md]
        pages = sorted(s["pages"])
        prange = (f"{pages[0]}–{pages[-1]}" if pages[0] != pages[-1] else str(pages[0])) if pages else ""
        fm = ("---\n"
              f"nazev: \"{label}\"\n"
              f"kapitola: \"{clabel}\"\n"
              f"strany_v_pdf: \"{prange}\"\n"
              f"zdroj: \"{SOURCE}\"\n"
              f"original: \"{SOURCE_URL}\"\n"
              f"upozorneni: \"{STATUS}\"\n"
              "---\n\n")
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(fm + "\n\n".join(file_body) + "\n", encoding="utf-8")
        full.append("\n\n".join(full_body))
        meta.append(dict(num=s["num"], title=s["title"], chapter=cnum, chapter_title=ctitle,
                         pages=prange, path=str(path), chars=len("\n\n".join(file_body))))
    orphan = [k for k in notes if k not in used_notes]
    if orphan:
        print("poznámky bez odkazu:", len(orphan), orphan[:30], file=sys.stderr)
    (root / "prirucka-cela.md").write_text("\n\n".join(full) + "\n", encoding="utf-8")
    (root / "sections.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("souborů:", len(meta))


if __name__ == "__main__":
    main()

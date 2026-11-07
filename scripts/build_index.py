#!/usr/bin/env python3
"""Vytvoří llms.txt a index.json z výstupu convert.py.

Použití: python3 build_index.py vystup/
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from popisy import POPISY  # noqa: E402

OUT = Path(sys.argv[1])
meta = json.loads((OUT / "sections.json").read_text(encoding="utf-8"))

missing = [m["num"] for m in meta if m["num"] not in POPISY]
if missing:
    sys.exit(f"Chybí popisy pro: {missing}")


def label(m):
    return m["title"] if m["num"] in ("0", "26") else f"{m['num']} {m['title']}"


def kb(chars):
    return f"{round(chars / 1000)} tis. znaků" if chars >= 1000 else f"{chars} znaků"


lines = [
    "# Příručka pro člena zastupitelstva obce po volbách v roce 2022",
    "",
    "> Neoficiální převod příručky Svazu měst a obcí ČR (SMO ČR, 2022) do Markdownu pro práci s jazykovými "
    "modely. Právní stav k roku 2022 – předpisy se od té doby mohly změnit, ověřujte aktuální znění. "
    "Originál: https://www.smocr.cz/Shared/Clanky/12158/eprirucka-final.pdf",
    "",
    "Jak hledat: podle popisů níže vyber 1–3 nejrelevantnější soubory a přečti jen ty. Každý soubor má v "
    "hlavičce rozsah stran originálu a v textu značky `<!-- str. N -->`, podle kterých lze citovat stranu PDF. "
    "Poznámky pod čarou jsou na konci souboru (`[^kapitola-číslo]`). Poslední podkapitola každé kapitoly "
    "obvykle obsahuje časté otázky, související předpisy, literaturu a dotazy z Právní poradny pro obce.",
    "",
]
current = None
for m in meta:
    ch = m["chapter"]
    if ch != current:
        current = ch
        if ch == "0":
            lines += ["## Úvod", ""]
        elif ch == "26":
            lines += ["", "## Tiráž", ""]
        else:
            lines += ["", f"## {ch} {m['chapter_title']}", ""]
    lines.append(f"- [{label(m)}]({m['path']}): {POPISY[m['num']]} (str. {m['pages']}, {kb(m['chars'])})")

lines += [
    "",
    "## Celý text",
    "",
    "- [prirucka-cela.md](prirucka-cela.md): celá příručka v jednom souboru (pro nástroje, které si soubor "
    "indexují samy, např. NotebookLM nebo projekty v Claude/ChatGPT).",
    "",
]
(OUT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

index = [dict(cislo=m["num"], nazev=m["title"], kapitola=m["chapter"], nazev_kapitoly=m["chapter_title"],
              strany_v_pdf=m["pages"], soubor=m["path"], znaku=m["chars"], popis=POPISY[m["num"]]) for m in meta]
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
print("llms.txt:", len("\n".join(lines)), "znaků;", len(index), "položek")

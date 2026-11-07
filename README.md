# Příručka pro člena zastupitelstva obce (2022) – verze pro AI nástroje

Neoficiální převod [Příručky pro člena zastupitelstva obce po volbách v roce 2022](https://www.smocr.cz/Shared/Clanky/12158/eprirucka-final.pdf) (Svaz měst a obcí ČR) z 288stránkového PDF do Markdownu. Převod je určený pro práci s jazykovými modely (ChatGPT, Claude, NotebookLM, Copilot, vlastní agenti).

PDF je pro AI drahé: celá příručka má zhruba 1,4 milionu znaků, což jsou stovky tisíc tokenů na jeden dotaz. Tady je rozdělená na 171 menších souborů (podkapitol) a má index, takže model přečte jen to, co k odpovědi potřebuje.

> ⚠️ **Právní stav k roku 2022.** Od vydání příručky se řada předpisů změnila. Byl například přijat zákon o ochraně oznamovatelů (č. 171/2023 Sb.) a nabyl účinnosti nový stavební zákon (č. 283/2021 Sb.). Odměny zastupitelů a limity veřejných zakázek se pravidelně mění. Odpovědi modelu vždy ověřte v aktuálním znění předpisů, například na [e-Sbírce](https://www.e-sbirka.cz/), nebo v [Právní poradně pro obce](https://www.poradnaproobce.cz/).

## Co je v repozitáři

| Soubor | K čemu slouží |
|---|---|
| `llms.txt` | Index: seznam všech podkapitol s popisem obsahu, stranami v originále a velikostí. Agent ho čte jako první. |
| `kapitoly/` | Text po podkapitolách (`kapitoly/02-…/02.04-organy-obce-….md`). Každý soubor má hlavičku s názvem, stranami v PDF, zdrojem a upozorněním na stav k roku 2022. |
| `prirucka-cela.md` | Celá příručka v jednom souboru. |
| `index.json` | Stejný index jako `llms.txt`, ale strojově čitelný. |
| `scripts/` | Převodní skripty, aby šlo převod zopakovat (například pro novou verzi příručky). |

## Jak to použít

**Nástroje s přístupem k souborům** (Claude Code, Cursor, Codex, vlastní agent): Stáhněte repozitář a modelu řekněte něco jako:

> Odpovídej podle příručky v této složce. Nejdřív si přečti `llms.txt`, vyber nejvýš tři relevantní soubory z `kapitoly/` a odpověz jen z nich. U každého tvrzení uveď podkapitolu a stranu originálu (značky `<!-- str. N -->`). Upozorni, že jde o právní stav k roku 2022.

Typický dotaz pak stojí index (zhruba 12–15 tisíc tokenů) plus 1–3 podkapitoly (obvykle 1–15 tisíc tokenů). Celá příručka by stála stovky tisíc.

**Chatovací nástroje** (projekt v Claude nebo ChatGPT, NotebookLM, Copilot): Nahrajte `prirucka-cela.md`, případně jen soubory z `kapitoly/`, které vás zajímají. Tyto nástroje si soubory indexují samy a s Markdownem pracují lépe než s PDF.

**Bez instalace:** Na GitHubu klikněte na *Code → Download ZIP*.

## Jak byl převod udělán

- Text a pořadí čtení pochází z `pdftotext` (Poppler), který správně zvládá dvousloupcovou sazbu i ligatury. PyMuPDF slouží k hledání tabulek, poznámek pod čarou a skrytého textu.
- **Tabulky** (26) jsou převedené na Markdown tabulky.
- **Schémata a grafy** (14) jsou ručně přepsané do textu nebo tabulek: organizační schémata, legislativa krizového řízení, rozpočtové určení daní, sociální dávky, SWOT, struktura programu rozvoje obce a další.
- **Mapy a snímky** (11) převedené nejsou. Na jejich místě je popis a odkaz na stranu PDF.
- **Ilustrace** na začátcích kapitol jsou vynechané.
- **Poznámky pod čarou** jsou na konci každého souboru a mají jednoznačné označení `[^kapitola-číslo]`.
- Odstraněné jsou živé záhlaví, čísla stránek a obsah. Rozdělená slova jsou spojená.

### Známá omezení

- Na několika stránkách se složitou sazbou (rámečky, text obtékající obrázky) se může pořadí odstavců mírně lišit od originálu.
- Nadpisy nižší úrovně než podkapitola (například 2.4.1) a tučné písmo nejsou formátované. Jsou to běžné odstavce.
- Chyby v originálu: poznámka 4 v kapitole 2 je v PDF useknutá a poznámka 42 v kapitole 22 v PDF chybí. Opravené jsou dvojí číslo poznámky 32 v kapitole 22 (tady 31 a 32) a obrácená čísla zákonů v tabulce krizových stavů a v kapitole 9 („č.1993/1 Sb.“ → „č. 1/1993 Sb.“, „č.1998/110 Sb.“ → „č. 110/1998 Sb.“, „č. 84/0190 Sb.“ → „č. 84/1990 Sb.“).
- Kontrola: z textu PDF chybí ve výstupu asi 1 % slov. Jde hlavně o živá záhlaví stránek, popisky v mapách a úlomky rozdělených slov.

## Zopakování převodu

Potřeba je Python 3, `poppler-utils` (pdftotext) a `pip install pymupdf`.

```bash
pdftotext -bbox-layout prirucka.pdf prirucka.bbox.html
python3 scripts/convert.py prirucka.pdf prirucka.bbox.html vystup/
python3 scripts/build_index.py vystup/
python3 scripts/check.py vystup/        # kontrola poznámek a úlomků textu
```

Skripty jsou laděné na vydání z roku 2022. Obsah (`toc.py`), schémata (`figures.py`) a popisy (`popisy.py`) jsou ručně psané, takže je u nové verze příručky bude potřeba upravit.

## Zdroj a práva

Původní dílo: *Příručka pro člena zastupitelstva obce po volbách v roce 2022*, Svaz měst a obcí České republiky, Praha 2022, ISBN 978-80-88375-17-3 (online), © SMO ČR 2022. Autoři kapitol jsou uvedeni v souborech a v kapitole *Na příručce spolupracovali*.

Tento repozitář je neoficiální a SMO ČR ho nevydalo ani neschválilo. Obsah zůstává dílem jeho autorů.

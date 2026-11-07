# Ručně převedená schémata, grafy a mapy.
# bbox = oblast na stránce (body PDF), jejíž text se z toku vynechá a nahradí polem md.
FIGURES = {
    "schema-pro": dict(page=95, bbox=(97, 300, 508, 482), md="""\
> **Schéma převedené na text.** Struktura Programu rozvoje obce (PRO):
>
> - **Úvod**
> - **A) Analytická část**
>   - A) 1 Charakteristika obce: 1. území, 2. obyvatelstvo, 3. hospodářství, 4. infrastruktura, 5. vybavenost, 6. životní prostředí, 7. správa obce
>   - A) 2 Východiska pro návrhovou část: silné stránky, slabé stránky
> - **B) Návrhová část**
>   - B) 1 Strategická vize: vize na 10–20 let, dlouhodobé cíle
>   - B) 2 Programové cíle: cíle na 4–7 let
>   - B) 3 Opatření: tematická, prostorová
>   - B) 4 Rozvojové aktivity: důležitost, termíny, odpovědnost, náklady, zdroje financování
>   - B) 5 Podpora realizace PRO: řízení realizace, způsob sledování a hodnocení, způsob aktualizace"""),

    "obr-10-1": dict(page=129, bbox=(100, 100, 530, 345), md="""\
> **Schéma převedené na text.** Hierarchie předpisů krizového řízení:
>
> - Ústavní zákon č. 1/1993 Sb., Ústava České republiky
>   - Ústavní zákon č. 110/1998 Sb., o bezpečnosti České republiky
>     - **Vnitřní bezpečnost ČR**
>       - zákon č. 240/2000 Sb., o krizovém řízení (krizový zákon)
>       - zákon č. 239/2000 Sb., o integrovaném záchranném systému
>       - zákon č. 241/2000 Sb., o hospodářských opatřeních pro krizové stavy
>     - **Vnější bezpečnost ČR**
>       - zákon č. 222/1999 Sb., o zajišťování obrany České republiky
>       - zákon č. 219/1999 Sb., o ozbrojených silách České republiky
>       - zákon č. 585/2004 Sb., o branné povinnosti a jejím zajišťování (branný zákon)"""),

    "obr-10-4": dict(page=132, bbox=(305, 100, 548, 290), md="""\
> **Graf převedený na data** (koláčový graf; stejné údaje jako výčet v kapitole 10.3):
>
> | Důvod vyhlášení stavu nebezpečí | Počet |
> |---|---|
> | povodně | 28 |
> | sesuv půdy | 4 |
> | nebezpečné látky | 2 |
> | tornádo (extrémní vítr) | 2 |
> | porucha vodního díla | 1 |
> | africký mor prasat | 1 |"""),

    "obr-10-7": dict(page=135, bbox=(100, 97, 495, 430), md="""\
> **Schéma převedené na text.** Celkový pohled na ochranu obyvatelstva:
>
> | Situace | Právní základ | Oblast |
> |---|---|---|
> | Mimořádná událost | zákon č. 239/2000 Sb., o integrovaném záchranném systému | civilní ochrana |
> | Stav nebezpečí | zákon č. 240/2000 Sb., o krizovém řízení | civilní ochrana |
> | Nouzový stav | ústavní zákon č. 110/1998 Sb., o bezpečnosti České republiky | civilní ochrana |
> | Stav ohrožení státu | ústavní zákon č. 1/1993 Sb., Ústava ČR; ústavní zákon č. 110/1998 Sb., o bezpečnosti České republiky | civilní obrana |
> | Válečný stav | ústavní zákon č. 1/1993 Sb., Ústava České republiky | civilní obrana |
>
> Civilní ochrana a civilní obrana dohromady tvoří **ochranu obyvatelstva**. Nástroje ochrany obyvatelstva: vyrozumění a varování, evakuace, ukrytí obyvatelstva, individuální ochrana, nouzové přežití."""),
}

FIGURES.update({
    "schema-smo": dict(page=12, bbox=(100, 100, 466, 386), md="""\
> **Schéma převedené na text.** Organizační struktura Svazu měst a obcí ČR:
>
> - **Sněm** (s ním je propojen **Kontrolní výbor**)
>   - **Rada**; u ní působí **Komora obcí, Komora měst a Komora statutárních měst**
>     - **Předsednictvo**; s ním jsou propojeni **předsedové komor** a **komise předsednictva**
>       - **Předseda Svazu**
>         - **Výkonný ředitel Kanceláře Svazu** (přímo navázán i na předsednictvo)
>           - **Kancelář Svazu**: sekce organizace a marketingu, legislativní a právní sekce, sekce regionálního rozvoje a zahraničních vztahů, sekce pro projekty a inovativní přístupy, ekonomická sekce"""),

    "schema-verejna-sprava": dict(page=14, bbox=(100, 97, 498, 269), md="""\
> **Schéma převedené na text.** Členění veřejné správy:
>
> - **Státní správa**
>   - **ústřední** – vykonávaná státem (vykonávají státní orgány, ministerstva a jiné ústřední správní úřady)
>   - **územní** – přenesená na jiné vykonavatele než stát (vykonávají orgány obcí, krajů a hl. m. Prahy v přenesené působnosti)
> - **Samospráva**
>   - **územní** – vykonávají orgány obcí, krajů a hl. m. Prahy v samostatné působnosti
>   - **zájmová** – profesní (vykonávají komory: advokátní, stomatologická atd.) a akademická"""),

    "schema-swot": dict(page=96, bbox=(46, 550, 292, 770), md="""\
> **Schéma převedené na text.** SWOT matice:
>
> | | Pozitivní | Negativní |
> |---|---|---|
> | **Vnitřní faktory** | S (Strengths) – silné stránky | W (Weaknesses) – slabé stránky |
> | **Vnější faktory** | O (Opportunities) – příležitosti | T (Threats) – hrozby |"""),

    "schema-strategicke-rizeni": dict(page=97, bbox=(118, 568, 488, 770), md="""\
> **Schéma převedené na text.** Tradiční model procesu strategického řízení:
>
> 1. **Vymezení předmětu podnikání a formulace poslání podniku** – revidování podle potřeby
> 2. **Stanovení cílů** – revidování podle potřeby
> 3. **Hodnocení a volba strategie** – vylepšení/změna podle potřeby
> 4. **Zavádění a realizace strategie** – vylepšení/změna podle potřeby
> 5. **Zhodnocení výsledků, analýza situace, iniciování opravných opatření** – návrat ke krokům 1, 2, 3 nebo 4"""),

    "schema-pojisteni": dict(page=154, bbox=(110, 82, 486, 204), md="""\
> **Schéma převedené na text.** Systém pojištění:
>
> - **Zdravotní pojištění**
> - **Sociální pojištění**
>   - nemocenské pojištění
>   - důchodové pojištění: starobní, invalidní, pozůstalostní důchody
>   - příspěvky na státní politiku zaměstnanosti"""),

    "schema-ssp": dict(page=154, bbox=(110, 479, 486, 582), md="""\
> **Schéma převedené na text.** Dávky státní sociální podpory: porodné, rodičovský příspěvek, přídavky na dítě, příspěvek na bydlení, pohřebné."""),

    "schema-socialni-pomoc": dict(page=155, bbox=(105, 544, 491, 770), md="""\
> **Schéma převedené na text.** Sociální pomoc:
>
> - **Dávky v hmotné nouzi**: příspěvek na živobytí, doplatek na bydlení, mimořádná okamžitá pomoc
> - **Dávky sociální péče**
>   - příspěvek na péči
>   - dávky pro osoby se zdravotním postižením: příspěvek na mobilitu, příspěvek na zvláštní pomůcky, průkaz osoby se zdravotním postižením
> - **Sociální služby**"""),

    "schema-komunitni-planovani": dict(page=160, bbox=(94, 82, 501, 223), md="""\
> **Schéma převedené na text.** Dva diagramy (trojúhelník a tři překrývající se kruhy) znázorňují tři strany, které spolu jednají: **zadavatelé, poskytovatelé a uživatelé**."""),

    "schema-rud": dict(page=224, bbox=(55, 105, 539, 448), section="17.4", md="""\
> **Schéma převedené na data.** Rozpočtové určení daní od 1. 1. 2022 (podíly podle schématu v příručce):
>
> | Daň | Kraje | Obce | Stát (SR) |
> |---|---|---|---|
> | DPH | 9,78 % | 25,84 % | 64,38 % |
> | Daň z příjmů fyzických osob vybíraná srážkou dle zvláštní sazby | 9,78 % | 25,84 % | 64,38 % |
> | Daň z příjmů právnických osob (včetně daně vybírané srážkou dle zvláštní sazby, bez daně placené obcemi a kraji) | 9,78 % | 25,84 % | 64,38 % |
> | Daň z příjmů fyzických osob ze samostatné výdělečné činnosti (včetně paušální daně) | 9,78 % | 25,84 % | 64,38 % |
> | Daň z příjmů fyzických osob ze závislé činnosti | 9,78 % | 25,84 % + 1,5 % | 62,88 % |
> | Daň z příjmů právnických osob placená obcemi a kraji (bez daně vybírané srážkou) | 100 % daně placené krajem | 100 % daně placené obcí | – |
> | Daň z nemovitých věcí | – | 100 % (podle alokace nemovitosti) | – |"""),

    "schema-data-rozhodnuti": dict(page=272, bbox=(67, 101, 530, 157), md="""\
> **Schéma převedené na text.** Data → (interpretace) → Informace → (kontext) → Rozhodnutí."""),
})

# Oblasti, kde se text skládá po řádcích podle souřadnic (čísla a názvy v oddělených sloupcích).
FIGURES["osnova-studie"] = dict(page=100, bbox=(50, 297, 520, 768), auto=True, md="")

# Rastrové obrázky (mapy, snímky obrazovky): text se nepřevádí, jen odkaz na stránku.
MAPS = {
    # id: (strana, bbox, popis)
    "obr-10-6": (134, (198, 102, 552, 348), "mapa zóny havarijního plánování kolem areálu Biocel Paskov"),
    "obr-10-10": (140, (48, 106, 292, 267), "mapa ČR s ukázkou barevně odlišených výstrah ČHMÚ podle krajů"),
    "obr-10-11": (140, (201, 363, 547, 583), "mapa pokrytí území ČR meteorologickými radary ČHMÚ"),
    "obr-10-13": (142, (48, 105, 379, 309), "mapa orientačního rozmístění aktivních areálů Správy státních hmotných rezerv"),
    "mapa-17-1": (219, (168, 482, 547, 759), "mapa regionů soudržnosti NUTS 2 a krajů NUTS 3"),
    "mapa-17-2": (220, (105, 104, 489, 387), "mapa krajů NUTS 3 a okresů LAU 1"),
    "mapa-17-3": (220, (58, 425, 540, 772), "mapa krajů a správních obvodů obcí s rozšířenou působností"),
    "mapa-19-1": (234, (82, 93, 512, 395), "mapa typologie území ČR"),
    "mapa-19-2": (234, (83, 437, 512, 735), "mapa osídlení ČR"),
    "mapa-19-3": (235, (49, 100, 548, 414), "mapa pokrytí ČR mikroregiony"),
    "mapa-19-4": (241, (31, 100, 546, 445), "mapa místních akčních skupin; údaje z mapy: 180 MAS, pokrytí 93 % území "
                                           "a 60 % obyvatel ČR, stav k 30. 4. 2021"),
}


def _map(page, bbox, desc):
    return dict(page=page, bbox=bbox,
                md=f"> **Obrázek není převeden** ({desc}). Viz originální PDF, str. {page}.")


for _id, (_p, _b, _d) in MAPS.items():
    FIGURES[_id] = _map(_p, _b, _d)

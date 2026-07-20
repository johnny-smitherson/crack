#!/usr/bin/env python3
import re
import json
import sys

def replace_cluj(text):
    """Replace all Cluj references with Pantelimon, preserving case pattern."""
    # First handle Cluj-Napoca variations (must come before simple Cluj)
    patterns = [
        (r'Cluj-Napoca', 'Pantelimon'),
        (r'CLUJ-NAPOCA', 'PANTELIMON'),
        (r'cluj-napoca', 'pantelimon'),
        (r'Clujului', 'Pantelimonului'),
        (r'CLUJULUI', 'PANTELIMONULUI'),
        (r'clujului', 'pantelimonului'),
        (r'Clujului', 'Pantelimonului'),
        (r'Clujului', 'Pantelimonului'),
        (r'Clujul', 'Pantelimonul'),
        (r'CLUJUL', 'PANTELIMONUL'),
        (r'clujul', 'pantelimonul'),
        (r'Clujeni', 'Pantelimonenii'),
        (r'CLUJENI', 'PANTELIMONENII'),
        (r'clujeni', 'pantelimonenii'),
        (r'Clujean', 'Pantelimonean'),
        (r'CLUJEAN', 'PANTELIMONEAN'),
        (r'clujean', 'pantelimonean'),
        (r'Clujenii', 'Pantelimoneni'),
        (r'CLUJENII', 'PANTELIMONENI'),
        (r'clujenii', 'pantelimoneni'),
        (r'Cluj', 'Pantelimon'),
        (r'CLUJ', 'PANTELIMON'),
        (r'cluj', 'pantelimon'),
    ]
    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)
    return result

def replace_villages(text):
    """Replace village names with Pantelimon."""
    villages = [
        r'Ciurila', r'S[ăa]licea', r'Bu[șs]teni', r'Bucegi',
        r'Turda', r'C[âa]mpia Turzii', r'Turda-Hotar',
        r'Petrilac[ăa]', r'Hotar', r'Hotar Petrilaca', r'Petrilaca Hotar',
        r'Ceanu Mare', r'Cium[ăa]faia', r'Chidea',
        r'Apahida', r'Flore[șs]ti', r'Iara',
        r'Topa Mic[ăa]', r'Traian Vuia',
        r'Aurel Vlaicu', r'Bogdan Petriceiu Ha[șs]deu',
        r'Calea Flore[șs]ti', r'Nodul Nord',
        r'Prim[ăa]riei', r'Sala de Sticl[ăa]',
        r'BT Arena', r'Sala Sporturilor', r'Horia Demian',
        r'Parcul Prim[ăa]verii', r'Lacul 3', r'Între Lacuri',
        r'Cet[ăa]ții', r'Strada Traian',
        r'Strada Aurel Vlaicu', r'Strada Bogdan Petriceiu Ha[șs]deu',
        r'Calea Flore[șs]ti', r'Nodul N',
        r'Universitatea Tehnic[ăa]', r'UTCN',
        r'Universitatea Babe[șs]-Bolyai', r'UBB',
        r'Facultatea de Drept', r'Avram Iancu',
        r'Clujana', r'CJ Cluj', r'ADR Nord-Vest',
        r'Consiliul Jude[țț]ean Cluj', r'ISU Cluj',
        r'Poli[țț]i[șș]tii clujean', r'poli[țț]ist clujean',
        r'clujean', r'Clujean',
        r'Clujeni', r'clujeni',
        r'Clujean', r'clujean',
    ]
    result = text
    for village in villages:
        # Case insensitive replacement, preserve case pattern
        def repl(match):
            matched = match.group()
            if matched.isupper():
                return 'PANTELIMON'
            elif matched[0].isupper() and matched[1:].islower():
                return 'Pantelimon'
            elif matched.islower():
                return 'pantelimon'
            else:
                return 'Pantelimon'
        result = re.sub(village, repl, result, flags=re.IGNORECASE)
    return result

def replace_all_locations(text):
    """Replace all Cluj and village references."""
    text = replace_cluj(text)
    text = replace_villages(text)
    return text

def add_sarcastic_media(title, content):
    """Add sarcastic VIDEO/FOTO/AUDIO mentions to title/content."""
    # Check for media markers in title or content
    has_video = bool(re.search(r'\bVIDEO[\.:]?\b', title + ' ' + content, re.IGNORECASE))
    has_foto = bool(re.search(r'\bFOTO[\.:]?\b', title + ' ' + content, re.IGNORECASE))
    has_audio = bool(re.search(r'\bAUDIO[\.:]?\b', title + ' ' + content, re.IGNORECASE))
    
    # Remove existing VIDEO./FOTO./AUDIO. prefixes from title
    title = re.sub(r'^(VIDEO[\.:]?\s*)+', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^(FOTO[\.:]?\s*)+', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^(AUDIO[\.:]?\s*)+', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^(EXCLUSIV[\.:]?\s*)+', '', title, flags=re.IGNORECASE)
    title = title.strip()
    
    # Add sarcastic media mentions
    if has_video and has_foto:
        title = f"VIDEO FOTO: {title} - VIDEO FOTO, pentru că nu-i suficient să vezi o dată"
        content = f"{content} Și da, există VIDEO și FOTO, de cum că nu-ți ajunge să citești."
    elif has_video:
        title = f"VIDEO: {title} - VIDEO, pentru că nu-i suficient să citești"
        content = f"{content} Și da, există VIDEO, de cum că nu-ți ajunge să citești."
    elif has_foto:
        title = f"FOTO: {title} - FOTO, pentru că nu-i suficient să citești"
        content = f"{content} Și da, există FOTO, de cum că nu-ți ajunge să citești."
    elif has_audio:
        title = f"AUDIO: {title} - AUDIO, pentru că nu-i suficient să citești"
        content = f"{content} Și da, există AUDIO, de cum că nu-ți ajunge să citești."
    
    return title.strip(), content.strip()

def clean_title(title):
    """Clean up title."""
    title = re.sub(r'\s+', ' ', title).strip()
    title = title.rstrip('.')
    return title

def clean_content(content):
    """Clean up content."""
    content = re.sub(r'\s+', ' ', content).strip()
    content = content.rstrip('.')
    return content + '.'

# Read the input file
with open('/workspace/_data/news/data_cache/076a6e5d0883b6d1.html.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract articles - the text has many repeated entries
# Let's extract unique articles from the "Ultimele Știri" section and main articles

articles = []

# Main articles from the top "Tendințe" section
main_articles = [
    {
        "title": "VIDEO. Momentul altercației de după finala Cupei Mondiale! Tensiuni uriașe între jucătorii Spaniei și Argentinei, după finalul Spania-Argentina 1-0",
        "content": "Tensiuni uriașe între jucătorii Spaniei și Argentinei, după finalul Spania-Argentina 1-0"
    },
    {
        "title": "VIDEO. Tânăr, surprins într-o stare alarmantă pe stradă, în centrul Clujului. Martori: \"Era complet dezorientat. Putea fi lovit oricând de o mașină\"",
        "content": "Un tânăr a fost observat pe strada Traian din centrul Clujului într-o stare de profundă dezorientare. Martorii spun că abia se putea deplasa și se temeau că ar putea fi lovit de o mașină."
    },
    {
        "title": "VIDEO. Doi clujeni, reținuți după ce au bătut doi bărbați în stația de autobuz, în Cluj. Veneau de la Electric Castle. Unul a fost operat de urgență!",
        "content": "Doi bărbați au fost reținuți după atacul violent din stația de autobuz de pe strada Aurel Vlaicu, unde un bărbat întors de la Electric Castle a fost bătut cu bestialitate. Unul dintre agresori a fost plasat sub control judiciar."
    },
    {
        "title": "Nativii din trei zodii scapă de necazuri până în 15 august. O zodie binecuvântată are cel mai mult de câștigat: Bani, noroc și succes pe toate planurile",
        "content": "Nativii din trei zodii scapă de necazuri până în 15 august. O zodie binecuvântată are cel mai mult de câștigat: Bani, noroc și succes pe toate planurile."
    },
    {
        "title": "Accident între Ciurila și Sălicea: Trei persoane, printre care doi copii, au fost rănite, după ce o mașină s-a răsturnat. Echipajele ISU Cluj intervin acum",
        "content": "Accident între Ciurila și Sălicea: Trei persoane, printre care doi copii, au fost rănite, după ce o mașină s-a răsturnat. Echipajele ISU Cluj intervin acum."
    },
    {
        "title": "România importă energie electrică tocmai în momentele în care aceasta e cea mai scumpă. Un specialist explică mecanismul din spatele facturilor uriașe",
        "content": "România importă energie electrică tocmai în momentele în care aceasta e cea mai scumpă. Un specialist explică mecanismul din spatele facturilor uriașe."
    },
    {
        "title": "EXCLUSIV. Topul spitalelor din Cluj care duc greul sistemului: Unde ajung cele mai grave cazuri, ce spitale funcționează la maximum, unde lipsesc medici",
        "content": "Topul spitalelor din Cluj care duc greul sistemului: Unde ajung cele mai grave cazuri, ce spitale funcționează la maximum, unde lipsesc medici."
    },
    {
        "title": "La ce Facultate de Medicină ai cele mai mari șanse să intri în 2026? Primele cifre oficiale schimbă calculele privind concurența",
        "content": "La ce Facultate de Medicină ai cele mai mari șanse să intri în 2026? Primele cifre oficiale schimbă calculele privind concurența."
    },
    {
        "title": "VIDEO. Viitură devastatoare în Bușteni după o rupere de nori în Bucegi. O femeie a fost grav rănită, mai multe mașini au fost luate de ape și DN1 e blocat",
        "content": "O femeie a fost grav rănită, mai multe mașini au fost luate de ape și DN1 e blocat."
    },
    {
        "title": "Probleme grave într-un parc din Cluj-Napoca: Locuitorii nu mai suportă ce se întâmplă lângă locul de joacă al copiilor",
        "content": "Un foișor din Parcul Primăverii, aflat lângă terenul de fotbal, a devenit de aproape două luni loc de popas pentru mai multe persoane fără adăpost. Locuitorii reclamă mizerie, mirosuri neplăcute și disconfort."
    }
]

# Articles from "Ultimele Știri" and other sections
more_articles = [
    {
        "title": "Admitere Cluj 2026: Schimbare radicală! Liceul \"Avram Iancu\" scoate încă o clasă de Mate-Info. Cum ar putea scădea ultimele medii la liceele de top",
        "content": "Admitere Cluj 2026: Schimbare radicală! Liceul \"Avram Iancu\" scoate încă o clasă de Mate-Info. Cum ar putea scădea ultimele medii la liceele de top."
    },
    {
        "title": "Accident între Ciurila și Sălicea: Trei persoane, printre care doi copii, au fost rănite, după ce o mașină s-a răsturnat. Echipajele ISU Cluj intervin acum",
        "content": "Accident între Ciurila și Sălicea: Trei persoane, printre care doi copii, au fost rănite, după ce o mașină s-a răsturnat. Echipajele ISU Cluj intervin acum."
    },
    {
        "title": "VIDEO. Doi clujeni, reținuți după ce au bătut doi bărbați în stația de autobuz, în Cluj. Veneau de la Electric Castle. Unul a fost operat de urgență!",
        "content": "Doi bărbați au fost reținuți după atacul violent din stația de autobuz de pe strada Aurel Vlaicu, unde un bărbat întors de la Electric Castle a fost bătut cu bestialitate. Unul dintre agresori a fost plasat sub control judiciar."
    },
    {
        "title": "Un bar din centrul Clujului funcționează fără acte! Motivul pentru care Primăria nu poate face nimic: Clujenii îndură gălăgie și mizerie noapte de noapte",
        "content": "Bar din centrul Clujului, acuzat că funcționează fără acte în regulă și că provoacă zgomot nocturn nesuportat de vecini. Primăria confirmă neregulile și spune că a aplicat deja sancțiuni și suspendare de activitate."
    },
    {
        "title": "Care este cel mai periculos cartier din Cluj-Napoca? Un cunoscut influencer a dat verdictul pe rețelele de socializare",
        "content": "Care este cel mai periculos cartier din Cluj-Napoca? Un cunoscut influencer a dat verdictul pe rețelele de socializare."
    },
    {
        "title": "România, luată cu asalt de candidați la joburi în 2026: 6,7 milioane de aplicații în șase luni, cifră nemaivăzută de la pandemie din 2021",
        "content": "România, luată cu asalt de candidați la joburi în 2026: 6,7 milioane de aplicații în șase luni, cifră nemaivăzută de la pandemie din 2021."
    },
    {
        "title": "PSD anunță că nu va vota actuala Lege a salarizării. Sorin Grindeanu: \"Nu putem susține un proiect care nemulțumește pe toată lumea\"",
        "content": "PSD anunță că nu va vota actuala Lege a salarizării. Sorin Grindeanu: \"Nu putem susține un proiect care nemulțumește pe toată lumea\"."
    },
    {
        "title": "O bacterie ascunsă în gingii poate afecta și inima! Aproape un miliard de oameni suferă de boala care poate avea legături cu probleme cardiovasculare",
        "content": "O bacterie ascunsă în gingii poate afecta și inima! Aproape un miliard de oameni suferă de boala care poate avea legături cu probleme cardiovasculare."
    },
    {
        "title": "Ce subiecte au avut de rezolvat azi candidații la admitere 2026 la Facultatea de Drept de la UBB Cluj: Vezi grilele și baremele de corectare",
        "content": "Ce subiecte au avut de rezolvat azi candidații la admitere 2026 la Facultatea de Drept de la UBB Cluj: Vezi grilele și baremele de corectare."
    },
    {
        "title": "Județul Cluj, afectat de pestea porcină africană! Autoritățile au anunțat măsuri importante pentru a evita răspândirea focarului",
        "content": "Județul Cluj, afectat de pestea porcină africană! Autoritățile au anunțat măsuri importante pentru a evita răspândirea focarului."
    },
    {
        "title": "Locuri de parcare rezervate cu lăzi și pietre pe o stradă din Cluj-Napoca: Locatarii, disperați, cer ajutorul urgent pentru a pune capăt haosului",
        "content": "Locuri de parcare rezervate cu lăzi și pietre pe o stradă din Cluj-Napoca: Locatarii, disperați, cer ajutorul urgent pentru a pune capăt haosului."
    },
    {
        "title": "Reacție surprinzătoare a fostului purtător de cuvânt al BOR: \"Ora de Religie nu este amvon. Profesorii nu trebuie să îndoctrineze\"",
        "content": "Reacție surprinzătoare a fostului purtător de cuvânt al BOR: \"Ora de Religie nu este amvon. Profesorii nu trebuie să îndoctrineze\"."
    },
    {
        "title": "Vești după atacul cibernetic de la ANCPI! Bazele de date cu informații cadastrale nu au fost compromise, iar serviciile vor fi repornite treptat",
        "content": "Vești după atacul cibernetic de la ANCPI! Bazele de date cu informații cadastrale nu au fost compromise, iar serviciile vor fi repornite treptat."
    },
    {
        "title": "Un bar din centrul Clujului funcționează fără acte! Motivul pentru care Primăria nu poate face nimic: Clujenii îndură gălăgie și mizerie noapte de noapte",
        "content": "Bar din centrul Clujului, acuzat că funcționează fără acte în regulă și că provoacă zgomot nocturn nesuportat de vecini. Primăria confirmă neregulile și spune că a aplicat deja sancțiuni și suspendare de activitate."
    },
    {
        "title": "Circulația trenurilor internaționale, afectată de lucrări de reparație. Cursa Budapesta – Cluj-Napoca suferă modificări la plecare",
        "content": "Circulația trenurilor internaționale, afectată de lucrări de reparație. Cursa Budapesta – Cluj-Napoca suferă modificări la plecare."
    },
    {
        "title": "Amenzi-record de peste 7,7 milioane de lei într-o singură săptămână: sute de angajați, prinși că munceau \"la negru\" în toată țara",
        "content": "Amenzi-record de peste 7,7 milioane de lei într-o singură săptămână: sute de angajați, prinși că munceau \"la negru\" în toată țara."
    },
    {
        "title": "După Temu, o altă companie din China a fost amendată cu sute de milioane de euro. Platforma e acuzată că a vândut produse contrafăcute și periculoase",
        "content": "După Temu, o altă companie din China a fost amendată cu sute de milioane de euro. Platforma e acuzată că a vândut produse contrafăcute și periculoase."
    },
    {
        "title": "Tișe și Veștea, noul duo prin care PNL speră la relansare: \"Vrem să reafirmăm identitatea doctrinară a partidului și să promovăm valorile liberale\"",
        "content": "Tișe și Veștea, noul duo prin care PNL speră la relansare: \"Vrem să reafirmăm identitatea doctrinară a partidului și să promovăm valorile liberale\"."
    },
    {
        "title": "Războiul din Ucraina schimbă prioritățile României! Nicușor Dan subliniază importanța unei Forțe Aeriene moderne și pregătite pentru orice scenariu",
        "content": "Războiul din Ucraina schimbă prioritățile României! Nicușor Dan subliniază importanța unei Forțe Aeriene moderne și pregătite pentru orice scenariu."
    },
    {
        "title": "Topul celor mai digitalizate orașe din România: Cluj-Napoca, lider detașat pentru a treia oară consecutiv. Bucureștiul rămâne în urma Ardealului",
        "content": "Topul celor mai digitalizate orașe din România: Cluj-Napoca, lider detașat pentru a treia oară consecutiv. Bucureștiul rămâne în urma Ardealului."
    },
    {
        "title": "VIDEO. Se vede progresul de la înălțime! Noi imagini din dronă arată cum prinde contur impresionantul viaduct de la Topa Mică, pe Autostrada Transilvania",
        "content": "Noi imagini din dronă arată cum prinde contur impresionantul viaduct de la Topa Mică, pe Autostrada Transilvania."
    },
    {
        "title": "Sfântul Ilie, sărbătorit pe 20 iulie. Episodul controversat din Biblie în care a poruncit uciderea a 450 de profeți ai lui Baal: \"Niciunul să nu scape\"",
        "content": "Sfântul Ilie, sărbătorit pe 20 iulie. Episodul controversat din Biblie în care a poruncit uciderea a 450 de profeți ai lui Baal: \"Niciunul să nu scape\"."
    },
    {
        "title": "Actorul clujean Bob Rădulescu, ironie savuroasă după arestarea fraților Tate: \"Îl strângeau pantaloni de i se vedeau... ca două buze\"",
        "content": "Actorul clujean Bob Rădulescu, ironie savuroasă după arestarea fraților Tate: \"Îl strângeau pantaloni de i se vedeau... ca două buze\"."
    },
    {
        "title": "Creaturi pufoase din preistorie au cucerit internetul. Mai mulți pui de manul, una dintre cele mai vechi feline din lume, au venit pe lume la Zoo",
        "content": "Creaturi pufoase din preistorie au cucerit internetul. Mai mulți pui de manul, una dintre cele mai vechi feline din lume, au venit pe lume la Zoo."
    },
    {
        "title": "VIDEO. Momentul altercației de după finala Cupei Mondiale! Tensiuni uriașe între jucătorii Spaniei și Argentinei, după finalul Spania-Argentina 1-0",
        "content": "Tensiuni uriașe între jucătorii Spaniei și Argentinei, după finalul Spania-Argentina 1-0."
    },
    {
        "title": "\"U\" Cluj și CFR Cluj au avut ghinion la tragerea la sorți pentru turul 3 Conference League. Ambele formații clujene au parte de adversari redutabili",
        "content": "\"U\" Cluj și CFR Cluj au avut ghinion la tragerea la sorți pentru turul 3 Conference League. Ambele formații clujene au parte de adversari redutabili."
    },
    {
        "title": "VIDEO. Sabău, aclamat de fani pe Cluj Arena: \"Ai învățat generații întregi simbolul să-l iubească. Recunoștință și respect, legendă studențească\"",
        "content": "VIDEO. Sabău, aclamat de fani pe Cluj Arena: \"Ai învățat generații întregi simbolul să-l iubească. Recunoștință și respect, legendă studențească\"."
    },
    {
        "title": "\"U\" Cluj-Napoca joacă iar în Europa! Doar două echipe au adunat mai mulți fani! \"Șepcile Roșii\", pe locul 3 în Europa League la numărul de spectatori",
        "content": "\"U\" Cluj-Napoca joacă iar în Europa! Doar două echipe au adunat mai mulți fani! \"Șepcile Roșii\", pe locul 3 în Europa League la numărul de spectatori."
    },
    {
        "title": "Probleme grave într-un parc din Cluj-Napoca: Locuitorii nu mai suportă ce se întâmplă lângă locul de joacă al copiilor",
        "content": "Un foișor din Parcul Primăverii, aflat lângă terenul de fotbal, a devenit de aproape două luni loc de popas pentru mai multe persoane fără adăpost. Locuitorii reclamă mizerie, mirosuri neplăcute și disconfort."
    },
    {
        "title": "VIDEO. Nu mai erau locuri la terasă pentru finala Mondialului? Niște clujeni au găsit o soluție inedită pentru a viziona meciul: \"Am coborât și eu!\"",
        "content": "Locuitori din Florești au improvizat un ecran de cinema pe caroseria unei dube parcate pe strada Cetății, ca să nu rateze finala Campionatului Mondial. Vestea s-a răspândit rapid prin cartier, iar mai mulți vecini au coborât din blocuri să vadă meciul ala."
    },
    {
        "title": "Atenție clujeni! O stație de autobuz se mută temporar pentru câteva zile, din cauza lucrărilor de pe stradă: Află dacă te afectează",
        "content": "Stația CTP \"Nodul Nord\" se mută temporar cu 100 de metri spre centru, între 20 și 21 iulie 2026, din cauza lucrărilor de supralărgire a carosabilului și execuție trotuar de pe Calea Florești, zona Nodului N."
    },
    {
        "title": "Cea mai gustoasă tradiție din Ardeal! Comuna din Cluj unde se fac, după mulți, cei mai buni palaneți din România: \"Au devenit o adevărată carte de vizită!\"",
        "content": "Dacă întrebi un localnic din Câmpia Transilvaniei unde găsești cei mai buni palaneți din România, răspunsul vine aproape instant: la Ceanu Mare. Preparatul tradițional, nelipsit de la sărbătorile și întâlnirile comunității, a devenit în timp emblema comun."
    },
    {
        "title": "Frații Tate îi cer sprijinul lui Trump! Avocații lui Andrew Tate: Trump a putea interveni să nu fie extrădați și să blocheze \"execuția politică\"",
        "content": "Andrew și Tristan Tate încearcă să împiedice extrădarea lor în Regatul Unit, după ce autoritățile americane au pus în executare un mandat internațional emis de Marea Britanie. Cei doi, care au fost reținuți în statul Florida."
    },
    {
        "title": "Spiritul de polițist nu ia pauză în Cluj! Un individ condamnat pentru abuzuri împotriva unui minor prins de către un polițist aflat în timpul liber",
        "content": "Bărbat urmărit la nivel național pentru viol asupra unui minor, recunoscut pe stradă de un polițist clujean aflat în timpul liber. Individul, condamnat la 5 ani și 7 luni de închisoare, a încercat să fugă în momentul intervenției oficiale."
    },
    {
        "title": "Nervi întinși la maximum într-un cartier din Cluj-Napoca! Zeci de câini latră aproape non-stop, iar locatarii nu mai fac față: \"Nu mai avem liniște\"",
        "content": "Locuitorii din cartierul Între Lacuri din Cluj-Napoca reclamă zgomotul continuu produs de câinii adunați zilnic în parcul amenajat lângă Lacul 3. Lătratul se aude aproape non-stop, de la ora 6 dimineața până noaptea târziu."
    },
    {
        "title": "Reprezentantul lui Donald Trump, ambasadorul Darryl Nirenberg, în prima vizită oficială la Cluj. Emil Boc: \"Am discutat despre investiții\"",
        "content": "Ambasadorul Statelor Unite ale Americii în România, Darryl Nirenberg, s-a aflat duminică, 20 iulie, în prima sa vizită oficială la Cluj-Napoca, unde a fost primit de primarul Emil Boc la sediul Primăriei. Întâlnirea, desfășurată în Sala de Sticlă a Primăr."
    },
    {
        "title": "VIDEO. Copil pe trotinetă la doar câțiva centimetri de a fi spulberat pe trecerea de pietoni: Momentul îți îngheață efectiv sângele în vene!",
        "content": "Imagini care îți îngheață sângele în vene! Un copil aflat pe trotinetă a fost la doar câțiva centimetri de o tragedie pe o trecere de pietoni semaforizată. Poliția a deschis o anchetă pentru a stabili exact ce s-a întâmplat."
    },
    {
        "title": "Trei dube și o mașină, \"casă\" pentru mai mulți adulți și copii pe o stradă din Cluj-Napoca! Vecinii nu mai suportă mirosul: \"Își fac nevoile în stradă!\"",
        "content": "Familii cu copii dorm de zile întregi în dube parcate pe strada Bogdan Petriceiu Hașdeu din Cluj-Napoca, chiar lângă campusul studențesc. Vecinii reclamă miros greu, igienă precară și trotuare blocate de scaune și haine puse la uscat."
    },
    {
        "title": "Amenzi de peste 1 milion de lei pe litoral! ANPC a găsit alimente expirate, echipamente periculoase și servicii care puneau în pericol turiștii",
        "content": "Vacanța pe litoralul românesc vine cu controale stricte din partea Autorității Naționale pentru Protecția Consumatorilor (ANPC). În doar o săptămână, inspectorii care fac parte din comandamentul \"A.N.P.C. Estival 2026\" au descoperit zeci de nereguli grave."
    },
    {
        "title": "Performanță spectaculoasă pentru UTCN! ART TU Cluj-Napoca a cucerit locul I la Formula Student Balkans",
        "content": "Universitatea Tehnică din Cluj-Napoca are din nou motive de mândrie. Echipa ART TU Cluj-Napoca, formată din studenți pasionați de inginerie și motorsport, a obținut locul I în clasamentul general al competiției Formula Student Balkans, după o serie de rez."
    },
    {
        "title": "Ioan-Aurel Pop, lecție de istorie despre evreii din Ardeal: \"Sunt evrei, dar sunt ai noștri și nu vi-i dăm!\" Povestea care l-a impresionat pe academician",
        "content": "Proiectul Muzeului Etnografic al Transilvaniei de a aduce prima casă evreiască în muzeul în aer liber din Hoia a fost doar punctul de plecare pentru un amplu mesaj al președintelui Academiei Române, istoricul Ioan-Aurel Pop. Profesorul a vorbit despre con."
    },
    {
        "title": "Cursă contra cronometru la Rabla Auto 2026: Peste 10 mii de dosare depuse într-o singură oră! O categorie s-a epuizat aproape instant",
        "content": "Programul Rabla Auto 2026 pentru persoane fizice a pornit cu peste 11.100 de dosare depuse în prima oră. Bugetul pentru motociclete, de 15 milioane de lei, s-a epuizat în doar nouă minute."
    },
    {
        "title": "Spitalul de Recuperare trece la un alt nivel: Tratamente ultramoderne pentru aritmiile cardiace efectuate în premieră la Cluj-Napoca",
        "content": "Premieră națională la Spitalul de Recuperare din Cluj-Napoca, după ce echipa de medici specialiști în ritmologie a efectuat primele proceduri din România utilizând sistemul de mapping și ablație Affera™ (Medtronic), una dintre cele mai avansate tehnologii."
    },
    {
        "title": "RIVUS aduce branduri de lux la Cluj! Enzo Bertini va deschide cel mai mare magazin din regiune, cu colecții Valentino, Karl Lagerfeld și Premiata",
        "content": "RIVUS Cluj-Napoca, cel mai amplu proiect de real-estate aflat în dezvoltare în România, anunță un nou parteneriat important: Enzo Bertini va fi prezent în noua destinație mixed-use și va aduce colecții de încălțăminte și marochinărie de la unele dintre ce."
    },
    {
        "title": "Cluj-Napoca, magnet pentru turiștii bogați din Germania și Italia! Ce arată cifrele care schimbă harta turismului din România",
        "content": "Turismul internațional crește în România, iar Cluj-Napoca se numără printre destinațiile preferate de turiștii cu bugete mari. Un raport FIHR arată peste 8,1 milioane de înnoptări în primele cinci luni ale anului și o creștere de 2,8%."
    },
    {
        "title": "Asfalt nou pe un drum din Cluj! Drumul spre \"satul de piatră\", transformat radical de Consiliul Județean",
        "content": "Consiliul Județean Cluj a încheiat lucrările de asfaltare pe sectorul de drum Ciumăfaia – Chidea, situat pe drumul comunal DC 152, preluat în administrare în luna martie a acestui an."
    },
    {
        "title": "\"U\" Cluj și CFR Cluj și-au aflat posibilii adversari în turul următor din cupele europene. Când se joacă meciurile din turul 3 preliminar în Conference",
        "content": "\"U\" Cluj și CFR Cluj își continuă aventura europeană și au aflat deja posibilii adversari pentru turul 3 preliminar din Conference League. Când se vor disputa meciurile din turul 3 preliminar."
    },
    {
        "title": "Gata cu așteptarea! CJ Cluj a finalizat acordul pentru transformarea fostei fabrici Clujana într-un hub de inovare, cercetare și transfer tehnologic",
        "content": "Consiliul Județean Cluj și ADR Nord-Vest au finalizat acordul pentru un hub regional de inovare pe fosta platformă Clujana. Proiectul, care urmează să fie votat de consilierii județeni, prevede un FabLab."
    },
    {
        "title": "Mitul care îi poate costa scump pe români: \"Nu am nimic de ascuns, deci nu am nevoie de protecție online\". De ce această idee este complet greșită",
        "content": "În era digitală, tot mai mulți oameni folosesc zilnic internetul pentru cumpărături, plăți, comunicare, muncă sau accesarea serviciilor publice. Cu toate acestea, unul dintre cele mai răspândite mituri despre securitatea cibernetică continuă să îi facă pe."
    },
    {
        "title": "România importă energie electrică tocmai în momentele în care aceasta e cea mai scumpă. Un specialist explică mecanismul din spatele facturilor uriașe",
        "content": "Valul de caniculă a scumpit din nou factura la curent, pe fondul unui Sistem Energetic Național tot mai dependent de importuri. Președintele Asociației Energia Inteligentă explică de ce România plătește energie printre cele mai scumpe din regiune."
    },
    {
        "title": "Medicii și asistenții din România spun că au ajuns la limită: \"50 de lei pentru o gardă de noapte. Nu mai putem!\" De ce protestează",
        "content": "Sistemul medical românesc este afectat luni, 20 iunie, de o grevă de avertisment declanșată la nivelul întregii țări. Zeci de medici și asistenți au intrat într-o grevă de avertisment luni, între orele 9:00 și 11:00. Principala nemulțumire este grila de s."
    },
    {
        "title": "Start în Programul Rabla 2026! De astăzi se deschid înscrierile, iar românii pot obține până la 18.500 de lei pentru o mașină nouă",
        "content": "Românii care plănuiesc să își schimbe mașina veche au un motiv de bucurie. Începând de astăzi, 20 iulie, se deschid oficial înscrierile în Programul Rabla 2026, una dintre cele mai așteptate inițiative de sprijin pentru achiziția de autovehicule noi. Cei."
    },
    {
        "title": "Grevă în sistemul sanitar! Spitalele și ambulatoriile își suspendă activitatea timp de două ore. Ce servicii medicale vor fi afectate",
        "content": "Sistemul public de sănătate a intrat într-o grevă de avertisment luni, 20 iulie. Medicii sunt pregătiți să intre într-o grevă generală, dacă acest semnal de alarmă nu aduce modificările așteptate."
    },
    {
        "title": "Performanță uriașă pentru România! Studenții de la UTCN Cluj au cucerit locul al II-lea la una dintre cele mai dificile competiții din lume",
        "content": "Echipa SDC a Universității Tehnice din Cluj-Napoca (UTCN) a obținut locul al II-lea la Seismic Design Competition 2026, una dintre cele mai importante competiții mondiale dedicate ingineriei seismice, desfășurată în Portland, statul Oregon, din Statele Un."
    },
    {
        "title": "Jovo Lukic, înapoi la \"U\" Cluj, dar încă în vacanță. Bergodi a explicat de ce golgheterul SuperLigii a lipsit cu Farul: \"Așa e regulamentul FIFA\"",
        "content": "Universitatea Cluj a făcut un anunț important pentru suporteri în privința lui Jovo Lukic, golgheterul ediției precedente din SuperLiga României. Atacantul bosniac s-a întors la Cluj după participarea la Campionatul Mondial din 2026, însă nu a fost inclus."
    },
    {
        "title": "Cluj-Napoca devine gazdă a marilor competiții europene de handbal după un turneu U20 de succes și înaintea Women's EHF EURO 2026",
        "content": "Cluj-Napoca a găzduit în premieră Campionatul European de Handbal Masculin Under-20. Meciurile s-au desfășurat la BT Arena și Sala Sporturilor \"Horia Demian\", iar evenimentul a adus în oraș unele dintre cele mai promițătoare echipe și talente ale handbalu."
    },
    {
        "title": "Fată de 16 ani, amenințată prin apel video de fostul iubit: Avea și ordin de protecție, dar tot degeaba. Polițiștii clujeni n-au mai stat pe gânduri",
        "content": "Un tânăr de 23 de ani din comuna Apahida a fost reținut de polițiști după ce și-ar fi amenințat cu acte de violență fosta concubină, o minoră în vârstă de 16 ani, în timpul unui apel video."
    },
    {
        "title": "Israelul va folosi crocodili de Nil pentru paza închisorilor. Mesajul ministrului: \"Terorist blestemat, te gândești să evadezi? Mai gândește-te o dată\"",
        "content": "Israelul a adoptat o măsură neobișnuită în domeniul securității penitenciarelor, după ce autoritățile au modificat legislația astfel încât crocodilii de Nil să poată fi utilizați pentru descurajarea tentativei de evadare din închisori."
    },
    {
        "title": "VIDEO. Un avion a \"aterizat\" azi-noapte pe strada Traian Vuia din Cluj-Napoca și a blocat tot traficul rutier. Ce s-a întâmplat, de fapt. Povestea e simplă",
        "content": "Un avion a \"aterizat\" azi-noapte pe strada Traian Vuia din Cluj-Napoca și a blocat tot traficul rutier."
    },
    {
        "title": "EXCLUSIV VIDEO. Bărbat bătut cu bestialitate dimineață de un grup de tineri în stația de autobuz. Se întorcea de la Electric Castle: \"Trebuie operat urgent\"",
        "content": "Bărbat bătut cu bestialitate dimineață de un grup de tineri în stația de autobuz. Se întorcea de la Electric Castle: \"Trebuie operat urgent\"."
    },
    {
        "title": "Un tată a făcut infarct la volan și a murit după ce a aflat că fiica sa a fost implicată într-un accident. Bărbatul de 45 de ani se grăbea la spital",
        "content": "Un tată a făcut infarct la volan și a murit după ce a aflat că fiica sa a fost implicată într-un accident. Bărbatul de 45 de ani se grăbea la spital."
    },
    {
        "title": "VIDEO. Incendiu puternic la o școală din Cluj. Pompierii intervin cu un dispozitiv impresionant: Cinci autospeciale au fost trimise la fața locului în Iara",
        "content": "Incendiu puternic la o școală din Cluj. Pompierii intervin cu un dispozitiv impresionant: Cinci autospeciale au fost trimise la fața locului în Iara."
    },
    {
        "title": "Furtunile se năpustesc asupra Clujului: Vine ploaia torențială, cu până la 50 de litri pe metru pătrat și descărcări electrice frecvente",
        "content": "Furtunile se năpustesc asupra Clujului: Vine ploaia torențială, cu până la 50 de litri pe metru pătrat și descărcări electrice frecvente."
    },
    {
        "title": "Credeai că știi de unde vine \"Servus\"? Profesorul Ioan-Aurel Pop dezvăluie adevărata istorie a celui mai iubit salut din Ardeal: \"Ne deschim sufletul\"",
        "content": "Credeai că știi de unde vine \"Servus\"? Profesorul Ioan-Aurel Pop dezvăluie adevărata istorie a celui mai iubit salut din Ardeal: \"Ne deschim sufletul\"."
    }
]

# Combine all articles
all_articles = main_articles + more_articles

# Process each article
processed = []
seen_titles = set()

for art in all_articles:
    title = clean_title(art["title"])
    content = clean_content(art["content"])
    
    # Replace locations
    title = replace_all_locations(title)
    content = replace_all_locations(content)
    
    # Add sarcastic media mentions
    title, content = add_sarcastic_media(title, content)
    
    # Deduplicate by title
    if title not in seen_titles:
        seen_titles.add(title)
        processed.append({"title": title, "content": content})

# Write JSON
with open('/workspace/_data/news/data_cache/076a6e5d0883b6d1.html.json', 'w', encoding='utf-8') as f:
    json.dump(processed, f, ensure_ascii=False, indent=2)

print(f"Processed {len(processed)} articles")
print(json.dumps(processed, ensure_ascii=False, indent=2)[:5000])
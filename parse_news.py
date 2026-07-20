#!/usr/bin/env python3
import re
import json
import html
from bs4 import BeautifulSoup

# Read the HTML file
with open('_data/news/data_cache/f594b4d291d6e1aa.html.txt', 'r') as f:
    html_content = f.read()

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Extract all text content
text = soup.get_text('\n', strip=True)

# Split into lines and clean
lines = [line.strip() for line in text.split('\n') if line.strip()]

# Now let's extract articles - they seem to have titles and content
# Looking at the structure, articles appear to have titles followed by content

# Let me extract articles by looking at patterns
# Articles seem to have: Title, Date, Content

articles = []

# Parse the HTML more carefully - look for article-like structures
# The HTML seems to have articles in a list format

# Let's extract all links and their surrounding text
for link in soup.find_all('a'):
    text = link.get_text(strip=True)
    href = link.get('href', '')
    if text and len(text) > 10 and not text.startswith('[') and not text.startswith('VIDEO'):
        # Check if this looks like an article title
        if len(text) > 20:
            # Find surrounding text for content
            parent = link.parent
            content_text = ''
            if parent:
                content_text = parent.get_text(strip=True)
            articles.append({
                'title': text,
                'content': content_text,
                'href': href
            })

# Also look for text patterns that look like articles
# The text has patterns like: Title, Date, Content

# Let me try a different approach - extract from the text lines
articles = []
current_title = None
current_content = []
current_date = None

for i, line in enumerate(lines):
    # Check if line looks like a title (longer, not a date, not a category)
    # Dates look like "09 Iulie 15:24" or "2026-03-20" or "20 Iulie 07:00"
    is_date = bool(re.match(r'^\d{1,2}\s+\w+\s+\d{1,2}:\d{2}$', line)) or \
              bool(re.match(r'^\d{4}-\d{2}-\d{2}$', line)) or \
              bool(re.match(r'^\d{1,2}\s+\w+\s+\d{2}:\d{2}$', line))
    
    # Categories are short uppercase words
    is_category = line in ['Ştiri', 'EDUCAŢIE', 'Social', 'Politic/Administrativ', 'Economic', 'LEGAL', 'Sport', 'National/International', 'Turism Cluj', 'VREMEA CLUJ', 'Divertisment', 'Economic', 'Social', 'Sport', 'National/International', 'Politic/Administrativ']
    
    # Skip navigation items
    is_nav = line in ['Contact', 'Trimite o stire', 'Urmăriţi-ne', 'Recomandări', 'Categorii', 'Tendințe', 'Ştiri de Cluj', 'Ştiri', 'VIDEO', 'FOTO', 'AUDIO', 'VIDEO.', 'FOTO.', 'AUDIO.', 'VIDEO:', 'FOTO:', 'AUDIO:']
    
    # Check if it looks like an article title (longer text, not a date, not a category)
    looks_like_title = len(line) > 30 and not is_date and not is_category and not is_nav and not line.startswith('[') and not line.startswith('VIDEO') and not line.startswith('FOTO') and not line.startswith('AUDIO')
    
    # Also check for lines that start with [ and have content - these are article titles in brackets
    bracketed_title = line.startswith('[') and len(line) > 30 and line.endswith(']')
    
    if (looks_like_title or bracketed_title) and not is_nav:
        # Save previous article
        if current_title:
            articles.append({
                'title': current_title,
                'content': ' '.join(current_content),
                'date': current_date
            })
        # Start new article
        current_title = line.strip('[]')
        current_content = []
        current_date = None
    elif is_date and current_title and not current_date:
        current_date = line
    elif current_title and not is_date and not is_category and not is_nav and len(line) > 10:
        current_content.append(line)

# Don't forget the last article
if current_title:
    articles.append({
        'title': current_title,
        'content': ' '.join(current_content),
        'date': current_date
    })

# Now let's also extract from the HTML structure more carefully
# Look for article-like elements
articles_from_html = []

# Find all text nodes that look like articles
for elem in soup.find_all(['div', 'article', 'li', 'p', 'h1', 'h2', 'h3', 'h4', 'a']):
    text = elem.get_text(strip=True)
    if len(text) > 50 and not text.startswith('[') and 'VIDEO' not in text[:10] and 'FOTO' not in text[:10]:
        # Check if it has a title-like structure
        lines_in_elem = text.split('\n')
        if len(lines_in_elem) >= 2:
            title_candidate = lines_in_elem[0]
            content_candidate = ' '.join(lines_in_elem[1:])
            if len(title_candidate) > 20 and len(content_candidate) > 30:
                articles_from_html.append({
                    'title': title_candidate,
                    'content': content_candidate
                })

# Combine and deduplicate
all_articles = articles + articles_from_html

# Deduplicate by title
seen_titles = set()
unique_articles = []
for art in all_articles:
    title_key = art['title'][:50].lower()
    if title_key not in seen_titles and len(art['title']) > 20:
        seen_titles.add(title_key)
        unique_articles.append(art)

# Now let's manually extract the clear articles from the text
# Looking at the text, I can see clear article patterns

# Let me manually extract the clear articles from the text
manual_articles = [
    {
        'title': 'VIDEO. Momentul altercației de după finala Cupei Mondiale! Tensiuni uriașe între jucătorii Spaniei și Argentinei, după finalul Spania-Argentina 1-0',
        'content': 'VIDEO. Momentul altercației de după finala Cupei Mondiale! Tensiuni uriașe între jucătorii Spaniei și Argentinei, după finalul Spania-Argentina 1-0',
        'date': '20 Iulie 07:00'
    },
    {
        'title': 'VIDEO. Tânăr, surprins într-o stare alarmantă pe stradă, în centrul Clujului. Martori: „Era complet dezorientat. Putea fi lovit oricând de o mașină”',
        'content': 'VIDEO. Tânăr, surprins într-o stare alarmantă pe stradă, în centrul Clujului. Martori: „Era complet dezorientat. Putea fi lovit oricând de o mașină”',
        'date': '20 Iulie 09:56'
    },
    {
        'title': 'VIDEO. Doi clujeni, reținuți după ce au bătut doi bărbați în stația de autobuz, în Cluj. Veneau de la Electric Castle. Unul a fost operat de urgență!',
        'content': 'VIDEO. Doi clujeni, reținuți după ce au bătut doi bărbați în stația de autobuz, în Cluj. Veneau de la Electric Castle. Unul a fost operat de urgență!',
        'date': '19 Iulie 21:44'
    },
    {
        'title': 'Nativii din trei zodii scapă de necazuri până în 15 august. O zodie binecuvântată are cel mai mult de câștigat: Bani, noroc și succes pe toate planurile',
        'content': 'Nativii din trei zodii scapă de necazuri până în 15 august. O zodie binecuvântată are cel mai mult de câștigat: Bani, noroc și succes pe toate planurile',
        'date': '19 Iulie 20:28'
    },
    {
        'title': 'Accident între Ciurila și Sălicea: Trei persoane, printre care doi copii, au fost rănite, după ce o mașină s-a răsturnat. Echipajele ISU Cluj intervin acum',
        'content': 'Accident între Ciurila și Sălicea: Trei persoane, printre care doi copii, au fost rănite, după ce o mașină s-a răsturnat. Echipajele ISU Cluj intervin acum',
        'date': '20 Iulie 10:07'
    },
    {
        'title': 'România importă energie electrică tocmai în momentele în care aceasta e cea mai scumpă. Un specialist explică mecanismul din spatele facturilor uriașe',
        'content': 'România importă energie electrică tocmai în momentele în care aceasta e cea mai scumpă. Un specialist explică mecanismul din spatele facturilor uriașe',
        'date': '20 Iulie 11:14'
    },
    {
        'title': 'EXCLUSIV. Topul spitalelor din Cluj care duc greul sistemului: Unde ajung cele mai grave cazuri, ce spitale funcționează la maximum, unde lipsesc medici',
        'content': 'Președintele României, Nicușor Dan, nu va păstra pistolul primit cadou din partea președintelui Turciei, Recep Tayyip Erdoğan, în cadrul summitului NATO desfășurat la Ankara. Administrația Prezidențială a transmis joi explicații oficiale privind soarta ar'
    },
    {
        'title': 'La ce Facultate de Medicină ai cele mai mari șanse să intri în 2026? Primele cifre oficiale schimbă calculele privind concurența',
        'content': 'La ce Facultate de Medicină ai cele mai mari șanse să intri în 2026? Primele cifre oficiale schimbă calculele privind concurența'
    },
    {
        'title': 'VIDEO. Viitură devastatoare în Bușteni după o rupere de nori în Bucegi. O femeie a fost grav rănită, mai multe mașini au fost luate de ape și DN1 e blocat',
        'content': 'VIDEO. Viitură devastatoare în Bușteni după o rupere de nori în Bucegi. O femeie a fost grav rănită, mai multe mașini au fost luate de ape și DN1 e blocat'
    },
    {
        'title': 'Probleme grave într-un parc din Cluj-Napoca: Locuitorii nu mai suportă ce se întâmplă lângă locul de joacă al copiilor',
        'content': 'Probleme grave într-un parc din Cluj-Napoca: Locuitorii nu mai suportă ce se întâmplă lângă locul de joacă al copiilor'
    },
    {
        'title': 'Cum arată pistolul primit cadou de Nicușor Dan de la Recep Erdogan. Ce a decis să facă președintele României cu arma, la sfatul serviciului SPP',
        'content': 'Președintele României, Nicușor Dan, nu va păstra pistolul primit cadou din partea președintelui Turciei, Recep Tayyip Erdoğan, în cadrul summitului NATO desfășurat la Ankara. Administrația Prezidențială a transmis joi explicații oficiale privind soarta ar',
        'date': '09 Iulie 15:24'
    },
    {
        'title': 'VIDEO: Ei sunt cei doi eroi, agenți de pază, care au intervenit în mai puțin de două minute la amenințarea cu armă din mazinul din Mărăști, Cluj-Napoca',
        'content': 'Doi agenți de securitate din Cluj-Napoca au intervenit în mai puțin de două minute la incidentul petrecut miercuri dimineață într-o societate comercială de pe strada Fabricii, din cartierul Mărăști, unde un bărbat a amenințat o angajată folosind un pistol',
        'date': '05 Iunie'
    },
    {
        'title': 'VIDEO. Amenințare cu pistolul într-un magazin din Cluj-Napoca, pe Fabricii, în Mărăști. O femeie a fost victima. Agresorul, imobilizat de agenții de pază',
        'content': 'VIDEO | Amenințare cu pistolul într-o firmă din Cluj-Napoca. O femeie a fost intimidată, iar agresorul a fost imobilizat de agenții de pază. Incidentul a avut loc în data de 4 iunie și a dus la intervenția de urgență a polițiștilor',
        'date': '05 Iunie'
    },
    {
        'title': 'Un clujean beat a amenințat cu moartea un polițist chiar în spital, după ce l-au ridicat de la pariuri: „Mâine vin cu pistolul la tine acasă!”',
        'content': 'Un bărbat din zona Huedinului a fost condamnat definitiv la 5 ani și 2 luni de închisoare după ce a amenințat un polițist cu moartea într-un spital din Cluj. Curtea de Apel i-a respins apelul pe 20 martie 2026',
        'date': '2026-03-20'
    },
    {
        'title': 'VIDEO. Traficant prins în flagrant de polițiștii clujeni cu 12 kg de „cristal” asupra lui. Avea și un pistol ascuns în compartimentul motor al mașinii',
        'content': 'Un bărbat de 41 de ani a fost prins în flagrant delict de polițiștii antidrog, după ce ar fi introdus în România o cantitate impresionantă de droguri de mare risc, ascunse ingenios în autoturismul său',
        'date': '2026-03-04'
    },
    {
        'title': 'EXCLUSIV. Răfuială periculoasă în centrul Clujului! Polițiștii l-au găsit pe clujeanul ce a amenințat un șofer cu pistolul: „Bă sugaciule, te împușc”',
        'content': 'Un incident extrem de grav, cu aer de răfuială în stil mafiot, a avut loc în centrul Clujului, în seara zilei de 8 februarie, pe strada Ploiești nr. 33. Totul a pornit de la o neînțelegere minoră în trafic, care a degenerat rapid,',
        'date': '2026-02-09'
    },
    {
        'title': 'EXCLUSIV. Răfuială în stil mafiot în centrul Clujului, în seara asta: „A scos pistolul, l-a armat și m-a amenințat că mă împușcă, după un flash”',
        'content': 'Un incident extrem de grav, ca o răfuială în stil mafiot, a avut loc în această seară, în jurul orei 20:30, în centrul Clujului pe strada Ploiești nr. 33 din Cluj-Napoca. Un clujean care se afla împreună cu familia în mașină a povestit',
        'date': '2026-02-08'
    },
    {
        'title': 'Un elev a fost împușcat în cap cu un pistol airsoft, chiar în timpul orelor, însă directorul a încercat să mușamalizeze cazul. Cum s-a aflat adevărul',
        'content': 'Un incident extrem de grav petrecut într-o unitate de învățământ din Predeal, județul Brașov, a ieșit la iveală în urma unui mesaj anonim transmis de un elev de 17 ani prin intermediul campaniei naționale „Spune, pe bune, ce se întâmplă la tine în școală”',
        'date': '2026-02-06'
    },
    {
        'title': 'Siguranța rutieră intră în era digitală: CNAIR va monitoriza traficul cu 400 de sisteme moderne. Ce vor face aceste camere video cu radar',
        'content': 'Cristian Pistol, Director General al Companiei Naționale de Administrare a Infrastructurii Rutiere (CNAIR) SA, a anunțat un pas major în digitalizarea monitorizării traficului pe drumurile naționale și autostrăzile din România. Potrivit acestuia, pentru r',
        'date': '2025-12-13'
    },
    {
        'title': 'Anunțul oficial al CNAIR! 400 de sisteme moderne de monitorizare a șoferilor, 13 dintre acestea vor supraveghea sectorul DN1 Aiud–Cluj',
        'content': '400 de sisteme moderne de monitorizare vor fi instalate pe drumurile naționale și pe autostrăzi. 13 dintre acestea vor supraveghea sectorul DN1 Aiud–Cluj, conform anunțului oficial al șefului CNAIR, Cristian Pistol.',
        'date': '2025-12-12'
    },
    {
        'title': 'Bătaie în stil mafiot în Florești, cu pumni, picioare și amenințări cu pistolul în Panemar. Autorii condamnați azi definitiv. Unul scapă nevinovat!',
        'content': 'Bătăușii din scandalul monstru din Florești condamnați definitiv. Unul dintre ei, scapă, deoarece s-a considerat că era în legitimă apărare. Incidentul a implicat violențe în stația de autobuz și amenințări cu pistol neletal în magazinul Panemar.',
        'date': '2025-11-26'
    },
    {
        'title': 'Parcările din Cluj prea scumpe? Nici vorbă. Cum a fost „jegmănită” Gina Pistol: „Simt că mi-a deschis cineva geanta și mi-a luat banii”',
        'content': 'Mult timp, șoferii clujeni s-au plâns că orașul lor deține „recordul” la cele mai scumpe parcări din România. Tarifele din zona centrală, dar mai ales cele din curtea Spitalului Județean Cluj, unde o simplă oră de staționare poate ajunge să coste cât o ma',
        'date': '2025-09-30'
    },
    {
        'title': 'Jaf demn de un film de acțiune: Un bărbat mascat a furat aproape 7000 de lei cu un pistol de jucărie de la o sală de jocuri de noroc',
        'content': 'Un bărbat a fost condamnat definitiv la 2 ani și 6 luni de închisoare de Curtea de Apel Cluj, după ce a jefuit o sală de jocuri cu un pistol de jucărie. Individul, recidivist, a reușit să fure aproape 7.000 de lei, dar a fost prins rapid de polițiști',
        'date': '2025-09-16'
    },
    {
        'title': 'Descinderi impresionante asupra unor hoți din Cluj pentru un furt de mii de lei! Polițiștii căutau haine furate și bani, dar au găsit o armă ținută ilegal!',
        'content': 'Percheziții la Cluj și Bihor: polițiștii au descoperit bunuri furate de peste 16.000 lei și un pistol deținut ilegal. Ancheta continuă.',
        'date': '2025-09-05'
    },
    {
        'title': 'Gata. E OFICIAL: S-a dat drumul la circulația pe drumul Expres de la Tureni! 5 kilometri „născuți” mai greu ca zidul chinezesc, dar... circulăm pe ei VIDEO',
        'content': 'Drumul Expres Tureni, care leagă DN1 de autostrada A3, a fost dat oficial în folosință joi, începând cu ora 14:00. Anunțul a fost făcut de directorul general al CNAIR, Cristian Pistol, după verificarea lucrărilor.',
        'date': '2025-07-10'
    },
    {
        'title': 'Urmărire cu focuri de armă la Cluj! Un polițist a împușcat un șofer care fugea că nu avea permis. Îl costă scump: Trebuie să-i plătească și spitalizarea',
        'content': 'Un agent de poliție clujean a fost condamnat definitiv pentru purtare abuzivă după ce a tras cu pistolul din dotare asupra unui șofer care încerca să fugă de control, provocându-i o plagă prin împușcare în zona abdominală',
        'date': '2025-06-28'
    },
    {
        'title': 'Andrew Tate, acuzații grave de violență și amenințări cu pistol. Dezvăluiri din documente judiciare: „Mă gândesc dacă să te ****** sau nu”/Vei plăti scump”',
        'content': 'Influencerul britanico-american Andrew Tate este din nou în centrul unui scandal de proporții, fiind acuzat de patru femei din Regatul Unit de fapte grave, inclusiv violență sexuală, amenințări cu moartea și constrângere.',
        'date': '2025-04-10'
    },
    {
        'title': 'Progres MASIV la Autostrada Transilvaniei: Sunt sute de lucrători pe șantier. Clujenii, conectați prin drum expres VIDEO',
        'content': 'Cristian Pistol, directorul CNAIR, a anunțat astăzi că lucrările la Autostrada Transilvaniei avansează. El a vorbit despre secțiunea Zimbor - Poarta Sălajului',
        'date': '2025-03-21'
    },
    {
        'title': 'VIDEO Ne legăm printr-o „autostradă” nouă cu Ungaria: Un constructor român face drumul expres de 720 milioane din NV țării',
        'content': 'Antreprenorul român Construcții Erbașu a fost desemnat câștigător al licitației pentru construcția drumului expres Satu Mare – Oar (frontieră Ungaria), conform anunțului făcut de directorul general al CNAIR, Cristian Pistol.',
        'date': '2025-03-14'
    },
    {
        'title': 'Drumul expres de la Tureni, ce leagă A3 de DN1, CHIAR ar putea fi gata în iunie 2025. După amânări repetate, au adus 220 de muncitori VIDEO',
        'content': 'Lucrările la Drumul Expres de la Tureni care va conecta Autostrada A3 Transilvania de DN1, avansează, în sfârșit, într-un ritm susținut, ajungând la un stadiu fizic de execuție de 80%. Potrivit directorului general al CNAIR, Cristian Pistol, termenul ini',
        'date': '2025-01-26'
    },
    {
        'title': 'Cluj: „Pistolarul” care vâna BMW-uri prin Grigorescu, condamnat cu suspendare! Tânărul de 19 ani s-a răzbunat pe un șofer care nu i-a dat prioritate',
        'content': 'Un tânăr de 19 ani a fost condamnat joi, 9 ianuarie, la un an și 3 luni de închisoare cu suspendare, după ce a tras cu pistolul de tip airsoft în luneta unui BMW care nu i-a acordat prioritate pe trecerea de pietoni. În plus, „pistolarul” este obligat să',
        'date': '2025-01-10'
    },
    {
        'title': 'Jaf la Cluj surprins VIDEO LIVE de CAMERE de SUPRAVEGHERE: Un individ a amenințat o angajat cu o replică de pistol. A luat banii și a fugit',
        'content': 'Jaful dintr-o sală de jocuri din Cluj-Napoca, surprins live de camerele de supraveghere: tânăr reținut după ce a amenințat o angajat cu o replică de pistol.',
        'date': '2024-12-24'
    },
    {
        'title': 'Focuri de armă pe străzile din Cluj-Napoca! Un clujean a tras cu arma într-un BMW care nu i-a dat prioritate pe trecerea de pietoni',
        'content': 'Un clujean de 19 ani riscă să ajungă la închisoare, după ce a tras cu pistolul de tip airsoft în luneta unui BMW care nu i-a acordat prioritate pe trecerea de pietoni.',
        'date': '2024-11-19'
    },
    {
        'title': 'Pas uriaș pentru Autostrada Transilvania! A fost atribuit cel mai scump contract de infrastructură rutieră din România',
        'content': 'Ultimul sector necontractat din Autostrada Transilvania (A3) are de vineri, 1 noiembrie, constructor desemnat, a anunțat Cristian Pistol, directorul Companiei Naționale de Administrare a Infrastructurii Rutiere (CNAIR).',
        'date': '2024-11-01'
    },
    {
        'title': 'Tânăr din Cluj-Napoca, arestat după un conflict în trafic. A tras cu arma într-o mașină, în cartierul Grigorescu',
        'content': 'În urma unor neînțelegeri în trafic, tânărul ar fi utilizat un pistol de tip airsoft și ar fi tras un foc asupra unui autoturism',
        'date': '2024-10-08'
    },
    {
        'title': 'VIDEO Show total la nunta Monicăi Bîrlădeanu cu medicul Valeriu Gheorghiță! Gina Pistol și Monica au cântat împreună: „Se mărită Mona mea”',
        'content': 'Sâmbătă, 5 octombrie 2024, Monica Bîrlădeanu și Valeriu Gheorghiță și-au sărbătorit iubirea într-un cadru grandios, organizând o nuntă de neuitat la Palatul Snagov. După ce au spus un sincer „DA” în fața celor dragi, proaspăt căsătoriții au dansat și',
        'date': '2024-10-07'
    },
    {
        'title': 'VIDEO Scandal cu arme în Florești, Cluj! Patru bărbați, reținuți după o altercație violentă într-un magazin/Arma a fost găsită acasă la unul dintre ei',
        'content': 'Scandal cu pistol în Florești, Cluj! Patru bărbați reținuți după o altercație violentă într-un magazin. Arma a fost găsită de polițiști după o percheziție acasă la unul dintre ei',
        'date': '2024-10-02'
    },
    {
        'title': 'Vacanță cu peripeții pentru Smiley și Gina Pistol. Ce s-a întâmplat la hotelul la care au fost cazați: ,,Ia halatul pe tine, geanta cu bani și vedem noi”',
        'content': 'Smiley și Gina Pistol au avut parte de o vacanță cu mai multă aventură decât s-ar fi așteptat cei doi. Plecați în Cipru pentru a se relaxa și a se bucura de câteva zile frumoase',
        'date': '2024-09-29'
    },
    {
        'title': 'Gina Pistol, gafă colosală la MasterChef! Ce întrebare stânjenitoare i-a pus soției unui concurent – Răspunsul femeii i-a lăsat pe toți cu gura cascată!',
        'content': 'Prima ediție a noului sezon MasterChef România a debutat cu un moment de mare stânjenelă pentru Gina Pistol, gazda emisiunii. Incidentul a avut loc în culise, în timp ce unul dintre concurenți era supus probei culinare.',
        'date': '2024-09-13'
    },
    {
        'title': 'Clip viral cu doi jandarmi care trag la țintă, lecție pentru bărbați: Nu subestima niciodată o femeie! La final, o să râzi cu lacrimi VIDEO',
        'content': 'Un videoclip amuzant realizat de doi jandarmi, un bărbat și o femeie, a devenit viral pe internet, stârnind hohote de râs și admirație printre internauți. În imagini, cei doi trag la țintă cu pistolul, iar rezultatele sunt surprinzătoare.',
        'date': '2024-06-25'
    },
]

# Now process the articles - replace place names and add sarcasm
def replace_place_names(text):
    """Replace Cluj and other place names with Pantelimon, preserving case pattern"""
    # Place names to replace (case-insensitive)
    # We need to preserve case pattern: Cluj -> Pantelimon, CLUJ -> PANTELIMON, cluj -> pantelimon
    
    replacements = [
        # Cluj variations
        (r'\bCluj\b', 'Pantelimon'),
        (r'\bCLUJ\b', 'PANTELIMON'),
        (r'\bcluj\b', 'pantelimon'),
        (r'\bCluj-Napoca\b', 'Pantelimon'),
        (r'\bCLUJ-NAPOCA\b', 'PANTELIMON'),
        (r'\bcluj-napoca\b', 'pantelimon'),
        (r'\bClujului\b', 'Pantelimonului'),
        (r'\bCLUJULUI\b', 'PANTELIMONULUI'),
        (r'\bclujului\b', 'pantelimonului'),
        (r'\bClujenilor\b', 'Pantelimoneni'),
        (r'\bCLUJENILOR\b', 'PANTELIMONENI'),
        (r'\bclujenilor\b', 'pantelimoneni'),
        (r'\bclujean\b', 'pantelimon'),
        (r'\bClujean\b', 'Pantelimon'),
        (r'\bCLUJEAN\b', 'PANTELIMON'),
        (r'\bclujene\b', 'pantelimon'),
        (r'\bClujene\b', 'Pantelimon'),
        (r'\bCLUJENE\b', 'PANTELIMON'),
        # Ciurila, Sălicea, Bușteni, Bucegi, Turda, Câmpia Turzii, Turda-Hotar, Petrilaca, Petrilacă, Hotar, Hotar Petrilaca, Petrilaca Hotar
        (r'\bCiurila\b', 'Pantelimon'),
        (r'\bCIURILA\b', 'PANTELIMON'),
        (r'\bciurila\b', 'pantelimon'),
        (r'\bSălicea\b', 'Pantelimon'),
        (r'\bSĂLICEA\b', 'PANTELIMON'),
        (r'\bsălicea\b', 'pantelimon'),
        (r'\bSălciea\b', 'Pantelimon'),
        (r'\bSĂLCIEA\b', 'PANTELIMON'),
        (r'\bsălciea\b', 'pantelimon'),
        (r'\bBușteni\b', 'Pantelimon'),
        (r'\bBUȘTENI\b', 'PANTELIMON'),
        (r'\bbușteni\b', 'pantelimon'),
        (r'\bBucegi\b', 'Pantelimon'),
        (r'\bBUCEGI\b', 'PANTELIMON'),
        (r'\bbucegi\b', 'pantelimon'),
        (r'\bTurda\b', 'Pantelimon'),
        (r'\bTURDA\b', 'PANTELIMON'),
        (r'\bturda\b', 'pantelimon'),
        (r'\bCâmpia Turzii\b', 'Pantelimon'),
        (r'\bCÂMPIA TURZII\b', 'PANTELIMON'),
        (r'\bcâmpia turzii\b', 'pantelimon'),
        (r'\bTurda-Hotar\b', 'Pantelimon'),
        (r'\bTURDA-HOTAR\b', 'PANTELIMON'),
        (r'\bturda-hotar\b', 'pantelimon'),
        (r'\bPetrilaca\b', 'Pantelimon'),
        (r'\bPETRILACA\b', 'PANTELIMON'),
        (r'\bpetrilaca\b', 'pantelimon'),
        (r'\bPetrilacă\b', 'Pantelimon'),
        (r'\bPETRILACĂ\b', 'PANTELIMON'),
        (r'\bpetrilacă\b', 'pantelimon'),
        (r'\bHotar\b', 'Pantelimon'),
        (r'\bHOTAR\b', 'PANTELIMON'),
        (r'\bhotar\b', 'pantelimon'),
        (r'\bHotar Petrilaca\b', 'Pantelimon'),
        (r'\bHOTAR PETRILACA\b', 'PANTELIMON'),
        (r'\bhotar petrilaca\b', 'pantelimon'),
        (r'\bPetrilaca Hotar\b', 'Pantelimon'),
        (r'\bPETRILACA HOTAR\b', 'PANTELIMON'),
        (r'\bpetrilaca hotar\b', 'pantelimon'),
        (r'\bFlorești\b', 'Pantelimon'),
        (r'\bFLOREȘTI\b', 'PANTELIMON'),
        (r'\bflorești\b', 'pantelimon'),
        (r'\bMărăști\b', 'Pantelimon'),
        (r'\bMĂRĂȘTI\b', 'PANTELIMON'),
        (r'\bmărăști\b', 'pantelimon'),
        (r'\bGrigorescu\b', 'Pantelimon'),
        (r'\bGRIGORESCU\b', 'PANTELIMON'),
        (r'\bgrigorescu\b', 'pantelimon'),
        (r'\bHuedin\b', 'Pantelimon'),
        (r'\bHUEDIN\b', 'PANTELIMON'),
        (r'\bhuedin\b', 'pantelimon'),
        (r'\bPredeal\b', 'Pantelimon'),
        (r'\bPREDEAL\b', 'PANTELIMON'),
        (r'\bpredeal\b', 'pantelimon'),
        (r'\bBrașov\b', 'Pantelimon'),
        (r'\bBRAȘOV\b', 'PANTELIMON'),
        (r'\rbrașov\b', 'pantelimon'),
        (r'\bBușteni\b', 'Pantelimon'),
        (r'\bAiud\b', 'Pantelimon'),
        (r'\bAIUD\b', 'PANTELIMON'),
        (r'\baiud\b', 'pantelimon'),
        (r'\bTureni\b', 'Pantelimon'),
        (r'\bTURENI\b', 'PANTELIMON'),
        (r'\btureni\b', 'pantelimon'),
        (r'\bZimbor\b', 'Pantelimon'),
        (r'\bZIMBOR\b', 'PANTELIMON'),
        (r'\bzimbor\b', 'pantelimon'),
        (r'\bPoarta Sălajului\b', 'Pantelimon'),
        (r'\bPOARTA SĂLAJULUI\b', 'PANTELIMON'),
        (r'\bpoarta sălajului\b', 'pantelimon'),
        (r'\bSatu Mare\b', 'Pantelimon'),
        (r'\bSATU MARE\b', 'PANTELIMON'),
        (r'\bsatu mare\b', 'pantelimon'),
        (r'\bOar\b', 'Pantelimon'),
        (r'\bOAR\b', 'PANTELIMON'),
        (r'\boar\b', 'pantelimon'),
        (r'\bUngaria\b', 'Pantelimon'),
        (r'\bUNGARIA\b', 'PANTELIMON'),
        (r'\bungaria\b', 'pantelimon'),
        (r'\bMuntele\b', 'Pantelimon'),
        (r'\bMUNTELE\b', 'PANTELIMON'),
        (r'\bmuntele\b', 'pantelimon'),
        (r'\bGutai\b', 'Pantelimon'),
        (r'\bGUTAI\b', 'PANTELIMON'),
        (r'\bgutai\b', 'pantelimon'),
        (r'\bBarcelona\b', 'Pantelimon'),
        (r'\bBARCELONA\b', 'PANTELIMON'),
        (r'\bbarcelona\b', 'pantelimon'),
        (r'\bAnkara\b', 'Pantelimon'),
        (r'\bANKARA\b', 'PANTELIMON'),
        (r'\bankara\b', 'pantelimon'),
        (r'\bTurcia\b', 'Pantelimon'),
        (r'\bTURCIA\b', 'PANTELIMON'),
        (r'\bturcia\b', 'pantelimon'),
        (r'\bNATO\b', 'PANTELIMON'),
        (r'\bnato\b', 'pantelimon'),
        (r'\bFabricii\b', 'Pantelimon'),
        (r'\bFABRICII\b', 'PANTELIMON'),
        (r'\bfabricii\b', 'pantelimon'),
        (r'\bMărăști\b', 'Pantelimon'),
        (r'\bDN1\b', 'DN1'),
        (r'\bDN1\b', 'DN1'),
        (r'\bA3\b', 'A3'),
        (r'\bISU\b', 'ISU'),
        (r'\bISU\b', 'ISU'),
        (r'\bCNAIR\b', 'CNAIR'),
        (r'\bSPP\b', 'SPP'),
        (r'\bNATO\b', 'NATO'),
        (r'\bNATO\b', 'NATO'),
    ]
    
    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    
    return result

def add_sarcasm_for_media(text, title):
    """Add sarcastic mentions of VIDEO/FOTO/AUDIO in title/content"""
    result_title = title
    result_content = text
    
    # Check for VIDEO mentions
    video_patterns = [r'\bVIDEO\b', r'\bVIDEO\.', r'\bVIDEO:', r'\bVIDEO\s']
    foto_patterns = [r'\bFOTO\b', r'\bFOTO\.', r'\bFOTO:', r'\bFOTO\s']
    audio_patterns = [r'\bAUDIO\b', r'\bAUDIO\.', r'\bAUDIO:', r'\bAUDIO\s']
    
    has_video = any(re.search(p, text, re.IGNORECASE) or re.search(p, title, re.IGNORECASE) for p in video_patterns)
    has_foto = any(re.search(p, text, re.IGNORECASE) or re.search(p, title, re.IGNORECASE) for p in foto_patterns)
    has_audio = any(re.search(p, text, re.IGNORECASE) or re.search(p, title, re.IGNORECASE) for p in audio_patterns)
    
    # Add sarcastic mentions
    if has_video and 'VIDEO' not in result_title.upper()[:10]:
        result_title = f"VIDEO: {result_title} - VIDEO, pentru că nu-i suficient că s-a întâmplat"
    elif has_video:
        result_content = f"{result_content} - VIDEO, pentru că nu-i suficient că l-ai văzut."
    
    if has_foto and 'FOTO' not in result_title.upper()[:10]:
        result_title = f"FOTO: {result_title} - FOTO, pentru că nu-i suficient că l-ai văzut"
    elif has_foto:
        result_content = f"{result_content} - FOTO, pentru că nu-i suficient că l-ai văzut."
    
    if has_audio and 'AUDIO' not in result_title.upper()[:10]:
        result_title = f"AUDIO: {result_title} - AUDIO, pentru că nu-i suficient că l-ai auzit"
    elif has_audio:
        result_content = f"{result_content} - AUDIO, pentru că nu-i suficient că l-ai auzit."
    
    return result_title, result_content

def make_sarcastic_romanian(title, content):
    """Make the content sarcastic and Romanian with diacritics"""
    # Replace place names in both title and content
    title = replace_place_names(title)
    content = replace_place_names(content)
    
    # Add sarcastic media mentions
    title, content = add_sarcasm_for_media(content, title)
    
    # Make content more sarcastic in Romanian
    sarcastic_templates = [
        "{content} Și totuși, lumea se mai miră.",
        "{content} România în toată splendoarea ei.",
        "{content} Doar o zi obișnuită în Pantelimon.",
        "{content} Nimic nou sub soarele de la Pantelimon.",
        "{content} Așa e viața la Pantelimon.",
        "{content} Știri de la Pantelimon, unde realitatea depășește ficțiunea.",
        "{content} Doar la Pantelimon se întâmplă asta.",
        "{content} Binevenit în realitatea noastră.",
    ]
    
    # Pick a random sarcastic template based on content hash
    import hashlib
    hash_val = int(hashlib.md5(content.encode()).hexdigest(), 16)
    template = sarcastic_templates[hash_val % len(sarcastic_templates)]
    
    content = template.format(content=content)
    
    return title, content

# Process all articles
processed_articles = []
for art in manual_articles:
    title, content = make_sarcastic_romanian(art['title'], art['content'])
    processed_articles.append({
        'title': title,
        'content': content
    })

# Create JSON output
output = json.dumps(processed_articles, ensure_ascii=False, indent=2)

# Write to file
with open('_data/news/data_cache/f594b4d291d6e1aa.html.json', 'w') as f:
    f.write(output)

print(f"Generated {len(processed_articles)} articles")
print("First article:")
print(json.dumps(processed_articles[0], ensure_ascii=False, indent=2))

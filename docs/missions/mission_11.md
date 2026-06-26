# Misiunea 11: Probleme la Școală
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Gina
**Recompense**: 100 EUR, Respect +10
**Prerechizite (Prerequisites)**: Misiunea 10: Acasă la Relu

---

## Rezumat și Obiective
**Obiectiv Principal**: Deși sunt despărțiți, Gina îl sună pe Relu pentru că fiul lor, Chuckie, este agresat la școală de un coleg al cărui tată este un gabor (polițist) corupt și influent. Relu și Gina merg la școală. Ulterior, Relu îl urmărește pe polițist în trafic și folosește mașina pentru a-l tampona ușor și a-l amenința cu barosul, explicându-i că băiatul lui trebuie să-l lase în pace pe Chuckie.

### Obiective de Gameplay:
- [ ] Mergi la școala generală din Pantelimon.
- [ ] Întâlnește-te cu Gina și diriginta lui Chuckie.
- [ ] Urmărește-l pe tatăl agresorului lui Chuckie.
- [ ] Intimidează-l pe polițist în trafic.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Diriginta: 'Codrin (Chuckie) este agresiv, dar și celălalt băiat îl provoacă. Tatăl lui e inspector de poliție...'
- Relu (către polițist): 'Dacă mai plânge băiatul meu o singură dată, Loganul ăsta galben o să treacă peste mașina ta. Ai înțeles?'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu stă în cabinetul directoarei lângă o Gina rece și distantă.**
- **[Cadru 2] Relu blochează mașina polițistului într-o intersecție aglomerată din Pantelimon.**
- **[Cadru 3] Relu coboară geamul și îi arată polițistului un baros greu, privindu-l amenințător.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_11_ACTIVE`
- **Condiție de deblocare**: `Misiunea 10: Acasă la Relu` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_11_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 12: Nemulțumirea Căpitanului`.

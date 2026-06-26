# Misiunea 31: Magazinul de Electrocasnice
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Teddy
**Recompense**: 600 EUR, Respect +30
**Prerechizite (Prerequisites)**: Misiunea 30: Presiunea Gaborilor

---

## Rezumat și Obiective
**Obiectiv Principal**: Pentru a spăla banii lui Toma, Relu și Teddy deschid un magazin de electrocasnice în Pantelimon. Niște interlopi mărunți din sectorul 3, neștiind cine controlează magazinul, vin să ceară taxă de protecție. Jucătorul trebuie să apere magazinul folosind un frigider sau televizoare vechi pentru a-i bate pe atacatori, apoi să-l captureze pe liderul lor și să-l lege de un stâlp.

### Obiective de Gameplay:
- [ ] Deschide noul magazin de electrocasnice (front de spălare bani).
- [ ] Alungă recuperatorii din sectorul 3 care cer taxă de protecție.
- [ ] Intimidează-l pe liderul lor.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Teddy: 'Vin băieții din sectorul 3 să ne ceară taxă. Pe teritoriul nostru!'
- Relu: 'Hai să le arătăm niște oferte speciale la mașinile de spălat.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Trei interlopi sparg vitrina magazinului de electrocasnice cu bâte.**
- **[Cadru 2] Relu împinge un frigider mare peste un atacator, strivindu-l de perete.**
- **[Cadru 3] Liderul recuperatorilor este legat cu bandă adezivă de un stâlp de înaltă tensiune în fața magazinului.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_31_ACTIVE`
- **Condiție de deblocare**: `Misiunea 30: Presiunea Gaborilor` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_31_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 32: Dispariția lui Nico`.

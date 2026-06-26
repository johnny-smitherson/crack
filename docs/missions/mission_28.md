# Misiunea 28: Sânge pe Zăpadă
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Toma
**Recompense**: 1500 EUR, RPG
**Prerechizite (Prerequisites)**: Misiunea 27: Confruntarea Finală

---

## Rezumat și Obiective
**Obiectiv Principal**: Finalul Sezonului 2. Relu și Toma organizează asaltul final asupra hangarului unde se ascunde Nicu. Misiunea este un masacru pe zăpada din jurul lacului Pantelimon. Jucătorul folosește un RPG pentru a distruge mașinile de lux ale lui Nicu și îl execută pe Nicu. Totuși, în timpul luptei, Nea Puiu este ucis de un lunetist trimis de Emilian, iar Relu realizează că războiul abia a început.

### Obiective de Gameplay:
- [ ] Mergi la hangarul abandonat de lângă Lacul Pantelimon.
- [ ] Elimină-l pe Nicu și garda sa de corp.
- [ ] Evită atacul de sniper al oamenilor lui Emilian.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nicu: 'Relu, te rog... îți dau toți banii din Spania...'
- Relu: 'Ai atins ușa casei mele. Să-i spui lui Nea Puiu că-mi pare rău.' (Trage)
- Emilian (prin stație): 'O să plângi mult timp de acum încolo, Relu...'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Un hangar mare din tablă ruginită pe malul înghețat al Lacului Pantelimon, acoperit de zăpadă.**
- **[Cadru 2] Relu trage cu RPG-ul într-un SUV alb aparținând lui Nicu, creând o explozie uriașă.**
- **[Cadru 3] Relu privește corpul inert al lui Nea Puiu întins pe zăpadă, strângându-și pumnii de furie.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_28_ACTIVE`
- **Condiție de deblocare**: `Misiunea 27: Confruntarea Finală` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_28_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 29: Noua Ordine`.

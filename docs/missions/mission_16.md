# Misiunea 16: Punct și de la Capăt
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Toma
**Recompense**: 1000 EUR, M4
**Prerechizite (Prerequisites)**: Misiunea 15: Trădarea

---

## Rezumat și Obiective
**Obiectiv Principal**: Finalul Sezonului 1. Relu realizează că este încolțit de poliție și de propriul șef. Face o călătorie rapidă la Constanța pentru a se întâlni cu Toma, marele șef care controlează portul. Toma îi propune lui Relu să-l trădeze pe Căpitanu' în schimbul protecției și preluării afacerilor din sectorul 2. Relu acceptă pactul, dar la întoarcerea în București este atacat de oamenii Căpitanului care suspectează trădarea. O luptă masivă de supraviețuire la depozitul din Pantelimon.

### Obiective de Gameplay:
- [ ] Mergi la întâlnirea secretă cu Toma la Constanța.
- [ ] Fă pactul secret pentru eliminarea Căpitanului.
- [ ] Întoarce-te în Pantelimon și apără-te de oamenii Căpitanului.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Toma: 'Căpitanu' e de domeniul trecutului, Relu. E prea zgomotos și prost. Tu ești băiat deștept. Îl curățăm și preiei tu.'
- Relu: 'Să moară Căpitanu'.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu și Toma stau pe o terasă luxoasă din portul Tomis, privind spre iahturi.**
- **[Cadru 2] O explozie violentă distruge garajul lui Nea Puiu în București.**
- **[Cadru 3] Relu, plin de funingine și sânge, ține în mână o armă automată M4, privind spre flăcări.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_16_ACTIVE`
- **Condiție de deblocare**: `Misiunea 15: Trădarea` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_16_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 17: Nuntă cu Scântei`.

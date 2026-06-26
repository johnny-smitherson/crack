# Misiunea 40: Prăbușirea Imperiului
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 1000 EUR, RPG, M4
**Prerechizite (Prerequisites)**: Misiunea 39: Tăierea Legăturilor

---

## Rezumat și Obiective
**Obiectiv Principal**: Toma lansează un asalt total asupra ultimului punct de rezistență din București—depozitul principal de la Granitul administrat de Nico. Nico și Relu, baricadați în depozit, trebuie să înfrunte valuri de inamici înarmați cu arme grele și vehicule blindate. O misiune de supraviețuire și luptă militară urbană la scară largă în stil GTA.

### Obiective de Gameplay:
- [ ] Mergi la depozitul principal din Pantelimon.
- [ ] Apără depozitul de asaltul total al mafiei din Constanța.
- [ ] Elimină blindatele trimise de Toma.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nico: 'Relu, vin peste noi cu tot ce au! Dacă pică depozitul ăsta, am terminat-o!'
- Relu: 'Pregătește lansatorul de rachete. O să fie măcel.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Depozitul este înconjurat de mașini de teren negre care trag cu mitraliere grele.**
- **[Cadru 2] Relu folosește un RPG pentru a arunca în aer un SUV blindat la porțile depozitului.**
- **[Cadru 3] Nico trage cu un M4 de pe acoperișul depozitului, acoperită de explozii și fum.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_40_ACTIVE`
- **Condiție de deblocare**: `Misiunea 39: Tăierea Legăturilor` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_40_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 41: Răfuiala de la Constanța`.

# Misiunea 21: Umbra lui Nea Puiu
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Nea Puiu
**Recompense**: 200 EUR
**Prerechizite (Prerequisites)**: Misiunea 20: Spălare de Bani

---

## Rezumat și Obiective
**Obiectiv Principal**: Nea Puiu începe să sufere de episoade paranoice severe din cauza vârstei și a alcoolului. Acesta pleacă prin Pantelimon înarmat cu un cuțit, strigând că poliția este pe urmele lor. Relu trebuie să-l găsească rapid înainte de a face o prostie, să-l salveze de o patrulă de poliție locală pe care Nea Puiu o amenința și să-l transporte în siguranță la o casă conspirativă din județul Ilfov.

### Obiective de Gameplay:
- [ ] Mergi la garajul lui Nea Puiu.
- [ ] Găsește-l pe Nea Puiu care a plecat paranoic prin cartier.
- [ ] Salvează-l de gaborii care vor să-l legitimeze.
- [ ] Du-l la o casă conspirativă din afara Bucureștiului.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nea Puiu: 'Vin după noi, Relule! Gaborul ăla cu ochi de sticlă știe tot! Trebuie să-i curățăm pe toți!'
- Relu: 'Nea Puiu, potolește-te. Urcă în mașină, mergem la aer curat.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Nea Puiu agită un cuțit ruginit în mijlocul unei intersecții din Pantelimon, speriind trecătorii.**
- **[Cadru 2] Relu intervine între doi polițiști locali și Nea Puiu, oferindu-le gaborilor o șpagă grasă.**
- **[Cadru 3] Nea Puiu doarme pe scaunul din dreapta al Loganului în timp ce mașina rulează pe un drum de țară.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_21_ACTIVE`
- **Condiție de deblocare**: `Misiunea 20: Spălare de Bani` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_21_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 22: Transport de Constanța`.

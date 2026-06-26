# Misiunea 33: Avertismentul lui Toma
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Toma
**Recompense**: 1200 EUR
**Prerechizite (Prerequisites)**: Misiunea 32: Dispariția lui Nico

---

## Rezumat și Obiective
**Obiectiv Principal**: Toma este furios că acțiunile lui Emilian blochează portul și afacerile cu droguri. Îl trimite pe Relu să 'facă curățenie' printre dealerii independenți din Mamaia care atrag atenția poliției. Jucătorul trebuie să elimine 4 ținte diferite în stațiune într-un timp limită, folosind o barcă de mare viteză pentru a fugi.

### Obiective de Gameplay:
- [ ] Mergi la întâlnirea cu oamenii lui Toma în portul Constanța.
- [ ] Află că Toma este nemulțumit de pierderile provocate de Emilian.
- [ ] Elimină dealerii concurenți din stațiunea Mamaia.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Toma: 'Bucureștiul tău îmi aduce numai probleme, Relu. Rezolvă dealerii ăia sau vin eu personal și curăț tot, inclusiv pe tine.'
- Relu: 'Consideră-i rezolvați.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu conduce o barcă cu motor pe valurile mării negre sub lumina apusului.**
- **[Cadru 2] Relu trage de pe barcă într-un dealer care încearcă să fugă pe plaja din Mamaia.**
- **[Cadru 3] Barca se îndepărtează în viteză în timp ce pe mal se aud sirenele poliției.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_33_ACTIVE`
- **Condiție de deblocare**: `Misiunea 32: Dispariția lui Nico` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_33_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 34: Trădătorul`.

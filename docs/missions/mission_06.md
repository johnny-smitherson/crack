# Misiunea 06: Fiorul Dragostei
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Teddy
**Recompense**: 300 EUR
**Prerechizite (Prerequisites)**: Misiunea 5: Doi la Preț de Unul

---

## Rezumat și Obiective
**Obiectiv Principal**: Teddy îl roagă pe Relu să-l ajute cu o treabă personală: vrea să meargă la o întâlnire cu Magda în Parcul Cosmos. Jucătorul îl conduce pe Teddy acolo. În timp ce ei vorbesc, niște golani din Pantelimon se iau de ei. Relu, ascuns după niște tufe, trebuie să intervină discret și să-i bată pe golani fără ca Magda să realizeze că tatăl ei este cel care îi protejează din umbră.

### Obiective de Gameplay:
- [ ] Du-l pe Teddy să cumpere flori din Obor.
- [ ] Condu-l la întâlnirea cu Magda în Parcul Cosmos.
- [ ] Apără-l pe Teddy de golanii din parc.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Teddy: 'Relu, te rog nu-i spune tatălui meu. O să creadă că sunt un fraier.'
- Relu: 'Nu-i spun. Dar ai grijă de tine.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Teddy îi oferă Magdei un buchet mare de trandafiri pe o bancă în Parcul Cosmos.**
- **[Cadru 2] Trei golani în treninguri Adidas se apropie amenințător de cei doi.**
- **[Cadru 3] Relu îl lovește pe la spate pe unul din golani cu o cheie franceză mare, trăgându-l în boscheți.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_06_ACTIVE`
- **Condiție de deblocare**: `Misiunea 5: Doi la Preț de Unul` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_06_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 7: Suspiciuni de Soție`.

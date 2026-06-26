# Misiunea 12: Nemulțumirea Căpitanului
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Căpitanu'
**Recompense**: 700 EUR, Micro-SMG
**Prerechizite (Prerequisites)**: Misiunea 11: Problems la Școală

---

## Rezumat și Obiective
**Obiectiv Principal**: Căpitanu' este extrem de nervos pentru că o livrare de electronice furate a fost interceptată sau întârziată. Îl trimite pe Relu să o recupereze cu forța de pe Centura București, unde este păzită de o firmă privată de securitate care colaborează cu rivalii. O misiune clasică de atac în mișcare și condus vehicule grele.

### Obiective de Gameplay:
- [ ] Mergi la biroul Căpitanului.
- [ ] Interceptă camionul cu marfă pe Centura București.
- [ ] Elimină paza camionului.
- [ ] Condu camionul la depozitul din Pantelimon.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Căpitanu': 'Marfa aia valorează 50 de mii de euro. O vreau în depozit în 2 ore, altfel te îngrop eu pe tine!'
- Relu: 'O rezolv. Pregătește oamenii să descarce.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu conduce Loganul umăr la umăr cu un camion mare pe șoseaua de centură.**
- **[Cadru 2] Relu trage cu un micro-SMG pe geamul Loganului spre cabina camionului.**
- **[Cadru 3] Camionul intră în viteză pe porțile depozitului Căpitanului, sub privirile mulțumite ale interlopilor.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_12_ACTIVE`
- **Condiție de deblocare**: `Misiunea 11: Problems la Școală` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_12_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 13: Încolțit`.

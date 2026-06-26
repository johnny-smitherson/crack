# Misiunea 19: Inspectorul Psihopat
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Emilian
**Recompense**: 300 EUR
**Prerechizite (Prerequisites)**: Misiunea 18: Cadoul Căpitanului

---

## Rezumat și Obiective
**Obiectiv Principal**: Inspectorul Emilian îl șantajează direct pe Relu cu dovezile crimei din sezonul 1. Pentru a-l lăsa în pace, Emilian îi ordonă lui Relu să compromită un senator curat care investighează corupția din poliție. Relu trebuie să se furișeze în parcarea privată a senatorului, să planteze o cantitate masivă de cocaină sub scaunul șoferului și apoi să sune la poliție dintr-o cabină telefonică publică.

### Obiective de Gameplay:
- [ ] Răspunde la telefonul lui Emilian.
- [ ] Mergi la locul de întâlnire de sub podul Grant.
- [ ] Plantează pachetul de cocaină în mașina senatorului.
- [ ] Sună la 112 anonim.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Emilian: 'Relu, ești o umbră în buzunarul meu. Faci ce spun eu, sau soția ta află unde ai îngropat cadavrul ăla.'
- Relu: 'Ce vrei să fac?'
- Emilian: 'O mică surpriză pentru un domn senator...'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Emilian zâmbește maniacal sub lumina galbenă a unui stâlp de sub podul Grant.**
- **[Cadru 2] Relu sparge discret geamul unei limuzine negre folosind un dispozitiv special.**
- **[Cadru 3] Relu vorbește la un telefon public vechi, acoperindu-și gura cu o batistă.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_19_ACTIVE`
- **Condiție de deblocare**: `Misiunea 18: Cadoul Căpitanului` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_19_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 20: Spălare de Bani`.

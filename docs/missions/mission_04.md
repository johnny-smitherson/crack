# Misiunea 04: Băiatul Șefului
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Căpitanu'
**Recompense**: 200 EUR, Respect +20
**Prerechizite (Prerequisites)**: Misiunea 3: O Escortă de Protejat

---

## Rezumat și Obiective
**Obiectiv Principal**: Căpitanu' îl cheamă pe Relu și îi cere să-l ia pe fiul său, Teddy, pe teren pentru a-l învăța meserie. Merg la un constructor care îi datorează bani Căpitanului. Când constructorul încearcă să-l păcălească pe Teddy, acesta se blochează, iar Relu intervine brutal. După misiune, îl lasă pe Teddy la o cafenea din Pantelimon, unde acesta o întâlnește pe Magda (fiica lui Relu), fără ca vreunul să știe conexiunea de familie.

### Obiective de Gameplay:
- [ ] Mergi la restaurantul Căpitanului.
- [ ] Ia-l pe Teddy în mașină.
- [ ] Mergi la șantierul de lângă Șoseaua Fundeni.
- [ ] Asistă la colectarea banilor și protejează-l pe Teddy.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Căpitanu': 'Fă-l bărbat, Relule. E prea moale. Ascultă rock în loc să se ocupe de afaceri.'
- Teddy: 'Nu sunt moale, tată...'
- Relu: 'Urcă în mașină, puștiule.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Căpitanu' mănâncă mici de pe o farfurie de carton și îi vorbește lui Relu, în timp ce Teddy stă supărat în colț.**
- **[Cadru 2] Pe șantier, Relu trântește un constructor pe o grămadă de nisip, în timp ce Teddy privește îngrozit.**
- **[Cadru 3] Teddy o vede pe Magda citind la o masă pe o terasă și se apropie sfiit.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_04_ACTIVE`
- **Condiție de deblocare**: `Misiunea 3: O Escortă de Protejat` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_04_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 5: Doi la Preț de Unul`.

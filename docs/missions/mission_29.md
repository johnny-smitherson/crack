# Misiunea 29: Noua Ordine
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Toma
**Recompense**: 1000 EUR
**Prerechizite (Prerequisites)**: Misiunea 28: Sânge pe Zăpadă

---

## Rezumat și Obiective
**Obiectiv Principal**: Debutul Sezonului 3. Căpitanu' este scos din joc (paralizat sau mort în urma atacurilor), iar Teddy încearcă să preia conducerea clanului sub îndrumarea lui Relu. Jucătorul trebuie să viziteze 3 cluburi mari din sectorul 2 pentru a re-impune autoritatea noului clan, bătându-i pe patronii care cred că pot refuza plata acum că bătrânul a dispărut.

### Obiective de Gameplay:
- [ ] Mergi la terasa Căpitanului (care acum este condusă de Teddy).
- [ ] Organizează noii oameni din Pantelimon.
- [ ] Recuperează taxa de la cluburile din sectorul 2.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Teddy: 'Relu, unii patroni zic că nu mă respectă pe mine. Că sunt doar băiatul Căpitanului.'
- Relu: 'O să ne respecte după ce le spargem barurile. Hai să le facem o vizită.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Teddy stă pe scaunul de piele al Căpitanului în biroul terasei, arătând nesigur.**
- **[Cadru 2] Relu sparge o sticlă de whisky de capul unui patron de club care refuza taxa.**
- **[Cadru 3] Patronul speriat semnează teancul de chitanțe în timp ce Relu își șterge mâinile.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_29_ACTIVE`
- **Condiție de deblocare**: `Misiunea 28: Sânge pe Zăpadă` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_29_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 30: Presiunea Gaborilor`.

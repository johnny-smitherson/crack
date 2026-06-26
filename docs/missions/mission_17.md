# Misiunea 17: Nuntă cu Scântei
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Teddy
**Recompense**: 500 EUR
**Prerechizite (Prerequisites)**: Misiunea 16: Punct și de la Capăt

---

## Rezumat și Obiective
**Obiectiv Principal**: Debutul Sezonului 2. Relația Magdei cu Teddy duce la o nuntă forțată pentru a stabili o alianță fragilă între Căpitanu' și facțiunea lui Toma (cu Relu ca intermediar). Relu trebuie să asigure securitatea la nuntă. Lucrurile degenerează când interlopii din Constanța și cei din Pantelimon se îmbată și scot cuțitele. Jucătorul trebuie să intervină fără a folosi arme de foc pentru a nu strica nunta fiicei sale.

### Obiective de Gameplay:
- [ ] Mergi la restaurantul unde are loc nunta lui Teddy cu Magda.
- [ ] Verifică invitații la intrare și confiscă armele.
- [ ] Oprește scandalul dintre interlopii din Constanța și cei din Pantelimon.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Căpitanu': 'Băi Relule, cuscrii tăi de la Constanța cam strâmbă din nas la mâncarea noastră. Spune-le să se potolească!'
- Relu: 'Nu strică nimeni nunta fetei mele. Cine mai scoate un cuțit, pleacă de aici cu picioarele înainte.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Magda în rochie albă de mireasă plânge lângă un Teddy îmbrăcat în costum de ginere strâmt.**
- **[Cadru 2] O masă plină de aperitive este răsturnată în timp ce doi interlopi masivi se iau de gât.**
- **[Cadru 3] Relu îi dă un pumn în figură unui interlop din Constanța, trimițându-l direct în tortul de nuntă.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_17_ACTIVE`
- **Condiție de deblocare**: `Misiunea 16: Punct și de la Capăt` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_17_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 18: Cadoul Căpitanului`.

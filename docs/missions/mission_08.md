# Misiunea 08: Afaceri de Familie
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 600 EUR, Shotgun
**Prerechizite (Prerequisites)**: Misiunea 7: Suspiciuni de Soție

---

## Rezumat și Obiective
**Obiectiv Principal**: Nico organizează un transport important de țigări la depozitul de la Granitul. Relu coordonează descărcarea. La întoarcere, Relu îl prinde din nou pe Sabin încercând să-i spioneze casa. De data aceasta, Relu îl bate crunt pe Sabin într-un colț întunecat pentru a-i da o lecție definitivă, având grijă să nu-și arate fața pentru ca Gina să nu afle cine l-a bătut pe fratele ei.

### Obiective de Gameplay:
- [ ] Mergi la depozitul de la Granitul.
- [ ] Prelucrează transportul de țigări de contrabandă.
- [ ] Snopeste-l în bătaie pe Sabin la colțul blocului.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nico: 'Marfa asta de contrabandă trebuie să ajungă în Obor până dimineață. Fără greșeli.'
- Sabin: 'Au! Cine ești, mă? Nu da! Moare mama!'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu și alți băieți descarcă cartoane de țigări dintr-un tir ascuns în depozitul Granitul.**
- **[Cadru 2] În spatele blocului, Relu îi pune un sac pe cap lui Sabin și începe să-l lovească cu pumnii.**
- **[Cadru 3] Sabin zace plin de sânge lângă ghena de gunoi, în timp ce Relu pleacă calm în noapte.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_08_ACTIVE`
- **Condiție de deblocare**: `Misiunea 7: Suspiciuni de Soție` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_08_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 9: Doctorul vine la Bloc`.

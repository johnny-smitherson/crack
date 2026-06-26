# Misiunea 13: Încolțit
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 500 EUR
**Prerechizite (Prerequisites)**: Misiunea 12: Nemulțumirea Căpitanului

---

## Rezumat și Obiective
**Obiectiv Principal**: Relu află de la Nico că poliția (condusă de un inspector ciudat pe nume Emilian) a obținut imagini video cu Dacia lui Logan în apropierea locului unde a fost aruncat cadavrul de la barul lui Sandu. Relu trebuie să se infiltreze noaptea în secția de poliție locală pentru a distruge hard-diskul cu înregistrările camerelor de supraveghere.

### Obiective de Gameplay:
- [ ] Furișează-te în secția de poliție locală.
- [ ] Șterge înregistrările video de pe server.
- [ ] Evită camerele și patrulele de poliție.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nico: 'Gaborii au filmări cu mașina ta la lac. Dacă nu le ștergi acum, ești istorie.'
- Relu: 'Intru prin spate. Ține-mă la curent pe stație.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu escaladează un gard de sârmă ghimpată în spatele secției de poliție.**
- **[Cadru 2] Relu se ascunde după un dulap de fișiere în timp ce un polițist trece prin coridor.**
- **[Cadru 3] Relu smulge hard-diskurile dintr-un rack de servere dintr-o cameră întunecată.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_13_ACTIVE`
- **Condiție de deblocare**: `Misiunea 12: Nemulțumirea Căpitanului` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_13_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 14: Secrete de Familie`.

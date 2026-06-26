# Misiunea 15: Trădarea
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Nea Puiu
**Recompense**: 400 EUR
**Prerechizite (Prerequisites)**: Misiunea 14: Secrete de Familie

---

## Rezumat și Obiective
**Obiectiv Principal**: Nea Puiu îi spune lui Relu că Nico se întâlnește în secret cu un tip ciudat care pare a fi polițist (Emilian). Relu o urmărește pe Nico prin București până la o fabrică dezafectată din marginea orașului, unde o vede oferind informații inspectorului Emilian. Jucătorul trebuie să colecteze dovezi foto/video și să plece fără a fi detectat.

### Obiective de Gameplay:
- [ ] Urmărește-o pe Nico fără să fii detectat.
- [ ] Filmează întâlnirea ei secretă cu Emilian.
- [ ] Scapă din zona de întâlnire fără alertă.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nea Puiu: 'Fata aia, Nico... se învârte cu cine nu trebuie, Relule. O miroase a gabor de la o poștă.'
- Nico: 'Ți-am dat ce doreai, Emilian. Acum lasă-mă în pace!'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu folosește zoom-ul unui aparat foto vechi de pe acoperișul unei clădiri ruinate.**
- **[Cadru 2] În vizor se văd Nico și Emilian discutând aprins lângă un morman de moloz.**
- **[Cadru 3] Relu coboară treptele de urgență în liniște, ascunzând aparatul foto sub haină.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_15_ACTIVE`
- **Condiție de deblocare**: `Misiunea 14: Secrete de Familie` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_15_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 16: Punct și de la Capăt`.

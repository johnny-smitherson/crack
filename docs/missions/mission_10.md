# Misiunea 10: Acasă la Relu
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Gina
**Recompense**: 0 EUR (Misiune de Poveste)
**Prerechizite (Prerequisites)**: Misiunea 9: Doctorul vine la Bloc

---

## Rezumat și Obiective
**Obiectiv Principal**: Sabin o convinge pe Gina că Relu l-a bătut și că este implicat în mafia locală. Când Relu ajunge acasă, Gina îl așteaptă cu bagajele făcute și îl dă afară din casă într-o scenă extrem de dramatică. Relu trebuie să-și adune hainele și restul banilor ascunși în perete și să se mute temporar la garajul insalubru al lui Nea Puiu.

### Obiective de Gameplay:
- [ ] Intră în apartamentul lui Relu.
- [ ] Confruntă-te cu Gina și Sabin cel bătut.
- [ ] Adună-ți lucrurile personale.
- [ ] Mergi la safehouse-ul lui Nea Puiu.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Gina: 'Pleacă! Nu vreau să te mai văd în casa mea! Ești un monstru, Relule! Uită-te ce i-ai făcut lui Sabin!'
- Relu: 'Gina, nu-i ceea ce crezi...'
- Gina: 'Ieși!'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Gina plânge în hohote aruncând hainele lui Relu pe holul blocului.**
- **[Cadru 2] Relu scoate un teanc de euro ascuns în spatele unei prize demontate.**
- **[Cadru 3] Relu stă pe o canapea ruptă în garajul lui Nea Puiu, înconjurat de scule auto și praf.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_10_ACTIVE`
- **Condiție de deblocare**: `Misiunea 9: Doctorul vine la Bloc` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_10_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 11: Probleme la Școală`.

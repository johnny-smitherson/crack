# Misiunea 36: Întoarcerea Acasă
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Relu
**Recompense**: 0 EUR (Misiune de Supraviețuire)
**Prerechizite (Prerequisites)**: Misiunea 35: O Vizită la Constanța

---

## Rezumat și Obiective
**Obiectiv Principal**: Pe drumul de întoarcere de la Constanța, Dacia lui Relu este lovită intenționat de un tir și aruncată în decor pe DN3A. Relu, rănit, trebuie să iasă din mașină și să se apere de o echipă de mercenari trimiși de Toma (care a decis să se debaraseze de Relu după finalizarea hit-ului). Misiunea implică o luptă intensă de tip stealth/survival printr-un lan mare de porumb, folosind doar un cuțit și armele recuperate de la inamici.

### Obiective de Gameplay:
- [ ] Condu pe drumul de întoarcere spre București.
- [ ] Supraviețuiește ambuscadei de pe DN3A.
- [ ] Luptă-te cu mercenarii prin lanul de porumb.
- [ ] Găsește un vehicul funcțional și întoarce-te în Pantelimon.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Mercenar: 'Găsiți-l! E rănit, nu poate fi departe! Toma vrea capul lui!'
- Relu (în șoaptă, în porumb): 'Toma... ai făcut cea mai mare greșeală din viața ta.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Dacia Logan galbenă este răsturnată într-un șanț adânc, cu motorul fumegând.**
- **[Cadru 2] Relu stă ascuns în lanul înalt de porumb, strângând un cuțit militar plin de sânge.**
- **[Cadru 3] Relu conduce un tractor vechi furat de la o fermă din apropiere, îndreptându-se spre București.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_36_ACTIVE`
- **Condiție de deblocare**: `Misiunea 35: O Vizită la Constanța` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_36_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 37: Obsesia lui Emilian`.

# Misiunea 41: Răfuiala de la Constanța
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Relu
**Recompense**: 2000 EUR, Minigun
**Prerechizite (Prerequisites)**: Misiunea 40: Prăbușirea Imperiului

---

## Rezumat și Obiective
**Obiectiv Principal**: Relu merge la Constanța pentru a pune capăt amenințării o dată pentru totdeauna. Înzestrat cu un minigun și un arsenal complet, Relu asaltează vila masivă a lui Toma de pe plajă. Trebuie să lupte prin grădină, piscină, holuri și să ajungă în biroul de la etaj unde Toma stă baricadat. Relu îl confruntă pe Toma și îl execută fără milă.

### Obiective de Gameplay:
- [ ] Mergi la Constanța.
- [ ] Asaltează vila luxoasă a lui Toma pe plaja din Năvodari.
- [ ] Elimină armata privată a lui Toma.
- [ ] Execută-l pe Toma în biroul său.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Toma: 'Relu... nu poți distruge ce am construit eu... sunt prea mulți oameni în spatele meu...'
- Relu: 'Oamenii tăi sunt morți în grădină, Toma. Acum e rândul tău.' (Trage o rafală de minigun)
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] O vilă albă modernă pe plaja din Năvodari, cu palmieri și o piscină mare plină de cadavre.**
- **[Cadru 2] Relu trage cu un Minigun devastator, distrugând stâlpii de marmură ai vilei.**
- **[Cadru 3] Toma stă prăbușit în scaunul său de piele roșie din birou, cu Relu privind spre mare prin geamul spart.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_41_ACTIVE`
- **Condiție de deblocare**: `Misiunea 40: Prăbușirea Imperiului` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_41_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 42: Umbre în Pantelimon`.

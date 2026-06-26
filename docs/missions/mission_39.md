# Misiunea 39: Tăierea Legăturilor
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Relu
**Recompense**: 500 EUR
**Prerechizite (Prerequisites)**: Misiunea 38: Ochi pentru Ochi

---

## Rezumat și Obiective
**Obiectiv Principal**: Relu realizează că Toma nu se va opri până nu-l va vedea mort. Decide să-și trimită întreaga familie (Gina, copiii și Teddy) în Spania pentru a-i proteja. La aeroportul Otopeni, terminalul este atacat de o echipă masivă de asasini trimiși de Toma. Relu trebuie să reziste atacului și să acopere retragerea familiei sale până când aceștia trec de porțile de securitate.

### Obiective de Gameplay:
- [ ] Mergi la Otopeni Airport.
- [ ] Escortează-i pe Gina, Magda, Teddy și Chuckie.
- [ ] Respinge asaltul trupelor lui Toma la terminalul plecări.
- [ ] Asigură-te că familia se îmbarcă în avionul spre Spania.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Gina: 'Relu, tu nu vii cu noi?'
- Relu: 'Mai am o treabă de terminat la Constanța, Gina. Aveți grijă de voi în Spania. O să vin și eu.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Terminalul de plecări al Aeroportului Otopeni, plin de pasageri care fug panicați.**
- **[Cadru 2] Relu trage de după un ghișeu de check-in spre trei atacatori îmbrăcați în costume negre.**
- **[Cadru 3] Avionul decolează pe pistă în timp ce Relu privește prin geamul mare al terminalului, singur.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_39_ACTIVE`
- **Condiție de deblocare**: `Misiunea 38: Ochi pentru Ochi` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_39_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 40: Prăbușirea Imperiului`.

# Misiunea 14: Secrete de Familie
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Teddy
**Recompense**: 300 EUR
**Prerechizite (Prerequisites)**: Misiunea 13: Încolțit

---

## Rezumat și Obiective
**Obiectiv Principal**: Teddy îl cheamă pe Relu disperat: Magda este însărcinată și vor să păstreze copilul. Relu este șocat, dar trebuie să meargă la Căpitanu' să-i spună vestea. În timpul întâlnirii lor tensionate de la o terasă din Pantelimon, o mașină a rivalilor trece prin zonă și deschide focul (Drive-by). Jucătorul trebuie să-i protejeze pe Căpitanu' și pe Teddy și să-i elimine pe atacatori.

### Obiective de Gameplay:
- [ ] Întâlnește-te cu Teddy la cafenea.
- [ ] Ascultă vestea despre sarcina Magdei.
- [ ] Mergi la întâlnirea cu Căpitanu' la terasă.
- [ ] Respinge atacul ambuscadă al rivalilor.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Teddy: 'Relu... Magda e însărcinată. Te rog nu mă omorî.'
- Căpitanu': 'Ce naiba zici acolo, mă?! Nepot de recuperator?!'
- Relu: 'Atenție! La pământ! Trag ăștia!'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Teddy stă cu capul în mâini la o masă de plastic, în timp ce Relu îl privește cu o furie stăpânită.**
- **[Cadru 2] O mașină neagră cu geamuri fumurii trece în viteză, trăgând rafale de gloanțe spre terasă.**
- **[Cadru 3] Relu trage de după o masă răsturnată, protejându-l pe Teddy cu corpul său.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_14_ACTIVE`
- **Condiție de deblocare**: `Misiunea 13: Încolțit` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_14_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 15: Trădarea`.

# Misiunea 25: Capcana
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Emilian
**Recompense**: 0 EUR (Misiune de Evadare)
**Prerechizite (Prerequisites)**: Misiunea 24: Răzbunarea lui Nicu

---

## Rezumat și Obiective
**Obiectiv Principal**: Emilian îl atrage pe Relu într-o capcană la un bloc turn din Pantelimon, sub pretextul unei noi sarcini. Când Relu ajunge, clădirea este înconjurată de trupele speciale ale poliției (mascați). Jucătorul trebuie să treacă prin apartamente, să urce pe acoperiș, să sară pe schelele exterioare de reabilitare a blocului și să evadeze prin ghena de gunoi pentru a scăpa de arest.

### Obiective de Gameplay:
- [ ] Mergi la întâlnirea aranjată de Emilian la un bloc turn.
- [ ] Realizează că este o capcană și că ești înconjurat de mascați.
- [ ] Evadează din clădire folosind acoperișurile și ghenele de gunoi.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Emilian: 'Sfârșitul jocului, Relu! De data asta nu mai scapi!'
- Relu: 'Niciodată să nu spui niciodată, gaborule.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Mascați înarmați până în dinți urcă pe scările blocului, spărgând uși.**
- **[Cadru 2] Relu aleargă pe acoperișul din smoală al blocului gri, sub lumina reflectoarelor unui elicopter.**
- **[Cadru 3] Relu sare într-un container mare de gunoi din spatele blocului, scăpând la limită.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_25_ACTIVE`
- **Condiție de deblocare**: `Misiunea 24: Răzbunarea lui Nicu` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_25_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 26: Pactul`.

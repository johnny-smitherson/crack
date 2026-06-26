# Misiunea 03: O Escortă de Protejat
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 400 EUR, Pistol 9mm
**Prerechizite (Prerequisites)**: Misiunea 2: Recuperare de Noapte

---

## Rezumat și Obiective
**Obiectiv Principal**: Nico îl trimite pe Relu să rezolve o dispută la un hotel local unde fetele de sub protecția Căpitanului sunt hărțuite de interlopi din Ferentari. Jucătorul trebuie să folosească tehnici de stealth sau luptă deschisă pentru a curăța hotelul de intrusi, demonstrând că Pantelimonul aparține Căpitanului.

### Obiective de Gameplay:
- [ ] Mergi la hotelul 'Lebăda' din Pantelimon.
- [ ] Asigură paza fetelor Căpitanului.
- [ ] Elimină bodyguarzii clanului rival din Ferentari.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nico: 'Vezi că băieții ăia de la Ferentari au cam trecut granița. Du-te și arată-le unde le e locul.'
- Relu: 'Se rezolvă. Fără zgomot.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu coboară din Logan în parcarea hotelului, verificându-și pistolul sub geacă.**
- **[Cadru 2] Relu îl prinde pe la spate pe un paznic rival în holul hotelului.**
- **[Cadru 3] Fetele stau speriate într-un colț al camerei în timp ce Relu curăță zona.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_03_ACTIVE`
- **Condiție de deblocare**: `Misiunea 2: Recuperare de Noapte` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_03_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 4: Băiatul Șefului`.

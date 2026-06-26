# Misiunea 01: Taximetria pe GPL
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 100 EUR, Respect +10
**Prerechizite (Prerequisites)**: Niciuna (Misiune de început)

---

## Rezumat și Obiective
**Obiectiv Principal**: Relu își începe ziua conducând Dacia Logan galbenă în zona Pantelimon. Trebuie să transporte 3 clienți diferiți, fiecare având replici tipice românești (un pensionar revoltat de prețuri, un corporatist grăbit și un bețiv prietenos). După finalizarea curselor, Nico îl sună pe Relu și îi spune că are o treabă de recuperare la barul lui nea Sandu de lângă Spitalul Pantelimon.

### Obiective de Gameplay:
- [ ] Ia clienții din stația de la Cora Pantelimon.
- [ ] Du-i la destinație în siguranță.
- [ ] Răspunde la apelul telefonic de la Nico.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Client 1 (pensionar): 'Băi băiatule, pe vremea mea biletul de tramvai era 50 de bani, tu-mi ceri 20 de lei până la Delfinului?!'
- Nico: 'Relu, lasă clienții ăia amărâți. Avem o problemă la barul lui Sandu. Mișcă-te!'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu stă la volanul Daciei Logan galbene, uitându-se plictisit la ceasul de la Cora Pantelimon.**
- **[Cadru 2] Un pensionar cu sacoșe de rafie urcă pe bancheta din spate bodogănind.**
- **[Cadru 3] Relu primește un telefon pe un Nokia 3310 vechi, fața lui devenind brusc serioasă.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_01_ACTIVE`
- **Condiție de deblocare**: `Niciuna (Misiune de început)` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_01_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 2: Recuperare de Noapte`.

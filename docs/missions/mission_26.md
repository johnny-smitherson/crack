# Misiunea 26: Pactul
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Nicu
**Recompense**: 1000 EUR
**Prerechizite (Prerequisites)**: Misiunea 25: Capcana

---

## Rezumat și Obiective
**Obiectiv Principal**: Relu se întâlnește cu Nicu la un depozit de fier vechi din Pantelimon. Nicu îi propune să-l ajute să-l elimine pe Căpitanu', promițând că familia lui Relu nu va fi atinsă. În timpul discuției, Relu observă doi dintre oamenii Căpitanului care îi spionau. Trebuie să-i urmărească și să-i elimine înainte de a raporta Căpitanului despre întâlnire.

### Obiective de Gameplay:
- [ ] Mergi la întâlnirea secretă cu Nicu la un depozit de fier vechi.
- [ ] Negociază trădarea Căpitanului.
- [ ] Elimină bodyguarzii Căpitanului care te-au spionat.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nicu: 'Hai să terminăm cu moșul ăsta de Căpitanu'. Tu îți vezi de treabă, eu preiau sectorul. Ce zici?'
- Relu: 'Dacă se atinge cineva de familia mea, vă curăț pe toți. Accept pactul.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu și Nicu discută înconjurați de munți de mașini strivite la fier vechi.**
- **[Cadru 2] O urmărire pe jos printre containere: Relu prinde din urmă un spion al Căpitanului.**
- **[Cadru 3] Relu îl strânge de gât pe spion cu o sârmă în spatele unui vagon de tren ruginit.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_26_ACTIVE`
- **Condiție de deblocare**: `Misiunea 25: Capcana` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_26_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 27: Confruntarea Finală`.

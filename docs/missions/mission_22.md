# Misiunea 22: Transport de Constanța
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Toma
**Recompense**: 1000 EUR, Sniper Rifle
**Prerechizite (Prerequisites)**: Misiunea 21: Umbra lui Nea Puiu

---

## Rezumat și Obiective
**Obiectiv Principal**: Toma trimite un transport masiv de marfă de contrabandă (țigări și alcool) către București. Oamenii lui Nicu organizează un baraj rutier pe autostradă pentru a fura marfa. Relu, echipat cu o pușcă cu lunetă (Sniper Rifle) primită de la Toma, trebuie să urce pe un pod peste autostradă, să elimine atacatorii de la distanță și apoi să conducă camionul până în Pantelimon.

### Obiective de Gameplay:
- [ ] Mergi pe autostrada A2 (Autostrada Soarelui).
- [ ] Întâlnește camionul cu marfă de la Constanța.
- [ ] Apără transportul de oamenii lui Nicu.
- [ ] Escortează camionul la depozitul din București.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Toma: 'Transportul ăsta e testul tău, Relu. Dacă marfa nu ajunge, înțelegerea noastră pică.'
- Relu: 'O să ajungă. Punct.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu stă întins pe burtă pe un pod de ciment peste A2, privind prin luneta puștii.**
- **[Cadru 2] Explozii și focuri de armă pe autostradă: o mașină a atacatorilor explodează după ce Relu trage în rezervor.**
- **[Cadru 3] Camionul trece peste resturile barajului, condus de un Relu impasibil.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_22_ACTIVE`
- **Condiție de deblocare**: `Misiunea 21: Umbra lui Nea Puiu` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_22_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 23: Jocul Dublu al lui Nico`.

# Misiunea 23: Jocul Dublu al lui Nico
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 600 EUR
**Prerechizite (Prerequisites)**: Misiunea 22: Transport de Constanța

---

## Rezumat și Obiective
**Obiectiv Principal**: Nico este disperată: Emilian a realizat că ea a încercat să-l mintă și plănuiește să o elimine. Ea îi cere ajutorul lui Relu pentru a fugi din țară. Relu trebuie să meargă în cartierul Colentina la un falsificator de documente extrem de dubios, să recupereze un pașaport fals sub amenințarea pistolului și să i-l livreze lui Nico la un motel, ajutând-o să treacă nevăzută de oamenii lui Emilian.

### Obiective de Gameplay:
- [ ] Întâlnește-te cu Nico la un hotel de tranzit.
- [ ] Află că Emilian vrea să o omoare.
- [ ] Obține pașaportul fals de la falsificatorul din Colentina.
- [ ] Predă pașaportul lui Nico și ajută-o să fugă.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nico: 'Relu, Emilian e nebun! O să mă omoare! Trebuie să plec din țară acum!'
- Falsificator: 'Băiatu', pașaportul ăsta costă dublu acum că e grabă.'
- Relu (punându-i pistolul la tâmplă): 'Plătesc cu plumb dacă nu mi-l dai acum.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu îl strânge de gât pe falsificator peste o masă plină de vopsele și prese de imprimat.**
- **[Cadru 2] Nico stă speriată la fereastra unui motel ieftin, privind spre parcare unde patrulează o mașină suspectă.**
- **[Cadru 3] Nico fuge pe ușa din spate a motelului, strângând pașaportul la piept.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_23_ACTIVE`
- **Condiție de deblocare**: `Misiunea 22: Transport de Constanța` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_23_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 24: Răzbunarea lui Nicu`.

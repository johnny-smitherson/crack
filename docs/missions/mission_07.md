# Misiunea 07: Suspiciuni de Soție
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Gina
**Recompense**: 150 EUR
**Prerechizite (Prerequisites)**: Misiunea 6: Fiorul Dragostei

---

## Rezumat și Obiective
**Obiectiv Principal**: Gina este convinsă că Relu are o amantă din cauza parfumului de pe hainele sale (parfumul lui Nico). Îl trimite pe fratele ei, Sabin, să-l urmărească. Relu observă că este urmărit de o rablă de mașină în timp ce merge la Cora. Jucătorul trebuie să-și piardă urma, apoi să se furișeze în spatele mașinii lui Sabin și să-i taie cablurile de la motor pentru a-i opri urmărirea.

### Obiective de Gameplay:
- [ ] Du-te acasă la Gina.
- [ ] Mergi la magazinul Cora Pantelimon.
- [ ] Urmărește-l pe Sabin (fratele Ginei) care te spionează.
- [ ] Dezactivează mașina lui Sabin fără să fii văzut.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Gina: 'De unde miroși așa, Relule? Iar ai reparat mașina vreunei dudui?'
- Relu: 'E de la odorizantul de taxi, Gina. Lasă-mă în pace.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Gina stă cu mâinile în șolduri în bucătărie, certându-l pe Relu care mănâncă ciorbă.**
- **[Cadru 2] Sabin privește printr-un binoclu dintr-o Dacia veche parcată la colțul blocului.**
- **[Cadru 3] Relu sabotează motorul mașinii lui Sabin cu un clește, zâmbind ironic.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_07_ACTIVE`
- **Condiție de deblocare**: `Misiunea 6: Fiorul Dragostei` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_07_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 8: Afaceri de Familie`.

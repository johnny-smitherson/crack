# Misiunea 38: Ochi pentru Ochi
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Relu
**Recompense**: 1000 EUR
**Prerechizite (Prerequisites)**: Misiunea 37: Obsesia lui Emilian

---

## Rezumat și Obiective
**Obiectiv Principal**: Emilian fuge când vede că planul lui a eșuat. Urmează o urmărire intensă cu mașini pe Șoseaua Pantelimon. Jucătorul trebuie să lovească mașina lui Emilian până când aceasta se izbește de un stâlp de tramvai. Emilian coboară rănit și trage în Relu. Misiunea se încheie cu executarea lui Emilian de către Relu în mijlocul străzii, sub privirile trecătorilor îngroziți.

### Obiective de Gameplay:
- [ ] Urmărește-l pe Emilian care încearcă să fugă cu o mașină de poliție.
- [ ] Provoacă un accident mașinii sale pe Șoseaua Pantelimon.
- [ ] Execută-l pe Emilian într-o confruntare directă.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Emilian (plângând și râzând): 'Nu mă poți ucide, Relu... sunt legea...'
- Relu: 'Aici, în Pantelimon, legea o scriu eu cu barosul.' (Trage un glonț în cap)
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] O mașină de poliție Logan albastră derapează violent pe linia de tramvai de pe Șoseaua Pantelimon.**
- **[Cadru 2] Emilian stă sprijinit de stâlpul de beton al tramvaiului, cu fața plină de sânge, trăgând haotic.**
- **[Cadru 3] Relu stă în picioare deasupra lui Emilian, cu arma îndreptată spre el, sub cerul gri al Bucureștiului.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_38_ACTIVE`
- **Condiție de deblocare**: `Misiunea 37: Obsesia lui Emilian` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_38_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 39: Tăierea Legăturilor`.

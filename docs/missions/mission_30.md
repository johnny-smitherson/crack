# Misiunea 30: Presiunea Gaborilor
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Teddy
**Recompense**: 800 EUR
**Prerechizite (Prerequisites)**: Misiunea 29: Noua Ordine

---

## Rezumat și Obiective
**Obiectiv Principal**: Emilian a pus presiune pe toate patrulele din cartier. Teddy și Relu trebuie să mituiască un comisar (Sabău) pentru a slăbi controalele. Relu livrează geanta într-o parcare subterană din Pantelimon, dar tranzacția este supravegheată de agenți de la afaceri interne. Jucătorul trebuie să elimine spionii înainte ca aceștia să raporteze.

### Obiective de Gameplay:
- [ ] Mergi la sediul poliției din sectorul 2.
- [ ] Întâlnește-te cu polițistul corupt Sabău.
- [ ] Livrează geanta cu mită de 20.000 EUR.
- [ ] Elimină agenții secreți care monitorizează tranzacția.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Sabău: 'Emilian e nebun, băieți. Nu mai pot să-l țin în frâu mult timp. Riscul e mare, mă costă mai mult.'
- Relu: 'Banii sunt aici. Ai grijă să nu vedem gabori pe stradă diseară.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] O parcare subterană slab iluminată, cu stâlpi de beton plini de igrasie.**
- **[Cadru 2] Relu îi predă comisarului Sabău o geantă sport neagră prin geamul mașinii.**
- **[Cadru 3] Relu elimină cu un pistol cu silențios doi agenți ascunși într-o mașină utilitară.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_30_ACTIVE`
- **Condiție de deblocare**: `Misiunea 29: Noua Ordine` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_30_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 31: Magazinul de Electrocasnice`.

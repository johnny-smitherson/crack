# Misiunea 32: Dispariția lui Nico
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 800 EUR
**Prerechizite (Prerequisites)**: Misiunea 31: Magazinul de Electrocasnice

---

## Rezumat și Obiective
**Obiectiv Principal**: Nico a fost capturată de Emilian și închisă într-un motel pe DN1 pentru a fi interogată și torturată. Relu primește un indiciu despre locație. Trebuie să se infiltreze în motel, să elimine oamenii lui Emilian și să o salveze pe Nico, care este într-o stare fizică critică în subsolul clădirii.

### Obiective de Gameplay:
- [ ] Mergi la ultimul semnal al telefonului lui Nico pe DN1.
- [ ] Infiltrează-te în motelul suspect.
- [ ] Elimină gărzile de corp ale lui Emilian.
- [ ] Eliberează-o pe Nico din subsol.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nico (mesaj slab): 'Relu... ajutor... e subsolul de la...'
- Relu: 'Rezistă, Nico. Vin acum.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu taie curentul electric al motelului de la panoul exterior.**
- **[Cadru 2] Relu curăță holurile motelului folosind un pistol cu amortizor sub lumina roșie de urgență.**
- **[Cadru 3] Relu o găsește pe Nico legată de un scaun în subsolul inundat, tăindu-i sforile.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_32_ACTIVE`
- **Condiție de deblocare**: `Misiunea 31: Magazinul de Electrocasnice` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_32_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 33: Avertismentul lui Toma`.

# Misiunea 09: Doctorul vine la Bloc
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Căpitanu'
**Recompense**: 800 EUR
**Prerechizite (Prerequisites)**: Misiunea 8: Afaceri de Familie

---

## Rezumat și Obiective
**Obiectiv Principal**: Căpitanu' anunță că 'Doctorul', un asociat periculos și influent de la Constanța, vine în vizită pentru a inspecta facilitățile. Relu trebuie să meargă rapid la sala sa de box din subsolul blocului și să mute toate armele și pachetele suspecte într-un apartament vecin înainte ca Doctorul să ajungă. Urmează o scenă de dialog tensionată în care orice greșeală de răspuns poate fi fatală.

### Obiective de Gameplay:
- [ ] Mergi la sala de box a lui Relu.
- [ ] Curăță sala de arme și droguri ascunse.
- [ ] Întâmpină-l pe 'Doctorul' și arată-i respect.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Căpitanu': 'Vine Doctorul, Relule. Dacă găsește ceva în neregulă, ne curăță pe toți.'
- Doctorul: 'Interesant loc ai aici, Relu. Sper că ești la fel de curat pe cât pari.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu aruncă saci plini de arme printr-o fereastră de subsol direct în portbagajul taxiului.**
- **[Cadru 2] Un bărbat elegant, la costum (Doctorul), coboară dintr-o limuzină neagră în fața blocului gri.**
- **[Cadru 3] Doctorul își trece degetul peste un sac de box, privind fix în ochii lui Relu.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_09_ACTIVE`
- **Condiție de deblocare**: `Misiunea 8: Afaceri de Familie` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_09_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 10: Acasă la Relu`.

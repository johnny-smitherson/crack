# Misiunea 37: Obsesia lui Emilian
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Gina
**Recompense**: 500 EUR
**Prerechizite (Prerequisites)**: Misiunea 36: Întoarcerea Acasă

---

## Rezumat și Obiective
**Obiectiv Principal**: Emilian, complet obsedat și paranoic, l-a răpit pe Chuckie pentru a-l forța pe Relu să vină la o confruntare finală. Relu merge la fabrica abandonată de sticlă din Pantelimon. Locația este plină de capcane cu fir (tripwires) și explozibili. Jucătorul trebuie să dezactiveze capcanele, să elimine ultimii gabori fideli lui Emilian și să-l salveze pe Chuckie înainte ca o bombă cu ceas să explodeze.

### Obiective de Gameplay:
- [ ] Răspunde la apelul plin de panică al Ginei.
- [ ] Mergi la fosta fabrică de sticlă din Pantelimon.
- [ ] Elimină capcanele explozive ale lui Emilian.
- [ ] Salvează-l pe Chuckie din mâinile lui Emilian.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Gina: 'Relu! Emilian l-a luat pe Chuckie din fața blocului! A zis că dacă nu vii la fabrica de sticlă, îl omoară!'
- Emilian (prin difuzor): 'Timpul trece, Relu! Ai 5 minute să-ți salvezi băiatul!'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Chuckie este legat de un stâlp de metal în mijlocul unei hale pline de cioburi de sticlă, cu un cronometru roșu clipind lângă el.**
- **[Cadru 2] Relu taie cu grijă firul unei grenade montate la intrarea în hală.**
- **[Cadru 3] Relu îl strânge în brațe pe Chuckie speriat, în timp ce în fundal se văd resturile capcanei dezactivate.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_37_ACTIVE`
- **Condiție de deblocare**: `Misiunea 36: Întoarcerea Acasă` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_37_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 38: Ochi pentru Ochi`.

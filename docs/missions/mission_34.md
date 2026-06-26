# Misiunea 34: Trădătorul
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Teddy
**Recompense**: 700 EUR
**Prerechizite (Prerequisites)**: Misiunea 33: Avertismentul lui Toma

---

## Rezumat și Obiective
**Obiectiv Principal**: Teddy descoperă că unul dintre băieții vechi ai Căpitanului oferă informații direct lui Emilian. Jucătorul trebuie să-l identifice la o bodegă din Pantelimon, să-l urmărească discret și să-l răpească introducându-l în portbagajul Daciei Logan. Misiunea se termină cu o scenă interactivă de interogatoriu în subsolul blocului unde Relu folosește un clește și un baros pentru a scoate adevărul.

### Obiective de Gameplay:
- [ ] Identifică trădătorul din interiorul clanului.
- [ ] Urmărește-l pe trădător prin cartier.
- [ ] Răpește-l și du-l în subsolul unui bloc.
- [ ] Interroghează-l pentru a afla ce i-a spus lui Emilian.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Trădător: 'Nu i-am spus nimic important, jur! Emilian m-a bătut, n-am avut de ales!'
- Relu: 'Alegerea o faci acum: îmi spui tot sau nu mai pleci de aici pe picioare.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu îl urmărește pe trădător mergând pe o alee întunecată printre blocuri.**
- **[Cadru 2] Relu îl lovește pe trădător în stomac, băgându-l cu forța în portbagajul taxiului galben.**
- **[Cadru 3] În subsol, sub o singură lumină chioară, Relu ține un baros deasupra genunchilor trădătorului.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_34_ACTIVE`
- **Condiție de deblocare**: `Misiunea 33: Avertismentul lui Toma` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_34_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 35: O Vizită la Constanța`.

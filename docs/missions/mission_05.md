# Misiunea 05: Doi la Preț de Unul
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Căpitanu'
**Recompense**: 500 EUR, Uzi
**Prerechizite (Prerequisites)**: Misiunea 4: Băiatul Șefului

---

## Rezumat și Obiective
**Obiectiv Principal**: Relu și Teddy merg la Piața Obor pentru a strânge taxa săptămânală de la florari. Câțiva bișnițari locali refuză și cheamă poliția locală. Relu și Teddy trebuie să fugă printre tarabe, să urce în Logan și să scape de poliție printr-o urmărire intensă pe străduțele înguste din spatele pieței.

### Obiective de Gameplay:
- [ ] Ia-l pe Teddy de la sala de box.
- [ ] Mergi la Piața Obor.
- [ ] Recuperează taxa de la tarabagiii de flori.
- [ ] Scapă de gaborii care patrulează zona.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Teddy: 'Relu, vin gaborii! Ce facem?'
- Relu: 'Calm. Urcă în mașină și ține-te bine de mâner.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Vânzătoarele de flori țipă în timp ce Relu răstoarnă o tarabă pentru a bloca gaborii.**
- **[Cadru 2] Loganul galben virează strâns pe două roți pe o străduță plină de gropi din Obor.**
- **[Cadru 3] Teddy zâmbește plin de adrenalină după ce au scăpat de mașina de poliție.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_05_ACTIVE`
- **Condiție de deblocare**: `Misiunea 4: Băiatul Șefului` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_05_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 6: Fiorul Dragostei`.

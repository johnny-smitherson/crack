# Misiunea 18: Cadoul Căpitanului
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Căpitanu'
**Recompense**: 400 EUR, Uzi
**Prerechizite (Prerequisites)**: Misiunea 17: Nuntă cu Scântei

---

## Rezumat și Obiective
**Obiectiv Principal**: Căpitanu' le oferă tinerilor căsătoriți o casă naționalizată în sectorul 2, dar aceasta este ocupată abuziv de o bandă de recuperatori rivali asociați cu Nicu (interlopul întors din Spania). Relu și Teddy merg să 'elibereze' proprietatea cu forța, folosind bâte de baseball și arme ușoare.

### Obiective de Gameplay:
- [ ] Mergi la casa primită cadou de tineri în sectorul 2.
- [ ] Elimină ocupanții ilegali trimiși de o bandă rivală.
- [ ] Asigură perimetrul pentru mutare.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Teddy: 'Tatăl meu ne-a dat casa asta, dar băieții ăștia zic că e a lor. Relu, ce facem?'
- Relu: 'Ce știm mai bine. Scoate bâta.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] O vilă veche, dărăpănată, cu graffiti pe pereți, înconjurată de curte plină de gunoaie.**
- **[Cadru 2] Teddy lovește cu o bâtă de baseball ușa de la intrare, spărgând lemnul putred.**
- **[Cadru 3] Relu amenință un interlop plin de tatuaje care fuge disperat peste gard.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_18_ACTIVE`
- **Condiție de deblocare**: `Misiunea 17: Nuntă cu Scântei` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_18_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 19: Inspectorul Psihopat`.

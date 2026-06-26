# Misiunea 27: Confruntarea Finală
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Gina
**Recompense**: 500 EUR, AK-47
**Prerechizite (Prerequisites)**: Misiunea 26: Pactul

---

## Rezumat și Obiective
**Obiectiv Principal**: Nicu trădează pactul și trimite o echipă de ucigași direct la apartamentul lui Relu pentru a-i elimina familia și a nu lăsa martori. Jucătorul ajunge chiar în momentul în care ușa este spartă. Trebuie să-și folosească arsenalul pentru a curăța apartamentul și scara blocului de atacatori, protejându-și familia îngrozită.

### Obiective de Gameplay:
- [ ] Mergi de urgență la apartamentul lui Relu.
- [ ] Apără apartamentul de asaltul oamenilor lui Nicu (care au trădat pactul).
- [ ] Du-i pe Gina și Chuckie într-un loc sigur.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Gina: 'Relu! Trag în noi! Ajutor!'
- Relu: 'Gina, Chuckie, sub pat! Acum!'
- Relu (încărcând AK-47): 'V-ați luat de cine nu trebuie, gunoaielor!'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Ușa apartamentului lui Relu este spulberată de gloanțe, Gina țipând în bucătărie.**
- **[Cadru 2] Relu trage o rafală de AK-47 pe holul îngust al blocului, doborând doi atacatori.**
- **[Cadru 3] Relu îi urcă pe Gina și Chuckie speriați în Loganul plin de găuri de gloanțe.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_27_ACTIVE`
- **Condiție de deblocare**: `Misiunea 26: Pactul` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_27_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 28: Sânge pe Zăpadă`.

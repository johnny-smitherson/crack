# Misiunea 24: Răzbunarea lui Nicu
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Căpitanu'
**Recompense**: 800 EUR, Shotgun
**Prerechizite (Prerequisites)**: Misiunea 23: Jocul Dublu al lui Nico

---

## Rezumat și Obiective
**Obiectiv Principal**: Nicu lansează un atac direct asupra teritoriului lui Relu pentru a trimite un mesaj Căpitanului. Sala de box a lui Relu este asaltată de zeci de oameni înarmați. Jucătorul trebuie să apere sala folosind un arsenal variat (shotgun, pistol, grenade), transformând subsolul blocului într-un adevărat câmp de luptă.

### Obiective de Gameplay:
- [ ] Mergi de urgență la sala de box a lui Relu.
- [ ] Apără sala de asaltul oamenilor lui Nicu.
- [ ] Elimină toți atacatorii și securizează zona.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nicu (mesaj audio): 'Relule, ai crezut că ești șmecher cu Constanța ta? Îți dărâm tot cartierul, spaniolule!'
- Relu: 'Ne vedem la sală, Nicu. Adu mulți oameni.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Oamenii lui Nicu sparg ușile sălii de box aruncând cocteiluri Molotov.**
- **[Cadru 2] Relu trage cu un shotgun din spatele unui stâlp de beton, în timp ce gloanțele distrug oglinzile din sală.**
- **[Cadru 3] Cadavre de interlopi zac pe ringul de box acoperit de cioburi și fum.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_24_ACTIVE`
- **Condiție de deblocare**: `Misiunea 23: Jocul Dublu al lui Nico` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_24_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 25: Capcana`.

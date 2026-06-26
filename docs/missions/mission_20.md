# Misiunea 20: Spălare de Bani
**Sezon / Episod corelat**: Sezonul 2 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 800 EUR
**Prerechizite (Prerequisites)**: Misiunea 19: Inspectorul Psihopat

---

## Rezumat și Obiective
**Obiectiv Principal**: Nico are nevoie de ajutorul lui Relu pentru a rula banii murdari proveniți din prostituție și contrabandă prin intermediul unei spălătorii auto și a unei case de amanet. În timpul transportului banilor, Relu este atacat în trafic de doi motocicliști înarmați trimiși de Nicu. Jucătorul trebuie să conducă defensiv, să-i elimine pe urmăritori și să predea banii în siguranță.

### Obiective de Gameplay:
- [ ] Mergi la spălătoria auto a clanului din Pantelimon.
- [ ] Colectează încasările fictive.
- [ ] Transportă banii la firma de amanet din Obor.
- [ ] Elimină hoții care încearcă să te jefuiască pe drum.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Nico: 'Banii ăștia trebuie spălați repede. Ai grijă, Nicu a aflat de traseu.'
- Relu: 'Să încerce doar să se apropie de mașină.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu numără teancuri de bancnote murdare într-un birou mic din spatele spălătoriei auto.**
- **[Cadru 2] O urmărire pe șoseaua Pantelimon: Relu lovește cu portiera Loganului un motociclist înarmat.**
- **[Cadru 3] Relu intră în casa de amanet cu o geantă sport neagră, lăsând în urmă o epavă de motocicletă arzând.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_20_ACTIVE`
- **Condiție de deblocare**: `Misiunea 19: Inspectorul Psihopat` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_20_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 21: Umbra lui Nea Puiu`.

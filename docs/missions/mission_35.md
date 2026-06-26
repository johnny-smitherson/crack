# Misiunea 35: O Vizită la Constanța
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Toma
**Recompense**: 1500 EUR, Combat Sniper
**Prerechizite (Prerequisites)**: Misiunea 34: Trădătorul

---

## Rezumat și Obiective
**Obiectiv Principal**: Toma dorește eliminarea șefului vămii din portul Constanța, care a refuzat șpaga și blochează transporturile. Relu merge la Constanța, se infiltrează în zona industrială a portului noaptea, urcă pe o macara gigantică și execută ținta de la distanță mare folosind o pușcă cu lunetă avansată (Combat Sniper).

### Obiective de Gameplay:
- [ ] Mergi la Constanța la vila lui Toma.
- [ ] Acceptă misiunea de asasinat asupra șefului vămii portuare.
- [ ] Infiltrează-te în zona restricționată a portului.
- [ ] Elimină ținta cu o armă cu lunetă de pe o macara.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Toma: 'Vameșul ăsta crede că e cinstit. Arată-i că cinstea se plătește cu viața în portul meu.'
- Relu: 'Sunt pe macara. Ținta e în vizor. Tragi-mi aer în piept. (Foc)'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu urcă treptele de fier ale unei macarale portuare uriașe, sub ploaia măruntă.**
- **[Cadru 2] Vizorul lunetei încadrează capul vameșului care discută la telefon în biroul său cu geamuri mari.**
- **[Cadru 3] Geamul se sparge în mii de bucăți în timp ce vameșul cade peste birou, ucis pe loc.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_35_ACTIVE`
- **Condiție de deblocare**: `Misiunea 34: Trădătorul` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_35_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 36: Întoarcerea Acasă`.

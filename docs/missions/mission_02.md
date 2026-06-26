# Misiunea 02: Recuperare de Noapte
**Sezon / Episod corelat**: Sezonul 1 (GTA Vice City Style)
**Client / Giver**: Nico
**Recompense**: 300 EUR, Pumnal
**Prerechizite (Prerequisites)**: Misiunea 1: Taximetria pe GPL

---

## Rezumat și Obiective
**Obiectiv Principal**: Relu ajunge la barul lui Sandu. Acesta refuză să plătească și îl atacă pe Relu cu o bâtă. Relu îl pune la pământ cu câțiva pumni bine plasați. Unul dintre oamenii lui Sandu sare la bătaie, dar Relu îl lovește prea tare și acesta rămâne inert. Realizând că l-a omorât din greșeală, Relu îl pune în portbagajul Daciei și conduce până la marginea lacului Pantelimon pentru a scăpa de cadavru sub acoperirea nopții.

### Obiective de Gameplay:
- [ ] Mergi la barul lui nea Sandu în Pantelimon.
- [ ] Intimidează-l pe Sandu pentru a plăti datoria de 2000 EUR.
- [ ] Ascunde corpul agresorului în portbagaj.
- [ ] Aruncă corpul în Lacul Pantelimon.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Sandu: 'N-am banii, băi Relule! Spune-i Căpitanului că-i dau săptămâna viitoare!'
- Relu: 'Căpitanu' nu așteaptă. Iar eu nu-mi bat gura degeaba.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Relu intră în barul întunecat și plin de fum, unde Sandu stă speriat la masă.**
- **[Cadru 2] Luptă corp la corp: Relu îi dă un croșeu de stânga unui bodyguard, care cade secerat în spatele tejghelei.**
- **[Cadru 3] Relu trage trupul inert pe pământul noroios de lângă Lacul Pantelimon, sub lumina palidă a Lunii.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_02_ACTIVE`
- **Condiție de deblocare**: `Misiunea 1: Taximetria pe GPL` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_02_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Misiunea 3: O Escortă de Protejat`.

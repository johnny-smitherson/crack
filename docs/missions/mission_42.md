# Misiunea 42: Umbre în Pantelimon
**Sezon / Episod corelat**: Sezonul 3 (GTA Vice City Style)
**Client / Giver**: Niciunul (Misiune Finală)
**Recompense**: Respect Maxim, Licență de Taxi de Aur
**Prerechizite (Prerequisites)**: Misiunea 41: Răfuiala de la Constanța

---

## Rezumat și Obiective
**Obiectiv Principal**: Misiunea finală a jocului. Relu se întoarce în Pantelimon. Totul este liniștit acum, dar el este complet singur—familia lui este în siguranță în Spania, șefii și inamicii sunt toți morți. Relu își pornește taxiul Logan și parchează la Cora Pantelimon, privind apusul peste blocuri. O persoană misterioasă urcă pe bancheta din spate și îi cere să meargă spre o destinație secretă. Relu zâmbește amar, bagă în viteză și pornește mașina în timp ce genericul de final începe să ruleze pe o piesă de hip-hop românesc (B.U.G. Mafia - Pantelimonu' petrece). Fades to black.

### Obiective de Gameplay:
- [ ] Mergi în parcarea de la Cora Pantelimon.
- [ ] Urcă în Loganul galben.
- [ ] Așteaptă ultimul pasager.

---

## Dialoguri în Română (Slang de Pantelimon)
```dialogue
- Pasager: 'Salut, șefu'. Mergem până în Ferentari?'
- Relu (privind în oglinda retrovizoare): 'Mergem oriunde vrei tu, prietene. Avem timp.'
```

---

## Storyboard (Cadre Manga/Hentai - Prompturi Vizuale)
Acest storyboard conține descrierea cadrelor vizuale care ilustrează acțiunea misiunii pentru a ghida artistul grafic:

- **[Cadru 1] Loganul galben stă singur sub cerul roșiatic al apusului în parcarea Cora Pantelimon.**
- **[Cadru 2] O mână deschide portiera din spate, lăsând să se vadă doar pantofi eleganți de piele.**
- **[Cadru 3] Mașina pleacă spre șoseaua Pantelimon, pierzându-se printre blocurile gri în timp ce genericul rulează.**

---

## Mașina de Stări a Jocului (Game State Machine)
- **Stare curentă**: `MISSION_42_ACTIVE`
- **Condiție de deblocare**: `Misiunea 41: Răfuiala de la Constanța` finalizată.
- **Tranziție**: La finalizarea tuturor obiectivelor, starea devine `MISSION_42_COMPLETED`.
- **Următoarea Misiune Deblocată**: `Sfârșitul Jocului (Joc Finalizat)`.

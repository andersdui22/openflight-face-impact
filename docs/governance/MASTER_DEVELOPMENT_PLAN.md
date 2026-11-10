# OpenFlight Face Impact — MASTER DEVELOPMENT PLAN V1.2

**Dato:** 10. november 2026  
**Status:** Godkendt af brugeren efter oprindelig fremlæggelse; arkiveret i GitHub 11. november 2026.  
**Omfang:** 8 faser · 35 Gates.  
**Styrende dokument:** `docs/governance/PROJECT_LAW.md` (Project Law V1).  
**Bemærkning:** Dette er den godkendte *plan*, ikke en live-status. Faktisk fremdrift dokumenteres separat i Active Change Gate, handoff, PR'er og samme-SHA CI. De oprindelige Gate-numre i ældre OpenFlight-arbejde er ikke MDP V1.2-numre.

Planen samler projektet fra kodeanalyse til færdig Windows-applikation. Den skal sikre, at eksisterende funktionalitet ikke mistes, det godkendte dashboard bevares, en brugbar EXE findes allerede i Fase 2, og at præcision aldrig påstås uden fysisk evidens.

## 1. Projektets faste rammer

| Emne | Beslutning |
|---|---|
| Platform | Windows 10/11 |
| Kamera | ELP OV9281 USB |
| Beregningsmotor | Python / OpenCV / NumPy |
| Brugerflade | React / TypeScript / Electron |
| Plan | 8 faser / 35 Gates |

**Formål:** Selvstændig Windows-applikation, som ved hjælp af ELP-kameraet registrerer eller estimerer golfboldens træfpunkt på køllefladen, viser det grafisk og gemmer resultater til senere analyse.

Ingen nødvendige afhængigheder til MLM2PRO, ConnectorNext, Bluetooth, radarmålinger, GSPro eller andre uvedkommende systemer. Eksisterende OpenFlight-kodebase er read-only reference; Gate 32-dashboardet er beskyttet visuelt udgangspunkt.

## 2. Komplet faseplan

| Fase | Område | Gates |
|---|---|---|
| 01 | Analyse og arkitektur | 01–04 |
| 02 | Komplet UI og Windows EXE | 05–11 |
| 03 | Kamera og billedopsamling | 12–15 |
| 04 | Kalibrering og køllemodeller | 16–19 |
| 05 | Impact-måling | 20–24 |
| 06 | Integration og brugerfunktioner | 25–28 |
| 07 | Fysisk validering | 29–32 |
| 08 | Windows-release | 33–35 |

Nummereringen er sammenhængende fra Gate 01 til 35 og må ikke forveksles med tidligere OpenFlight-Gates.

## 3. Fase 1 — Analyse, afhængigheder og arkitektur

**Mål:** Ingen flytning, omskrivning eller fjernelse af kode, før funktioner og afhængigheder er forstået.

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 01 | Komplet read-only audit af repository, branches, PRs, CI, Python, React og Electron | Relevante moduler og forbindelser kortlagt |
| 02 | Matematisk audit: kalibrering, pixelstråler, 3D-pose, boldposition, kontaktgeometri og koordinatsystemer | Inputs, outputs, enheder og antagelser dokumenteret |
| 03 | Klassificering af kode og afhængigheder | Hvert modul: genbrug, tilpas, erstat eller udelad med begrundelse |
| 04 | Ny arkitektur, Project Law, teststrategi og kodegenbrug | Dokumentation godkendt før implementering |

Afhængighedskæden skal dokumenteres: kamera/frame-timestamps → billedbehandling/observationer → kalibrering/3D-koordinater → bold- og køllefladeposition → kontaktberegning/usikkerhed → resultat-API/lagring → dashboard/træfpunkt.

Syntetisk fungerende matematik beviser ikke fysisk måling. Afklar licens, attribution og AGPL-3.0-or-later ved kodegenbrug.

## 4. Fase 2 — Færdigt visuelt program og Windows EXE

**Mål:** Programmet kan åbnes med dobbeltklik, og hele brugerfladen kan prøves før avanceret kameramåling.

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 05 | Nyt GitHub-projekt, struktur og grundlæggende tests | Isoleret fra eksisterende repository |
| 06 | Overfør Gate 32-dashboard med paneler, faner, felter og knapper | Layout visuelt bevaret og responsivt |
| 07 | Grafiske kølleflader: driver, fairwaywood, jern og wedge | Korrekt visning og skalering |
| 08 | UI-handlinger, navigation og indstillinger | Ingen døde knapper; handlinger defineret |
| 09 | Demotilstand med simulerede slag, træfpunkter, sessioner og statistik | Brugeroplevelse uden kamera |
| 10 | Windows-start, Electron, Python-backend og EXE-pakning | Dobbeltklik uden terminal |
| 11 | Visuel og funktionel accepttest | UI, demo, navigation og EXE består tests |

**UI-funktionsregister:** Alle funktioner mærkes *fungerer*, *demotilstand*, *afventer hardware* eller *fejl*. Synlige funktioner efter Fase 2: hoveddashboard, kameravisning, impact-kølleflade, slaghistorik, statistik, kameraindstillinger, kalibrering, sessioner, indstillinger, diagnostik, hjælp/status og demotilstand.

Slutbrugeren må ikke behøve separat Python, Node.js eller manuel serverstart. Kontroller processtart/-stop, manglende filer, fejlmeddelelser og flere baggrundsservere. Hardwareafhængige funktioner må ikke foregive at være færdige.

## 5. Fase 3 — Kamera og billedopsamling

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 12 | ELP OV9281 USB-opdagelse, forbindelse og genoprettelse | Tilslutning, frakobling og genfinding |
| 13 | Opløsning, FPS, eksponering, gain og billedformat | Faktiske værdier måles eller mærkes ukendte |
| 14 | Stabil livevisning og én fælles frame-buffer | Ingen konkurrerende kamera-readers eller blokering |
| 15 | Slagtrigger, pre-/post-shot frames, køstyring og replay | Korrekt sekvensidentitet og tidsinformation |

Skeln mellem ønsket FPS, faktisk FPS og kameraeksponeringens tidspunkt; Windows-modtagelsestid er ikke eksponeringstid. Test langvarig drift, tabte frames, USB-fejl, CPU, hukommelse og flere på hinanden følgende slag.

## 6. Fase 4 — Kalibrering og køllemodeller

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 16 | Kamerakalibrering, linseforvrængning og profil | Reproducerbarhed og dokumenteret fejl |
| 17 | Køllefladens position, orientering og referencepunkter | Verificerede koordinater og transformationer |
| 18 | Køllespecifikke fysiske modeller og dimensioner | Driver, wood, jern og wedge efter egen geometri |
| 19 | Kalibreringsworkflow, lagring og gyldighed | Ugyldig/forældet kalibrering afvises |

Driver og fairwaywood har typisk bulge/roll, mens den oprindelige matematik er plan. Skeln mellem grafisk og fysisk model. Manglende geometri må ikke erstattes af umærket standardmodel.

## 7. Fase 5 — Impact-detektion og beregninger

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 20 | Bolddetektion, kontur og observationskvalitet | Målbar lokaliseringsfejl på testdata |
| 21 | Køllefladedetektion og 3D-pose | Kendte begrænsninger for orientering og position |
| 22 | Kontaktøjeblik og tidsrekonstruktion | Dokumenteret metode for tidspunkt |
| 23 | Impact-koordinater, centrumafstand og fladegrænser | Kontrol mod kendte geometriske cases |
| 24 | Usikkerhedsmodel, kvalitetskontrol og afvisning | Ingen falske træfpunkter ved utilstrækkelige data |

Ved 120 FPS er der ca. 8,3 ms mellem frames, ofte længere end selve bold-kølle-kontakten. Man kan ikke antage, at et frame viser kontaktøjeblikket. Undersøg pålidelig før-/efter-estimation og konsekvenser af vinkel, sløring, lys og manglende dybde. Tilpas eller begræns metoden, hvis præcision ikke kan dokumenteres.

## 8. Fase 6 — Integration og komplette brugerfunktioner

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 25 | Kameramålinger i dashboard | Virkelige data uden layoutændringer |
| 26 | Slaghistorik, sessioner og lagring | Gem, genindlæs og eksporter |
| 27 | Statistik, spredning og køllespecifik analyse | Konsistente, mærkede beregninger |
| 28 | Indstillinger, diagnostik, fejlhåndtering og integrationstest | Sammenhængende system |

Hvert slag har entydigt ID, billedsekvens, køllemodel, kalibrering, beregningsversion og kvalitetsstatus. Slag uden pålideligt træfpunkt skal kunne håndteres uden opdigtet resultat.

## 9. Fase 7 — Fysisk validering og præcision

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 29 | Fysiske ELP/IR-tests med forskellige køller | Opsætning og rådata dokumenteret |
| 30 | Uafhængig reference for træfpunkt | Fejl i millimeter |
| 31 | Gentagelighed, fejlrater og robusthed | Performance under relevante forhold |
| 32 | Præcisionsgodkendelse og optimering | Forudbestemte krav eller dokumenterede begrænsninger |

Brug uafhængig reference, fx impact tape. Et visuelt plausibelt resultat er ikke bevis. Dokumenter X/Y-fejl i mm, P50/P95, gyldige og afviste målinger i %, faktisk FPS og behandlingstid i ms. Tolerancer, antal slag og succeskriterier fastsættes **før** testresultaterne ses.

## 10. Fase 8 — Windows-release

| Gate | Arbejdsopgave | Acceptkriterium |
|---|---|---|
| 33 | Stabilitet, performance, fejl og sikkerhed | Ingen kendte release-blokerende fejl |
| 34 | Installer, opdateringsstrategi og ren-PC-test | Installation, opstart, afinstallation og genstart |
| 35 | Endelig accept, dokumentation og V1.0 | Særskilt godkendt release knyttet til testet SHA |

Test uden udviklingsværktøjer, med relevante drivere, antivirus, Windows-tilladelser og uden internet. Fase 2-EXE er tidlig testversion; Fase 8 er endelig release.

## 11. Project Law — obligatoriske regler

Den eksisterende `PROJECT_LAW.md` forbliver autoritativ og erstattes ikke af denne plan.

1. Ingen ændring uden godkendt Gate med godkendelse, base-SHA, filer, undtagelser, kriterier og stopbetingelser.
2. Read-only startup audit af repository, branch, HEAD, PRs og CI.
3. Kun ændringer inden for Gate-afgrænsningen.
4. Ingen ukontrolleret sletning; forstå afhængigheder og regressioner.
5. Én kameraejer; preview og analyse deler kontrollerede frames.
6. Ærlige målinger; ukendte værdier må ikke opdigtet udfyldes.
7. Tests på samme SHA som godkendes.
8. Ingen skjulte testomgåelser eller falske mocks.
9. Ingen merge eller release uden særskilt godkendelse.
10. Sporbarhed, beslutningslog og handoff.
11. Beskyttede visuelle og fysiske baselines.
12. Stop ved ukendt licens-, afhængigheds-, data- eller Gate-risiko.

## 12. Dokumentation

| Dokument | Formål |
|---|---|
| PROJECT_LAW.md | Regler og godkendelser |
| MASTER_DEVELOPMENT_PLAN.md | Denne plan |
| ACTIVE_CHANGE_GATE.md | Aktuel godkendt Gate |
| ARCHITECTURE.md | Komponenter og dataflow |
| DEPENDENCY_REGISTER.md | Afhængigheder og genbrug |
| MATH_AND_GEOMETRY.md | Formler, koordinater og antagelser |
| UI_FUNCTION_REGISTER.md | Knapper, felter og status |
| TEST_REGISTER.md | Tests, data og fejl |
| HARDWARE_BASELINE.md | Kamera, objektiv, indstillinger og kalibrering |
| DECISION_LOG.md | Beslutninger |
| KNOWN_LIMITATIONS.md | Begrænsninger |
| RELEASE_CHECKLIST.md | Releasekrav |
| HANDOFF.md | Overdragelse mellem sessioner |

Derudover kræves register over tredjepartslicenser, kildeoprindelse, afhængigheder og grafiske aktiver.

## 13. Arbejdsproces og Gate-status

Planlagt betyder ikke implementeret. Hver Gate gennemløber: **Undersøg → Afgræns → Implementér → Test → Verificér samme SHA/CI → Luk Gate**. Status ændres kun med faktisk dokumentation og godkendelse.

## 14. Risici og forebyggelse

| Risiko | Forebyggelse |
|---|---|
| Skjulte afhængigheder | Import- og funktionskort |
| Dashboard ændrer sig | Visuelle regressionstests |
| EXE virker kun på udviklings-PC | Ren Windows-installation |
| Tabte kameraframes | Faktisk FPS og frame-tab |
| Blandede slag | Shot-ID og kø |
| Fejlkalibrering | Kalibrerings-ID og gyldighed |
| Forkert træfpunkt | Usikkerhed og afvisning |
| Forkert 3D-køllemodel | Køllespecifikke mål |
| Kun syntetisk funktion | Fysiske accepttests |
| GitHub-drift | Read-only audit og samme-SHA |
| Overset licens | Oprindelses-/licensregister |
| Glemte funktioner | UI-funktionsregister |

## 15. Definition af færdig V1.0

- Installerbar og dobbeltklik-startbar på almindelig Windows-PC.
- Godkendt dashboard bevaret; alle funktioner har korrekt handling.
- Stabil ELP-drift gennem gentagne slag og lange sessioner.
- Kalibrering og køllemodeller med dokumenterede begrænsninger.
- Fysisk verificeret træfpunktnøjagtighed mod **forudgodkendte** tolerancer.
- Usikre målinger afvises.
- Slaghistorik, statistik, indstillinger og diagnostik fungerer.
- Automatiske og fysiske accepttests bestået.
- Kode, Windows-pakke, licensdokumentation og testresultater spores til samme release.
- Brugeren har særskilt godkendt slutversionen.

**Afsluttende vurdering:** 35 fokuserede Gates er udgangspunktet; yderligere Gates kan blive nødvendige ved tekniske fund. Den centrale tidlige beslutning er, hvilken målenøjagtighed der kræves, og om ét OV9281-kamera realistisk kan levere den. Dette skal afklares, før den endelige målearkitektur låses.

---

**Arkivnote (11. november 2026):** Den oprindelige tekst sluttede med »Forslag V1.2« og »endnu ikke oprettet eller godkendt«. Det beskrev tidspunktet *før* brugerens efterfølgende godkendelse. Planen er siden godkendt. Dette dokument er en struktureret Markdown-gengivelse af den brugerleverede godkendte plan; denne arkivering giver **ikke** ny tilladelse til kodeændringer, Gate-lukning, merge, release eller fysisk test.

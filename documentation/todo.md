revel like engine monitoring dashboard
can view stats in assembly view during playback of flight
animated scenes to follow missile in air


# Backlog (from U_SystemsModellingTool/documentation/todo.md)

# Features
- Phase and stage status, with the output plot colored by the state, fex boost phase/powered flight -> coasting phase/midcourse phase -> terminal phase


# Directories
## modules
### propulsion
### environment
### aerodynamics
### systems


## system_specifications
### SSC-X-9_SKYFALL.py/txt/csv
- read specs from this file, or read directly from excel sheet (ideally) 


# Flysimulator og missilmodellering
- name: TorFlight?
- rename to SystemModellingTool
- TSFC
- Isp beregninger fra brenntid, etc.
- Regne på brennstoffskomposisjon
- Engine cycles for liquid-rocket motor
- Size a liquid-rocket motor from scratch to understand thrust output based on known parameters like nozzle area, fuel etc. 
- Engine cycles for turbojets -> compute stage count -> what assumptions are the calcs based on? Isentropic and those terms, etc. research how these assumptions affect accuracy of stimations. What are its limitations?
- nuclear reactor cycle coupled to Brayton cycle
- Generic heat exchanger to model energy transfer from nuclear reactor
- Hvor mange compressor stages? Avhenger av temp og trykk i heat exchanger - materialer i heat exchanger? Modellere alt dette
- Turbin stages beregne plass, nozzle hvor lang? Alt skal passe bak luftinntak
- Warhead hvor tung?
- Booster er jo montert bak - pusher cog bak ved launch men må fremdeles være stabil så gir mening med reaktor foran? Altså separert arkitektur
- Ramjet / scramjet air intakes model -> what size and shape needed for correct air slow down and mixture with fuel to provide sufficient thrust? 
- Model combustion too
- Atmosfæriske påvirkninger på bane, hastighet, etc. integrere i flysim, full astmosfærisk og gravitasjons-modell, referance frames etc. 
- GUI
- Evasive maneuvres, pull-up maneuvres, feed in how many gs pulled, steering algos, full GNC module
- Missile DATCOM
- Power on C_D vs power-off C_D
- UAVs can be studied too, range etc.
- Flymodell, wing sizing etc. -> CMs
- impact energy, kinetic
- energy saving principle type PID controller for CM
- induced drag, drag polar?, complete lift and drag equations
- static and dynamic stability analysis using laplace, fex. -> especially for CMs but also for BMs
- Reverse engineer fisint signals from my flight sim - use flight sim to log flight data as a real life flight would and see if signals match a pattern
- Model heat effects of reentry, mach nr during reentry, plasma formation that blocks signals-> when do these go away and missile can detect ship? At what altitude? When is plasma present?
- Show heating on aeroballistic / hyperosnic missile vs regular cruise missile (Tsirkon vs STROBILE, fex.) during flight
- Drag at hypersonic - how to model shock waves, correct for plasma and real-gas effects etc. -> Loke thread
- ML for aerodynamic modellling (surrogate model) to get all test cases without having to do CFD/DSMC for each case -> gpt thread 
- compute g-force during maneuvres to ensure no material limits are crossed -> speaks to max pull-up capability, fex, for a missile
- address parameter uncertainty by doing a Monte Carlo sim to characterise the thrust span that may arise
- integrere data fra når søker er på (feks før første pull-up manøver på KILLJOY), og visualisere dette for å iverksette eventuelle mottiltak (tenk: skipsradar kan detektere søker signaler og bruke det til å få track) og forberedelser på at den nærmer seg
- trajectory planner/computer given launch and target pos, too complex?? can do via a script that sims through many trajectories and finds the one with closest hit to target, but can it be solved analytically? NO
    - logic that decides whether to use pull up maneuver, fex -> can help inform collection by predicting trajectories
- simulated INS?
- how do i code a working control system without sensors for feedback? simulate sensors? (add noise etc.)
- coriolis effect
- rotation of earth causing rotation of atm. and hence a "wind effect"?
- RCS calcs
- lage funksjon som lager ny mappe i results med dato for når man gjør en simulering - automatisk
- hypersonic coefficients from FFI project get and use

### Inputs
- Input feks. data fra FISINT -> få ut Isp, fuel composition etc. 
- Input feks. Isp, total impulse, mass, firing angle -> range, speed, trajectory
- Input weights of warheads, number of them etc. to predict range. Can compare conventional vs nuclear payload ranges, fex.
- Dato og grid for nøyaktige historiske atmosfæriske/gravitasjonelle/andre effekter som centrigual data slik at realistisk gjenflygning av en oppskytning kan gjennomføres

### Bygge på
- Integrere OpenFOAM også ---- CAD-model -> OpenFOAM/MissileDATCOM -> Mesh -> solve -> insert coefficients to model -> simulate 
    finnes python libs for import av STL, STEP
    find openFOAM wrapper - put OpenFOAM in requirements
- FFI sammarbeid på CFD/DSMC, kjøre på supercomputere -> bruke CAD av missiler og RVer/MaRV/HGV
- Processing 4 for visuell 3D missil orientering mens den flyr
    - eller python for samme 
- conservation of momentum analysis - determine mass ratio between STG1 and STG2 based on velocity - gir dette mening?? går det?? fra OWG 2026 møte - noen hadde gjort det på RM01
- regne på poseidon fart - plotte to koordinater - launch og der den ender opp - fra feks comint - regn gjennomsnittsfart basert på tiden det tok
- lage cad modeller  programmatisk fra python gjennom solidworks
- importere masse, materialer og andre parametere direkte fra SLDASM fil gjennom python

### Spørsmål man kan svare åå gjennom å simulere, feks , IPBVs like MaRV:
- hvor mye kan de bevege seg rundt?
- begrensninger på hvor fort de kan skifte retning for å feks unngå, komme seg rundt rekkevidden til, luftvern?
- hastighetsprofil som funskjon av høyde, horisontal traversering, hvor mye den veksler kinetisk energi for potensiell energi
- step by step simulere bevegelse gitt gjennom enkle kommandoer som pull up i feks 5 sek
- step by step bevegelse som resultat av PID kontroller output etter signal input fra en simulert flight controller som igjen får signal fra sensor, feks radar
- radar detection range and time to track (based on radar FOV, range, missile speed and earth curvature)
- gitt at et missil, feks SS-N-26, flyr sånn og sånn og man klarer å replikere det nøyaktig, med en detaljert SRM og ramjet-modell, hvilke andre trajectories KAN den gjøre? Hvor mye fart, rekkevidde etc. taper den dersom den må unnvike ting/kjøre rundt, eksempelvis luftforsvarssystemer, på sin vei?

### Modes
- hit target (optimises trajectory)
- hit trajectory (specify type? i.e high, depressed, minimum energy)

### Reverse engineering
- finne thrust ved å teste parametre til fartsprofil er funnet
- think: they have sized the nozzle to optimally expand (i.e P_e=P_atm), for some altitude(which?), the combustion gases. Since the exp_ratio is known, that gamma can be computed (using exp_ratio as func. of pressure ratio formula) and will hence tell or something about the fuel (although not much)

### Visuals
- illustrate radar detection range, particulary of HCM, on graphs based on earth curvature, altitude, plasma sheet from hypersonic speed, or known radar ranges - comment also on engagement time as a result of this
- color code curves based on temparature through flight

## MissileDATCOM integration
- load .STL file directly into FlightSim and a MissileDATCOM wrapper handles it


## Detection and shoot down
- map sensor and interceptor reach based on their specs and location, and incoming missile alt and loc.
- can then infer how to best construct trajectory, pre flight, to fly between AD layers, fex. 
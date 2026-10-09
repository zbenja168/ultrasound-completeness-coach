# Robotic and Autonomous Ultrasound Scanning: State of the Field (as of October 2026)

Scope note: notes compiled 2026-10-08. "Deployed" below means a product sold/used on real patients outside a study; "lab" means a research prototype tested on volunteers, phantoms, or in a single-site pilot. Several key sources (Nature, Springer 2026 reviews) were paywalled; where only abstracts or secondary summaries were accessible this is flagged.

---

## Key Question 1: Which commercial robotic ultrasound systems exist, and what is their regulatory status and real deployment?

### Takeaway
Every robotic ultrasound system that is actually cleared and in clinical use today is either **teleoperated** (a remote human sonographer still drives the probe: MELODY, MGIUS-R3, Wosler, Dopl, Cobionix CODI) or **narrow-task autonomous on a rigid, superficial anatomy** (ROPCA ARTHUR, hand/wrist joints only). No general-purpose autonomous diagnostic scanner (abdomen, cardiac, OB) is cleared anywhere as of Oct 2026; the closest, Corbotics' cardiac "Bed Based Echo," holds only an FDA Breakthrough Device designation, not clearance.

### Cited Findings

**Teleoperated systems (remote human still scans)**

- AdEchoTech **MELODY** (France): FDA 510(k) K161354, decision date 12 June 2017, Class II under 21 CFR 892.1560, substantially equivalent to the SonoCiné ABU breast system. Intended use: hold the transducer of cleared ultrasound equipment so a remotely located expert can manipulate it over the Internet; a trained assistant at the patient site must position the robot frame. Clinical support was >500 patients comparing remote vs on-site sonography. — [FDA 510(k) summary K161354](https://www.accessdata.fda.gov/cdrh_docs/pdf16/K161354.pdf); [Innolitics record](https://fda.innolitics.com/device/K161354)
- MELODY is FDA-cleared for abdominal, pelvic, obstetric, vascular and MSK remote ultrasound but **not** echocardiography, and requires a medical assistant at the patient site holding a frame against the patient. — [Monsky et al., Methodist DeBakey Cardiovasc J, Oct 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513344/)
- First US clinical deployment: RWJ University Hospital / Rutgers performed a transatlantic robotic cardiac tele-ultrasound test on 24 Jan 2022 over a routine 4G network, for several hours in real time. — [RWJBarnabas Health, Feb 2022](https://www.rwjbh.org/blog/2022/february/rwj-university-hospital-and-rutgers-rwj-medical-/)
- Deployment scale: ESA stated (c. 2016) that AdEchoTech had marketed the system to "more than 15 hospitals and health institutes in France and abroad." — [ESA](https://www.esa.int/spaceinimages/Images/2016/02/Live_demonstration). Cayenne and Maripasoula (French Guiana) adopted MELODY in 2012 — [CNES](https://cnes.fr/actualites/grace-aux-satellites-tele-echographie-desenclave-deserts-medicaux); University Hospital of Guadeloupe uses it for teleradiology — [AuntMinnie Europe](https://www.auntminnieeurope.com/industry-news/article/15650497/robotic-ultrasound-advances-telerad-in-france); a 2023 pediatric lung feasibility study ran at CHI Créteil — [CHI Créteil press release, June 2023](https://www.chicreteil.fr/wp-content/uploads/2023/06/CP-CHI-Creteil-Comparaison-entre-lechographie-pulmonaire-conventionnell.pdf). CNES's holding subsidiary took an equity stake in AdEchoTech. — [CNES press](https://presse.cnes.fr/en/node/10829)
- MGI Tech **MGIUS-R3** (China): holds China NMPA Class III approval, CE certification, Australian TGA registration, and Singapore HSA approval (announced March 2023); MGI reported the system in use across 21 provinces/cities/regions in China as of June 2022, via hospital partnerships. — [MGI Tech press release](https://global-mgitech.com/mgius-r3-approved-hsa-singapore/)
- MGI's Sansha Island (Hainan) 5G remote clinic has served "nearly 400 residents" since 2017; named user hospitals include Beijing 301, Shenzhen Luohu People's, Zhongnan Hospital of Wuhan University, and Leishenshan Hospital (2020 COVID use). — [MGI Tech, Taiyuan forum, 24 July 2021](https://global-mgitech.com/mgi-tech-we-believe-the-system-has-a-promising-future-chinese-sonographers-embrace-mgi-remote-robotic-ultrasound-system/)
- Peer-reviewed MGIUS-R3 evidence: a single rural care center in Huzhou, Zhejiang, with 5G link latency under 200 ms. — [Chai et al., Frontiers in Public Health 2022](https://www.frontiersin.org/articles/10.3389/fpubh.2022.915071/full)
- MGI 5G "robotic ultrasound vehicle" drove 1,633 km from Shanghai to Sinan County, Guizhou for a free thyroid-screening week. — [MGI Tech](https://global-mgitech.com/mgi-tech-5g-powered-robotic-ultrasound-vehicle-brings-high-quality-medical-resources-to-the-villages-in-western-china/)
- The Monsky 2025 review (all four authors affiliated with Dopl Technologies) lists MELODY as FDA-approved, MGIUS-R3 as "commercialized in Asia," and Apricity Robotics, Dopl Technologies and Wosler Robotics as "emerging fully telerobotic solutions" with no regulatory status stated. — [Monsky et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513344/)
- **Dopl Technologies** (Bothell, WA): closed a $6.3M seed round in July 2026; 10 employees; >$8M raised total; CEO frames the goal as "telerobotic and autonomous care delivery"; plans to submit to FDA in **2027**. — [MassDevice, July 2026](https://www.massdevice.com/dopl-remote-ultrasound-robot-developer-seed-round/)
- **Cobionix CODI** (Waterloo, Canada): raised ~$3M USD mid-2025 and $4.1M strategic equity (Oct 2025, led by TitletownTech); planned UK launch "by end of year," Canada 2026, US "mid-2026." — [The Robot Report](https://www.therobotreport.com/cobionix-expands-with-3m-strategic-funding/); [BetaKit](https://betakit.com/cobionix-secures-4-1-million-to-commercialize-its-collaborative-medical-robot/). Company said CODI "is already capable of teleoperated ultrasound operation" while it is "perfecting its fully autonomous ultrasound functionality." — [Canadian Healthcare Technology, Sept 2023](https://www.canhealth.com/2023/09/20/company-developing-robot-that-can-do-ultrasounds/). A 2026 event listing calls CODI a "clinician-guided robotic platform for cardiac ultrasound (TTE)" with ISO 13485 / IEC 60601 certification claims. — [b2match listing, Aug 2026](https://www.b2match.com/e/belt-road-summit-2026/opportunities/UGFydGljaXBhdGlvbk9wcG9ydHVuaXR5OjI1MzA0MA==). Clinical trials ongoing at Saskatchewan's Virtual Health Hub. — [UWaterloo RoboHub](https://uwaterloo.ca/robohub/news/justin-trudeau-meet-codi). **No FDA or Health Canada clearance found.**
- **Wosler** (Alberta): Kinova-arm telerobotic system; first remote abdominal scan Wabasca, Alberta ← London, ON (3,500 km) in late 2022; 2023 goal was to "pass all required safety tests and certifications." — [Surgical Robotics Technology / Kinova case study](https://www.surgicalroboticstechnology.com/articles/kinova-startup-story-wosler-diagnostics-remote-telerobotic-ultrasound-solution/); [Alberta Innovates 2023](https://albertainnovates.ca/wp-content/uploads/2023/06/AICE_onepager_wosler.pdf)
- **Apricity Robotics** (Dublin, OH; founded 2022 as Crookes Research): semi-autonomous cardiac telerobotic ultrasound; last raised $1.1M (June 2024); roadmap is "one expert sonographer overseeing multiple scans." — [CB Insights](https://www.cbinsights.com/compare/apricity-robotics-vs-neurasignal)
- **NovaSignal** (formerly Neural Analytics): FDA-cleared NovaGuide robotic transcranial Doppler for cerebral blood flow; last funding Series C Sept 2021. This is a narrow TCD device, not diagnostic imaging. — [Nanalyze](https://www.nanalyze.com/?p=65099)

**Narrow-task autonomous (cleared)**

- **ROPCA ARTHUR** (Denmark; spin-out of U. Southern Denmark / Odense University Hospital, founded 2019): built on the KUKA LBR Med cobot, which was already certified for medical integration, "shortening the path to market." CE mark 2022; in use (c. 2023) in six rheumatology clinics in Denmark, Germany, Switzerland and Austria. Scans 11 joints per hand, ~15 min exam, patient guided by audio/text instructions. — [Today's Medical Developments / KUKA](https://www.todaysmedicaldevelopments.com/article/rheumatoid-arthritis-ultrasound-robot-kuka-medtech-arthur-ropca-aps); [ITU AI for Good](https://aiforgood.itu.int/?p=17119)
- **FDA 510(k) K260190 cleared 18 June 2026** for the ARTHUR + DIANA musculoskeletal ultrasound system (finger, hand, wrist joints); publicly announced Sept 2026; CEO: "We are now ready to build the U.S. clinical and commercial partnerships." — [FDA.report K260190](https://fda.report/PMN/K260190); [MassDevice](https://www.massdevice.com/tag/ropca/)
- Clinical validation (RMD Open, Aug 2025, 30 RA patients, 22 hand joints): ARTHUR successfully scanned **564 of 660 joints (85.5%)**; agreement with rheumatologist: synovial hypertrophy exact 57.9%, close 92.9%, binary 87.3%, kappa 0.38; Doppler exact 77.3%, close 94.2%, binary 91.2%, kappa 0.44. Authors conclude repeatability "on par with intra-expert agreement" but "further refinement is needed... across specific joints." — [Region H research record (RMD Open 2025)](https://research.regionh.dk/en/publications/automated-ultrasound-system-arthur-with-ai-analysis-diana-matches/); [ACR abstract](https://acrabstracts.org/?p=40753); [MDedge coverage](https://mdedge.com/rheumatology/article/271729/rheumatoid-arthritis/ra-assessment-automated-ultrasound-scanner-ai-saves-time-performs-well-rheumatologists)

**Autonomous diagnostic scanners in regulatory pipeline (not cleared)**

- **Corbotics Bed Based Echo (BBE)** (Netherlands): autonomous TTE acquisition without a sonographer at bedside; FDA Breakthrough Device Designation granted June 2026; Aug 2026 distribution partnership with Us2.ai (AI echo measurement/reporting) covering US, EU, UK. No clinical results, pricing, or market timeline disclosed. CEO Adriaan van Donk frames it as reducing "pressure on the sonographer workforce"; Us2.ai's Yoran Hummel: goal is to "extend clinicians' reach rather than replace them." — [The AI Insider, 31 Aug 2026](https://theaiinsider.tech/2026/08/31/corbotics-and-us2-ai-partner-to-combine-ai-and-robotics-for-automated-cardiac-ultrasound-tech/)
- **GE HealthCare + Nvidia**: announced collaboration to test robotics for automating ultrasound and X-ray acquisition (patient positioning, scanning, QC) using Nvidia's Isaac for Healthcare simulation to train autonomous systems virtually before physical deployment. No product or timeline. — [Radiology Business](https://radiologybusiness.com/topics/artificial-intelligence/using-robotics-automate-x-ray-ultrasound-workflows-goal-new-ge-healthcare-nvidia-partnership) (page returned 403 on fetch; date of announcement not verified from the article text; search summary says "March")
- No Philips or Siemens Healthineers robotic ultrasound program surfaced in searches. — [search result](https://radiologybusiness.com/topics/artificial-intelligence/using-robotics-automate-x-ray-ultrasound-workflows-goal-new-ge-healthcare-nvidia-partnership)
- Adjacent but not ultrasound imaging: Vitestro's Aletta venipuncture robot (uses US + NIR for vein finding) received FDA authorization Aug 2026. — [Forbes, 27 Aug 2026](https://www.forbes.com/sites/lesliekatz/2026/08/27/fda-authorizes-autonomous-blood-drawing-robot/)
- "Sonobotics": no company or product by this name was found in searches. — [search](https://arxiv.org/abs/2510.08106v1)
- Market-research sizing (vendor forecasts, treat as estimates): $1.78B (2025) → $2.07B (2026), CAGR 16.5%, $3.77B by 2030. — [The Business Research Company, Feb 2026](https://www.thebusinessresearchcompany.com/report/global-robotic-ultrasound-systems-market-report)

### Inferences
- The regulatory map is clear: teleoperation clears as a probe-holder accessory (MELODY's 510(k) predicate was a *breast positioning* device, not a diagnostic tool), and the only cleared "autonomous" device (ARTHUR) targets a flat, rigid, superficial anatomy where probe placement is almost a 2D problem. Deep-organ autonomous scanning has no regulatory precedent.
- Deployment counts are small and mostly vendor-reported: MELODY "~15+ sites" (2016), ROPCA "6 clinics" (2023), MGI "21 provinces" (2022). Nothing suggests thousands of units; the sector is pilots and single-digit site counts per vendor outside China.
- The 2025-2026 funding activity (Dopl $6.3M, Cobionix $7M, Corbotics breakthrough designation) is modest by medtech standards and concentrated on **cardiac** teleoperation, the exam with the most acute sonographer shortage.

### Gaps
- No current (2025-2026) installed-base numbers for MELODY, MGIUS-R3, or ARTHUR were found; MGI's figures are 2021-2022 press material and unverified.
- Cobionix's claimed UK/Canada/US launches (2025-2026) could not be confirmed as having occurred; no regulatory filing was found.
- Corbotics' clinical data, funding, and pricing were not disclosed in any source found.
- Wosler and Apricity: no 2025-2026 news found; current status unknown.
- Price lists for any commercial system were not found (see Q4).

---

## Key Question 2: What has the academic literature shown about autonomous scanning success rates, force control, patient safety, and generalization?

### Takeaway
The best 2024-2026 results are organ-specific proof-of-concept studies on volunteers: >90% stage success for carotid (UltraBot, 41 unseen subjects), 95.2% completion for thyroid (21 patients), and ARTHUR's 85.5% joint-level success in 30 RA patients. All are superficial, non-moving, non-rib-shielded targets; robots are 2-3x slower than humans; cohorts are small, young, and narrow in BMI; and even the strongest paper calls itself a "proof of concept."

### Cited Findings

**Reviews and their framing**

- Jiang, Salcudean & Navab, *Medical Image Analysis* 2023 (arXiv 2307.05545): categorizes RUSS as teleoperated vs autonomous; states "teleoperated RUSS is easier to be certified for clinical use" because experts retain diagnostic decisions and trajectory; deformation-correction approaches are "not yet applicable to clinical practice"; patient-specific CT/MRI-registration methods have "reduced" advantage clinically because they need a prior scan. Long-term goal is "intelligent robotic sonographer colleagues," not replacements. — [arXiv 2307.05545 (HTML)](https://arxiv.org/html/2307.05545v2); [abstract](https://arxiv.org/abs/2307.05545)
- Same review, teleoperation clinical results: abdominal 92% success on 18 patients (89% strongly willing to repeat); aortic patient acceptability 84±18%; cardiac valve leak/stenosis detection 86% (61/71); obstetric biometrics correct in 93.1%; one abdominal tele-exam took 27±7 min, ~50% longer than conventional. — [arXiv 2307.05545 (HTML)](https://arxiv.org/html/2307.05545v2)
- Bi, Jiang, Duelmer, Huang, Navab (2024, accepted *Annual Review of Control, Robotics, and Autonomous Systems*): open problems are "scarcity of medical data," need for "deeper understanding of the physical aspects," and "effective data representation." — [arXiv 2401.02376](https://arxiv.org/abs/2401.02376)
- IEEE Access 2025 survey (>60 publications, 2022-2025): cobots with 6-DOF F/T sensors and RGB-D cameras now standard; gaps: "surface-parallel force and torque components are often ignored in control models, limiting the accuracy of probe orientation and tissue coupling," and "real-time ultrasound image feedback is rarely used for path optimization." — [IEEE Access survey](https://ieeexplore.ieee.org/document/11016698/)
- Springer 2026 narrative review (RAUS 2021-early 2026, perception/planning/control): "the dynamic and complex nature of the human physiological environment severely hinders the transition of RAUS from automation to full autonomy." — [J Robotic Surgery 2026](https://link.springer.com/article/10.1007/s11701-026-03509-z) (paywalled; from search abstract)
- MDPI Sensors 2026 review: "autonomy in motion-planning and execution does not necessarily imply clinically acceptable diagnostic autonomy, which further requires validated quality metrics and clinically aligned endpoints"; bottlenecks are "safety-verifiable autonomy and failure recovery, motion compensation under deformation, and the lack of standardized, clinically meaningful US image quality metrics." — [Sensors 26(7):2081, 2026](https://www.mdpi.com/1424-8220/26/7/2081) (403 on fetch; from search abstract)
- 2023 *Neurocomputing* review: "Currently, RMUIS is not a complete replacement for the sonographer" and robot-guided interventions "are not yet widely used in clinical practice." — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S092523122300913X)
- A 2026 comprehensive review (PubMed) describes "a paradigm shift toward fully autonomous systems" but says "critical regulatory and ethical frameworks are still needed before clinical translation." — [PubMed 42638373](https://pubmed.ncbi.nlm.nih.gov/42638373/) (abstract only via search)

**Flagship autonomous results**

- **UltraBot carotid** (Jiang, Zhao, Yang et al.; Tsinghua + PLA General Hospital; *Nature Communications*, 23 Aug 2025): fully imitation-learning-based on 247,000 expert-demonstration samples; 7-DOF Franka Panda; 122 volunteers (81 train/val, 41 unseen test, BMI 16.5-30.8, 7 subjects >60 yr); scanning success >90.2% at every stage, mean stage success 95.8% **with up to three trials per participant**; CIMT reproducibility Spearman 5.5x better than sonographers, CoV 2.4x lower; measurement time cut ~14x but total scan+measure time "did not differ significantly, and the robot was slightly slower overall"; comfort split 8 preferred robot / 7 preferred human; force via variable impedance control using Franka joint-torque estimates, kept in a "comfortable range" (no numeric values in text); failures relegated to Supplementary Fig. 1; authors call it a "proof of concept" and note training data from only 81 individuals. Generalization tested across a second ultrasound machine (Hisky EQTouch L15-4 vs GE Vivid E7 9L). — [PMC12375115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12375115/); [Tsinghua announcement](https://www.tsinghua.edu.cn/info/1175/121057.htm)
- UltraBot authors' own critique of prior art: rule-based methods and simulation-trained RL "demonstrate limited generalizability and fail to complete real-world clinical workflows." — [PMC12375115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12375115/)
- **FARUS thyroid** (Su, Liu et al.; SCUT / Peng Cheng Lab / Nanfang Hospital / Carleton; *Nature Communications* 11 May 2024): UR3 arm + Robotiq FT300-S force sensor + Azure Kinect + SonoStar C5; 89 participants robotically scanned (70 volunteers aged 20-30 for image quality; 19 patients mean age 53 for diagnosis); **target contact force 2.0-4.0 N, hard stop at 4.5 N**; scan time **213.0±85.3 s per lobe vs 67.2±27.6 s for doctors** (3x slower; authors attribute to conservative speed for safety); doctors found nodules in 17/19 patients, FARUS in 13/19, missing 8 nodules (small/isoechoic) and 4 possible false positives; scan aborts if patient moves >2 cm laterally in 1 s or >5 cm anteroposteriorly; participants scanned seated (doctors scan supine); "some participants expressed anxiety... most felt that robots cannot replace doctors." — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)
- **Thyroid pilot prospective study** (Zhou et al., *J Med Ultrasonics*, 2026; NWPU-affiliated): 21 consecutive participants, randomized order robot vs operator; completion without human intervention **20/21 (95.2%)**; participant-level nodule detection 8/9 (88.9%); coverage left lobe 100%, right 95%, isthmus 80%; comfort median Likert 3 (IQR 3-4); authors: "acceptable screening performance in a controlled clinical setting, supporting further validation in larger and more diverse populations." — [Springer](https://link.springer.com/article/10.1007/s10396-026-01667-z); [NWPU record](https://pure.nwpu.edu.cn/en/publications/feasibility-and-preliminary-validation-of-an-autonomous-robotic-u/)
- **Lightweight liver robot** (Li ... Liao, Ning; arXiv Oct 2025): 588 g, 6-DOF cable-driven robot mounted *on* the abdomen (claimed more robust to patient motion than an arm), AI agent with memory attention to find structures not in current view; tested on patients incl. two in Xining (2,261 m altitude) and in "wilderness" settings; abstract gives no n, success rate, or force data. — [arXiv 2510.08106](https://arxiv.org/abs/2510.08106)
- **UltraDP** carotid diffusion-policy: secondary summary claims 95% success in transverse scanning on unseen subjects (not verified against paper). — [arXiv 2509.13832](https://arxiv.org/pdf/2509.13832v2); [Emergent Mind](https://www.emergentmind.com/topics/ultradp)
- **RAG-RUSS** (2026): retrieval-augmented, "interpretable framework capable of performing a full carotid examination in accordance with the clinical workflow." — [arXiv 2603.01153](https://arxiv.org/pdf/2603.01153)
- **Cardiac autonomous scanning** (Frontiers Robotics & AI, May 2024): human posture recognition + image servo; authors note "few existing studies have combined autonomous path planning with scanning pose compensation." — [Frontiers](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1383732/full)

**Foundation-model / VLA / LLM work (2024-2026), all lab stage**

- **ForceU-VLA** (Wu et al., arXiv 15 Aug 2026): force-aware vision-language-action model; dataset of 450 expert trajectories, ~100,000 synchronized frames, 2 organs, 5 views; claims improved "contact stability and probe pressure regulation"; no success rates on abstract page; code on GitHub. — [arXiv 2608.15009](https://arxiv.org/abs/2608.15009)
- **US-VLA** (arXiv Aug 2026): VLA for embodied abdominal scanning. — [arXiv 2608.16074](https://arxiv.org/pdf/2608.16074)
- **SAMe** semantic anatomy mapping engine (arXiv Apr 2026). — [arXiv 2604.25646](https://arxiv.org/pdf/2604.25646)
- **USPilot** (arXiv Feb 2025, IEEE RA-L 2025): LLM-enhanced graph planner over robot APIs; task-planning accuracy ~60-79% on public datasets; one physical demonstration. — [arXiv 2502.12498](https://arxiv.org/abs/2502.12498); [IEEE](https://ieeexplore.ieee.org/document/11123690/)
- **Embodied-intelligence ultrasound** (arXiv May 2024, MICCAI 2024): LLM + hand-built ultrasound operation knowledge database to follow verbal commands; reviewer noted it "needs large knowledge datasets built by physicians and roboticists." — [arXiv 2405.00461](https://arxiv.org/abs/2405.00461); [MICCAI 2024](https://papers.miccai.org/miccai-2024/799-Paper0242.html)
- **Guideline-to-action agent** (arXiv Mar 2026): LLM agent reads scanning guidelines via RAG, calls tools, RL-fine-tuned for tool selection; claims generalization to unseen guidelines. — [arXiv 2603.14393](https://arxiv.org/html/2603.14393v1)
- "UltrasoundGPT" is described in a 2023 LLM-in-medicine survey as prompt-engineered dynamic scanning strategy. — [arXiv 2311.05112](https://arxiv.org/pdf/2311.05112)
- **SonoGym** (arXiv Jul 2025): high-performance simulation for RL training of robotic-ultrasound surgical tasks. — [arXiv 2507.01152](https://arxiv.org/pdf/2507.01152)

### Inferences
- Reported "success" is a stage-completion or coverage metric under retries, not diagnostic accuracy; the thyroid studies show the diagnostic gap directly (FARUS missed 8 nodules; the 2026 pilot had only 9 nodule-positive patients).
- Every strong result is on a superficial, immobile, un-shadowed target (carotid, thyroid, hand joints). There is no published autonomous result on a full abdominal, cardiac, or obstetric protocol with patient-level diagnostic endpoints.
- Robots are consistently 1.5-3x slower than humans in the published comparisons (thyroid 3x, tele-abdominal +50%, UltraBot "slightly slower"), which undercuts the throughput argument (Q4).
- The 2026 VLA/LLM papers are at the "we built a dataset and an architecture" stage, with hundreds (not tens of thousands) of trajectories and no clinical endpoints; their abstracts do not report success rates.

### Gaps
- UltraBot's numeric force values and failure-mode descriptions are in supplementary material not accessed.
- No independent replication of any autonomous system by a group other than its developers was found.
- No study comparing an autonomous system against a *novice with AI guidance* (the realistic alternative) was found.
- The 2026 Springer and MDPI reviews were paywalled/403; findings are from abstracts via search summaries.

---

## Key Question 3: What are the hard technical problems blocking autonomous diagnostic ultrasound?

### Takeaway
The literature converges on a short list: regulating contact force on deformable tissue (2-20 N window, with image quality and comfort pulling in opposite directions), motion and breathing, limited acoustic windows (ribs, bowel gas), probe-orientation subtleties that confidence-map optimizers get wrong, absence of a clinically validated image-quality objective, and the fact that failure recovery and safety verification for an autonomous device touching a patient have no established certification path.

### Cited Findings

**Contact force on deformable tissue**
- Acceptable contact force is "less than approximately 20 N" depending on tissue (citing Tsumura 2021); forces "less than 1.2 N" generally indicate incomplete skin contact (Dhyani 2017); "it is challenging for human operators to maintain a constant force"; passive spring limiters cap at ~10 N or 21.98±0.96 N but "cannot precisely and dynamically control the contact force"; admittance control suits soft tissue, impedance control stiff tissue. — [Jiang et al. 2023 review](https://arxiv.org/html/2307.05545v2)
- FARUS used 2.0-4.0 N target with 4.5 N stop; image entropy stabilized above ~2 N; force fluctuated near thyroid poles due to cartilage; assumed tissue stiffness 125-500 N/m. — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)
- A passive spring-loaded ball clutch safety joint gave a measured force limit of 17-24 N at neutral posture, mean 22.10±1.76 N at the probe. — [PMC7115904](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7115904/)
- A KUKA LBR iiwa system targeted a 5 N contact force and stopped forward motion when the maximum was exceeded. — [Jiang et al. 2023 review](https://arxiv.org/html/2307.05545v2)
- Commercial F/T sensors are expensive enough that a 2025 group designed a 3D-printed sensor to make robotic US "accessible." — [PMC11769168](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769168/)
- 2025 survey: surface-parallel (shear) force and torque components are "often ignored in control models." — [IEEE Access 2025](https://ieeexplore.ieee.org/document/11016698/)
- ForceU-VLA motivation: prior methods have "loosely coupled modeling between force and ultrasound modalities." — [arXiv 2608.15009](https://arxiv.org/abs/2608.15009)

**Patient motion and breathing**
- Free-hand style motion compensation is "extremely difficult"; one robotic approach achieved 1.9±0.3 mm arterial reconstruction error in non-static scenes; early systems handled only rigid motion, later ones articulated joints, not described as solved. — [Jiang et al. 2023 review](https://arxiv.org/html/2307.05545v2)
- FARUS simply aborts on >2 cm lateral motion in 1 s. — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)
- The liver robot's body-mounted design is explicitly a workaround for motion robustness. — [arXiv 2510.08106](https://arxiv.org/abs/2510.08106)
- 2026 Sensors review lists "motion compensation under deformation" as a deployment bottleneck. — [Sensors 2026](https://www.mdpi.com/1424-8220/26/7/2081)

**Ribs / limited acoustic windows**
- Intercostal imaging is hard due to "a lack of effective scan path generation within the constrained acoustic window"; TUM's 2025 tactile-mapping approach (palpate ribs, build point cloud, add tilt-angle adjustment) was validated on **four phantoms only** (waypoint error 3.41 mm MNND; sub-rib reconstruction 0.69-2.2 mm vs CT); no in-vivo test. — [arXiv 2507.20282, IROS 2025](https://arxiv.org/abs/2507.20282)
- Subcostal organs are framed as a "limited acoustic windows" problem. — [Jiang et al. 2023 review](https://arxiv.org/html/2307.05545v2)
- The only commercial system clearing for cardiac is Corbotics (breakthrough designation only); MELODY is explicitly *not* cleared for echo. — [Monsky 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513344/)

**Probe orientation (tilt, rocking, fanning, heel-toe)**
- Orthogonal-to-surface is the usual target but "the probe may need to be tilted from the orthogonal direction"; confidence-map-optimal images "may not be the best images expected by clinicians"; a breast framework had normal-direction errors of 12.6° out-of-plane and 4.3° in-plane; force-based orientation estimation is unreliable on soft tissue. — [Jiang et al. 2023 review](https://arxiv.org/html/2307.05545v2)
- 2025 survey: "real-time ultrasound image feedback is rarely used for path optimization." — [IEEE Access 2025](https://ieeexplore.ieee.org/document/11016698/)

**Acoustic coupling and setup**
- MELODY requires a trained assistant on site to prepare the patient and position the robot frame. — [FDA K161354](https://www.accessdata.fda.gov/cdrh_docs/pdf16/K161354.pdf)
- FARUS scanned seated while clinicians scan supine, affecting measurements. — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)

**No validated objective / "language of sonography"**
- The "language of sonography," i.e., modeling expert reasoning and action, is framed as a research direction whose "side result could be as valuable as progress in robotic scanning itself." — [arXiv 2307.05545](https://arxiv.org/abs/2307.05545)
- Lack of "standardized, clinically meaningful US image quality metrics." — [Sensors 2026](https://www.mdpi.com/1424-8220/26/7/2081)
- Data scarcity is the first listed open problem in Navab group's ML review. — [arXiv 2401.02376](https://arxiv.org/abs/2401.02376)

**Safety certification and failure recovery**
- "Safety-verifiable autonomy and failure recovery" is a named deployment bottleneck. — [Sensors 2026](https://www.mdpi.com/1424-8220/26/7/2081)
- Teleoperation "is easier to be certified" because a human retains trajectory and diagnostic control. — [Jiang et al. 2023 review](https://arxiv.org/html/2307.05545v2)
- Teleoperation barriers (US): no CPT codes for remote telerobotic scanning; sonographer licensure required in NH, NM, ND, OR; credentialing of ancillary staff and liability allocation unresolved; FDA cybersecurity requirements; haptics "not yet widely built into commercial systems." Latency must be ≤250 ms with <3% packet loss (400 ms perceivable). — [Monsky 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513344/)
- ROPCA's regulatory path was shortened because the KUKA LBR Med was pre-certified for medical integration. — [Today's Medical Developments](https://www.todaysmedicaldevelopments.com/article/rheumatoid-arthritis-ultrasound-robot-kuka-medtech-arthur-ropca-aps)

**Generalization across body habitus**
- UltraBot tested BMI 16.5-30.8 only (no obese class II/III) and only 7 subjects over 60; training set 81 people. — [PMC12375115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12375115/)
- FARUS: "most volunteers were young college students," "recruitment bias," most nodules low-risk. — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)
- Thyroid 2026 pilot: 21 participants, "controlled clinical setting." — [Springer](https://link.springer.com/article/10.1007/s10396-026-01667-z)

**Patient acceptance**
- FARUS: "some participants expressed anxiety about robotic scanning, and most felt that robots cannot replace doctors." — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)
- UltraBot comfort: 8 preferred robot, 7 preferred human of 21. — [PMC12375115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12375115/)

### Inferences
- The force problem is bounded (roughly 2-20 N) and arguably "solved enough" for superficial targets with a compliant cobot; what is not solved is coupling force with image-driven orientation decisions and shear/torque, which is exactly what skilled heel-toe/rocking does.
- Ribs and breathing are the discriminator between "demo" and "clinic": every deployed or near-deployed autonomous system avoids them (thyroid, carotid, hand), and the one rib-aware paper is phantom-only.
- The absence of a clinically validated image-quality objective means learning-based systems are optimizing proxies (confidence maps, entropy, imitation of a few dozen experts); the UltraBot authors' own call for a "public offline validation tool" signals this.
- Certification for autonomy is a first-of-kind problem; ROPCA's route (pre-certified cobot + narrow indication + human-reviewed AI output) is the template others will copy, and it implies narrow indications, not general scanners.

### Gaps
- No source gave a regulatory (IEC/FDA) numeric force limit for robotic US; all figures are design choices in prototypes.
- No quantitative data on autonomous performance in obese patients (BMI >35) or on breathing-gated abdominal scanning in vivo.
- Room footprint: no source quantified floor space or ceiling-mount requirements for arm-based systems.

---

## Key Question 4: Does a robot make economic sense vs training humans or vs AI guidance on a handheld?

### Takeaway
The only peer-reviewed economic study (rural Saskatchewan, 2020 CAD) found telerobotic ultrasound saves money only versus flying patients out, and is roughly break-even with an itinerant sonographer; published robots are slower per exam than humans; capital costs are opaque ($100k-$500k vendor-forecast range); and the competing approach, AI guidance on a handheld for nurses, has been FDA-authorized since 2020 at near-zero marginal hardware cost. The economic case today is access (rural/remote, sonographer vacancy 12-24%), not throughput or labor replacement.

### Cited Findings

**Published cost analysis**
- Cost-minimization study, rural/remote Saskatchewan (2020 CAD, payer perspective): average cost per exam **$342 telerobotic alone, $323 telerobotic + itinerant sonographer, $368 itinerant sonographer alone, $478 patient travel**. Itinerant sonographer alone was cheapest for the smallest communities (~535-2,075 people). Societal-perspective costs were higher for robot-only. — [PubMed 35906950](https://pubmed.ncbi.nlm.nih.gov/35906950); [USask full text](https://research-groups.usask.ca/remote-presence/economic-evaluation-of-telerobotic-ultrasound-technology-to-remotely-provide-ultrasound-services-in-rural-and-remote-communities.pdf)
- The Dopl-affiliated review states only that "initial and related costs must be appropriate," cites no system prices, and cites a 2002 estimate of $25,000-$60,000/month lost revenue per injured sonographer and 65-91% MSK pain prevalence among sonographers as part of the case. No CPT codes exist for remote telerobotic scanning. — [Monsky 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513344/)

**Capital cost**
- Vendor market-research estimate: average robotic ultrasound system cost $100,000-$500,000 (2023), "a barrier for smaller healthcare facilities." Not peer-reviewed. — [Persistence Market Research](https://www.persistencemarketresearch.com/market-research/robotic-ultrasound-system-market.asp)
- Research systems use UR3 (FARUS), Franka Panda (UltraBot), KUKA LBR Med (ARTHUR), KUKA iiwa, Kinova (Wosler); commercial F/T sensors are described as "expensive." — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/); [PMC12375115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12375115/); [PMC11769168](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769168/)

**Throughput**
- Thyroid: robot 213 s/lobe vs human 67 s/lobe. — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)
- Tele-abdominal: 27±7 min, ~50% longer than conventional. — [Jiang 2023 review](https://arxiv.org/html/2307.05545v2)
- UltraBot: measurement 14x faster but total exam time not significantly different, robot slightly slower. — [PMC12375115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12375115/)
- ARTHUR: ~15 min per exam, framed as a "productivity tool" that frees rheumatologist time, scanning while the clinician does other work. — [ITU AI for Good](https://aiforgood.itu.int/?p=17119)

**Human labor side**
- US diagnostic medical sonographer median wage $96,590 (BLS OEWS May 2025, via third-party reproduction; 10th pct $67,820, 90th $129,370); BLS projects +13% employment 2024-2034, ~5,800 openings/yr. — [TradeCareerPath (reproducing BLS)](https://tradecareerpath.com/trade-school/utah/washington/best-sonography-and-ultrasound-programs/)
- US ultrasound exam volume rose 55.1% (38.6M → 59.8M) 2011-2021 while sonographers rose 43.6% (54,760 → 78,640); open positions rose 36.3% (18,462 → 25,162). — [J Diagn Med Sonography 2024, "Sound the Alarm"](https://pubmed.ncbi.nlm.nih.gov/38534218/)
- ASRT 2025 survey: US sonographer vacancy rate 12.4% (down from 16.7% in 2023, above 6.9% in 2021). — [AuntMinnie MinnieCast](https://www.auntminnie.com/clinical-news/ultrasound/sonographer/video/15831868/ultrasound-minniecast-episode-14-weathering-the-sonographer-shortage)
- UK: Society of Radiographers 2025 Ultrasound Census (published March 2026) found sonography vacancy rate 24.2%. — [SoR](https://www.sor.org/news/ultrasound/sonography-vacancy-rates-have-increased-dramatical)

**The AI-guided-handheld alternative**
- Caption Guidance: FDA De Novo authorization Feb 2020, "first medical software authorized by the FDA that provides real-time AI guidance for medical imaging acquisition"; indicated for 2D TTE in adults; pivotal trial of 240 patients where registered nurses with no ultrasound experience acquired diagnostic-quality images, judged by a panel of five expert echocardiographers. — [Radiology Business](https://radiologybusiness.com/topics/medical-imaging/ultrasound-imaging/fda-heart-ultrasound-imaging-clearance-ai); [DAIC](https://www.dicardiology.com/node/81224); [AuntMinnie](https://www.auntminnie.com/clinical-news/ultrasound/article/15627835/ai-guided-echo-helps-novice-nurses-perform-ultrasound)
- Monsky et al. list Verisound AI, Lumify and EchoNous as AI-assisted point-of-care (non-robotic) alternatives. — [Monsky 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513344/)
- ROPCA's DIANA AI can analyze manually acquired images without the robot. — [ITU AI for Good](https://aiforgood.itu.int/?p=17119)

### Inferences
- With a ~$100k/yr sonographer and a $100k-$500k robot that is slower per exam and still needs an on-site assistant (MELODY) or a remote sonographer (all teleoperated systems), the robot does not reduce labor per exam; it relocates labor. The Saskatchewan data show the saving comes from avoided patient travel, not avoided sonographer time.
- The strongest near-term economic case is a "hub-and-spoke" model where one remote expert serves several rural sites, or ARTHUR's model where a fixed, bounded exam runs unattended while the clinician does something else.
- For most in-hospital scanning, AI guidance on a handheld (nurse + Caption-style software) attacks the same shortage at roughly the cost of a tablet and already has a 2020 regulatory precedent; a robot has to beat that, not just beat a sonographer.
- Absence of CPT codes means a US hospital cannot currently bill a telerobotic exam differently from a standard one, so capital must be recovered from access gains or sonographer injury reduction rather than revenue.

### Gaps
- No peer-reviewed cost-effectiveness study of a robot vs a sonographer in a hospital (non-rural) setting was found.
- No published list prices for MELODY, MGIUS-R3, ARTHUR, CODI, or Dopl were found.
- No data on service/maintenance contracts for robotic US (robotic-surgery analogs cite $40k-$150k/yr but are not ultrasound). — [PMC12417245](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12417245/)
- No head-to-head study of autonomous robot vs AI-guided novice was found.

---

## Key Question 5: What do experts say about the timeline to practical autonomous diagnostic ultrasound?

### Takeaway
No credible source gives a date for autonomous diagnostic ultrasound replacing sonographers; the field's leading academic group (Navab/Jiang, TUM) frames the goal as "robotic sonographer colleagues," commercial players frame their products as "extending clinicians' reach," and the nearest regulatory milestones are a 2027 FDA submission for a *teleoperated* system (Dopl) and a breakthrough-designated *cardiac* autonomous system (Corbotics) with no disclosed data or timeline.

### Cited Findings
- TUM group (Jiang, Salcudean, Navab 2023): long-term goal is "intelligent robotic sonographer colleagues" that collaborate with human sonographers; RUSS "holds the potential to provide medical interventions for populations suffering from the shortage of experienced sonographers." — [arXiv 2307.05545](https://arxiv.org/abs/2307.05545)
- UltraBot authors (Tsinghua, 2025) call their Nature Communications result a "proof of concept" for clinical use and list multimodal perception, use of report data, and a public offline validation tool as next steps "since large-population validation is costly." — [PMC12375115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12375115/)
- FARUS authors (2024): "clinical studies are needed before the system can serve as a screening tool for malignancy." — [PMC11519952](https://pmc.ncbi.nlm.nih.gov/articles/PMC11519952/)
- Springer 2026 review: the physiological environment "severely hinders the transition... from automation to full autonomy." — [J Robotic Surgery 2026](https://link.springer.com/article/10.1007/s11701-026-03509-z)
- 2026 PubMed review: "paradigm shift toward fully autonomous systems" but "critical regulatory and ethical frameworks are still needed before clinical translation." — [PubMed 42638373](https://pubmed.ncbi.nlm.nih.gov/42638373/)
- 2023 review: RMUIS "is not a complete replacement for the sonographer." — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S092523122300913X)
- Dopl (telerobotic, Dopl-affiliated review): "It is probable that telerobotic systems will become increasingly established, cost-effective, and widely adopted"; AI to guide the arm is "a key next step toward autonomous echocardiography"; FDA submission planned 2027. — [Monsky 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12513344/); [MassDevice 2026](https://www.massdevice.com/dopl-remote-ultrasound-robot-developer-seed-round/)
- Us2.ai president on Corbotics partnership: goal is to "extend clinicians' reach rather than replace them"; Corbotics CEO: expand automation "while keeping expert review." — [The AI Insider, Aug 2026](https://theaiinsider.tech/2026/08/31/corbotics-and-us2-ai-partner-to-combine-ai-and-robotics-for-automated-cardiac-ultrasound-tech/)
- Cobionix (2023): full autonomy is "the primary goal for the future of CODI," teleoperation is what works now. — [Canadian Healthcare Technology](https://www.canhealth.com/2023/09/20/company-developing-robot-that-can-do-ultrasounds/)
- ROPCA CEO on FDA clearance (Sept 2026): "ready to build the U.S. clinical and commercial partnerships that take this new category forward." — [MassDevice](https://www.massdevice.com/tag/ropca/)
- GE HealthCare–Nvidia: autonomous ultrasound is framed as testing and simulation-training "before deploying in the physical world," no product timeline. — [Radiology Business](https://radiologybusiness.com/topics/artificial-intelligence/using-robotics-automate-x-ray-ultrasound-workflows-goal-new-ge-healthcare-nvidia-partnership)
- A search for any expert-stated replacement timeline returned none; sources describe "augmentation and teleoperation as the realistic near-term path." — [search summary citing 2023-2025 reviews](https://pubmed.ncbi.nlm.nih.gov/42638373/)

### Inferences
- Reading the regulatory pipeline: by ~2028-2030 it is plausible to see (a) more teleoperated clearances (Dopl 2027 submission), (b) ARTHUR-style narrow autonomous devices for other rigid/superficial targets (thyroid, carotid are the obvious next ones given the 2024-2026 data), and (c) possibly a cardiac autonomous acquisition device (Corbotics) *with* clinician review of images. A general-purpose autonomous abdominal/OB scanner that replaces a sonographer is not on any disclosed roadmap.
- The consistent "colleague / extend reach / keep expert review" language from both academics and vendors is partly regulatory positioning (human-in-the-loop is easier to clear) and partly an honest description of what the technology does.
- For the "just have a robot do it" question: realistic now only for teleoperation with a remote human, or for narrow fixed-protocol superficial exams; within 5 years, likely expands to a few more narrow protocols with expert review, not to general diagnostic scanning.

### Gaps
- No named expert gave a year-based forecast; the above 5-year view is inference from pipeline disclosures, not a cited opinion.
- Corbotics' expected clearance date and clinical trial status are undisclosed.
- No survey of sonographers' or radiologists' attitudes toward autonomous robots (as opposed to AI software) was found.

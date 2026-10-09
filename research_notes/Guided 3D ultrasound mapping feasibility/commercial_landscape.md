# Commercial Landscape: AI Ultrasound Operator Guidance and Consumer/Handheld 3D Ultrasound (as of October 2026)

Scope note: this covers (a) products that guide a novice operator in real time on probe movement, and (b) products that build 3D volumes from a handheld sweep or freehand scan, plus anything combining the two. Facts are verified against FDA database records, company releases, and trade press where possible; marketing claims are labelled as such. Items older than 2025 are dated explicitly. Tool-call budget was exceeded deliberately because of the breadth of the assignment (~60 calls).

---

## Key Question 1: Product-by-product landscape of real-time AI operator guidance (what it does, exams, FDA status, year, pricing, how guidance is delivered)

### Takeaway
As of October 2026 there are only five FDA-authorized real-time probe-guidance products for novices, all cardiac (Caption Guidance/GE, UltraSight, DESKi HeartFocus) or single-protocol (ThinkSono DVT, Pulsenmore home prenatal); every one is cardiac or OB/vascular, delivers guidance as on-screen directional prompts plus a quality meter, and none produces 3D. The big OEMs (Philips, Mindray, Canon, Siemens) sell automation and auto-measurement rather than probe-steering guidance; Samsung and Exo advertise "exam guidance"/"SweepAI" without a cleared probe-guidance indication.

### Cited Findings

**Regulatory category.** FDA created the product code QJU / 21 CFR 892.2100 ("Image acquisition and/or optimization guided by artificial intelligence") via the Caption Guidance De Novo; it is the code under which all subsequent probe-guidance products (UltraSight, HeartFocus) were cleared. — [FDA De Novo DEN190040](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID=DEN190040); [FDA K251416](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251416); [FDA K242807](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K242807)

**GE HealthCare Caption Guidance / Caption AI (ex-Caption Health, ex-Bay Labs)**
- De Novo DEN190040 granted 02/07/2020 to Bay Labs, Inc., product code QJU, regulation 892.2100. — [FDA De Novo database](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID=DEN190040)
- Follow-on 510(k) K200755 "Caption Guidance" cleared 04/16/2020 (Caption Health, QJU). — [FDA 510(k) K200755](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K200755)
- Exams: cardiac only (10 standard TTE views) with AutoEF (LVEF from PLAX, AP2, AP4). — [GE Vscan Air Caption AI page via search](https://www.gehealthcare.com/en-us/products/ultrasound/handheld-ultrasound/vscan-air-caption-ai)
- Guidance delivery: "real-time visual guidance that prompts users on probe movements, plus a quality meter," AutoCapture and Save Best Clip. — [GE press release, April 3, 2024](https://www.gehealthcare.com/en-us/about/newsroom/press-releases/ge-healthcare-introduces-caption-ai-on-vscan-air-sl-wireless-handheld-ultrasound-system-to-help-more-clinicians-capture-diagnostic-quality-cardiac-images)
- Platforms: Venue family (optional add-on, announced October 2023) and Vscan Air SL handheld (debuted ACC April 6-8, 2024); marketed under GE's "Verisound AI" brand. — [GE Venue release](https://www.gehealthcare.com/en-us/about/newsroom/press-releases/ge-healthcare-launches-enhanced-venue-family-point-of-care-ultrasound-systems-featuring-ai-driven-caption-guidance); [GE Verisound AI](https://www.gehealthcare.com/products/ultrasound/ultrasound-digital-solutions/verisound-ai)
- Pricing: not public; a third-party overview says Caption AI is sold on a subscription model. — [Physician AI Tools profile](https://physicianaitools.com/companies/caption-health-now-part-of-ge-healthcare/)
- The Vscan Air itself has separate 510(k)s: K202035 (Nov 20, 2020), K231301 (Aug 15, 2023), K250087 (May 1, 2025, adds Auto Bladder Volume with 92.24% auto-caliper success). — [Innolitics K250087](https://510k.innolitics.com/device/K250087); [Innolitics K231301](https://510k.innolitics.com/device/K231301)

**UltraSight (Israel) – "UltraSight AI Guidance" / "Echosystem" / "Echo Stewardship Program"**
- K223347 "UltraSight AI Guidance" received Nov 1, 2022, cleared July 24, 2023 (applicant Ultrasight Inc., Rehovot). — [FDA K223347](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K223347)
- K251416 "UltraSight Guidance" received May 7, 2025, cleared Dec 17, 2025, QJU, 892.2100 (third-party aggregator reports a PCCP authorization). — [FDA K251416](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251416); [510kdatabase.net](https://www.510kdatabase.net/k251416/)
- K252235 "PVAD IQ Software" cleared Dec 18, 2025 (image-processing code, not guidance). — [FDA K252235](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K252235)
- Indication: 2D TTE in adults, acquisition of the 10 standard views; initially compatible only with Philips Lumify; a neural network predicts probe pose relative to the heart from the video stream and guides the user. — [UltraSight release, July 27, 2023](https://ultrasight.com/fda-grants-clearance-for-ultrasights-ai-powered-cardiac-ultrasound-technology/)
- January 2026: expanded clearance covering handheld, laptop and cart-based systems, aimed at "trained non-sonographer clinicians including APPs" doing FoCUS exams. — [Diagnostic Imaging, Jan 6, 2026](https://www.diagnosticimaging.com/view/fda-expanded-clearance-ultrasight-cardiac-ultrasound-echo-stewardship-program)
- Joined Butterfly Garden June 2024 "subject to regulatory approvals"; as of the current marketplace page the UltraSight app is still listed "Coming soon." — [PRNewswire, June 2024](https://www.prnewswire.com/news-releases/ultrasight-joins-butterfly-garden-to-expand-ai-real-time-guidance-across-point-of-care-ultrasound-devices-302184449.html); [Butterfly Garden page](https://www.butterflynetwork.com/ai-marketplace)
- Evidence: 2022 multicenter study, 9 residents/nurses, 240 patients, LV function assessable 99.6% of the time (company-cited). — [Cardiovascular Business](https://cardiovascularbusiness.com/topics/artificial-intelligence/fda-clears-expanded-use-ai-helps-novice-users-perform-echo-exams)
- Sept 23, 2026: $24M Series B2 led by Alive HealthTech Growth Fund with Deep Insight, Star51, Connecticut Innovations, eHealth Ventures, Mayo Clinic Ventures, NYU, Iron Nation; total raised $42M; "more than 10 commercial sites." — [HIT Consultant](https://hitconsultant.net/2026/09/23/ultrasight-secures-24m-series-b2-ai-cardiac-ultrasound-echosystem-jama-cardiology/); [Calcalist](https://www.calcalistech.com/ctechnews/article/by947zxcgl)
- Pricing: not public. Trials: ENABLE-HCM (NCT07155434, completion Feb 24, 2026); Jefferson Health RV/PE pilot (Jan 2026). — [ClinicalTrials.gov](https://clinicaltrials.gov/study/NCT07155434); [Signify, Jan 30, 2026](https://www.signifyresearch.net/insights/product-launches-ai-advances-and-global-partnerships-kick-off-2026/)

**DESKi (Bordeaux, France) – HeartFocus**
- K242807 "HeartFocus V.1.1.1" received Sept 17, 2024, cleared April 4, 2025, QJU; K260780 Special 510(k) cleared June 3, 2026; FDA also approved a Predetermined Change Control Plan. — [FDA K242807](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K242807); [FDA K260780](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K260780); [MassDevice](https://www.massdevice.com/deski-wins-fda-clearance-for-heartfocus-software/)
- Guidance: real-time quality and precision indicators, auto-records clips for 10 cardiac reference views; "live image guidance." — [Diagnostic Imaging](https://www.diagnosticimaging.com/view/fda-clears-emerging-ai-enabled-software-for-cardiac-ultrasound); [Butterfly Garden listing](https://www.butterflynetwork.com/ai-marketplace)
- Pivotal study (JACC: Advances, July 2025): 8 nurses with no US experience, Clarius HD3 phased probe, 240 patients at Lenox Hill (NY) and CHU Bordeaux, Nov 2023–Aug 2024 (NCT05874128); 240/240 (100%) of novice exams adequate for LV size, LV function, RV size, pericardial effusion, identical to expert rate; no unassisted-novice control arm. — [PMC12308015](https://pmc.ncbi.nlm.nih.gov/articles/PMC12308015/)
- Available now on Butterfly Garden (30-day trial) – the only shipping third-party real-time guidance app on Butterfly. — [Butterfly Garden page](https://www.butterflynetwork.com/ai-marketplace)
- May 28, 2026: "HeartFocus Link" extends guidance to any cart-based system for training programs; certification pathway with Inteleos (May 2026). — [BusinessWire](https://www.businesswire.com/news/home/20260528026125/en/HeartFocus-Launches-HeartFocus-Link-Bringing-AI-Guided-Cardiac-Ultrasound-Education-and-Guidance-to-Any-Cart-Based-System); [Signify, May 6, 2026](https://www.signifyresearch.net/insights/partnerships-product-launches-and-ai-innovation-drive-ultrasound-market-momentum/)
- Funding: $6M seed reported (one source wrongly dates FDA clearance to 2023). — [hyper.ai](https://hyper.ai/en/stories/963ff2b5af76fa63154deea206b42e23)

**ThinkSono (UK) – ThinkSono Guidance (DVT)**
- FDA 510(k) announced July 29, 2026; Breakthrough Device designation Feb 2026; runs on a Clarius handheld; app guides probe positioning and recording of venous compression cine-loops which go to a remote clinician dashboard; software does not interpret. — [Endovascular Today](https://evtoday.com/news/fda-clears-thinksonos-ultrasound-AI-guidance-software-to-evaluate-suspected-dvt)
- Evidence: 1,691 patients, 24 sites (157 DVT); US pivotal NCT06652568, 594 patients at 5 sites; adequate image quality 87.1%, sensitivity 92.9%, specificity 97.1%; operator training 60–90 min; median scan 5m24s. — [Endovascular Today](https://evtoday.com/news/fda-clears-thinksonos-ultrasound-AI-guidance-software-to-evaluate-suspected-dvt)
- Also listed as "available" training app on Butterfly Garden (2024 Butterfly training version was explicitly not diagnostic). — [Butterfly Garden page](https://www.butterflynetwork.com/ai-marketplace); [Newswire, April 2024](https://www.newswire.com/news/thinksono-releases-real-time-dvt-ai-training-solution-for-butterfly-22297057)

**Pulsenmore (Israel) – Pulsenmore ES home prenatal ultrasound**
- FDA De Novo marketing authorization announced Nov 3, 2025 (request received by FDA Dec 11, 2024; Class II with special controls; file DEN240074). — [MassDevice](https://www.massdevice.com/pulsenmore-fda-nod-home-prenatal-ultrasound/); [FDA DEN240074 letter PDF](https://www.accessdata.fda.gov/cdrh_docs/pdf24/DEN240074.pdf); [Pulsenmore Nov 2025 newsletter](https://pulsenmore.com/november-2025-newsletter/)
- How it works: cradle attaches to the patient's smartphone; app walks the pregnant user through each scan; clips reviewed remotely by physicians; prescription-only; does not replace in-clinic anatomy scans; >200,000 scans in Israel, Europe, Brazil, Australia; phased US launch early 2026. — [BioSpace press release](https://www.biospace.com/press-releases/pulsenmore-receives-fda-de-novo-marketing-authorization-for-home-use-prenatal-ultrasound-pioneering-a-new-era-of-prenatal-care-in-the-u-s)
- Nasdaq listing January 2026 (PLSM); Pulsenmore FC (home follicular monitoring for IVF) 5-year Clalit agreement ~$4.5M; Ouma Health partnership June 24, 2026. — [Pulsenmore site](https://pulsenmore.com/); [Signify, Jan 30, 2026](https://www.signifyresearch.net/insights/product-launches-ai-advances-and-global-partnerships-kick-off-2026/)
- Pricing: not found.

**Butterfly Network – iQ3, ScanLab, Butterfly Garden, Compass AI**
- iQ3 FDA-cleared January 2024, US launch Feb 13, 2024; "iQ Slice" captures 46 slices across a wide angle with automated beam steering; "iQ Fan" for lung; tools include Auto Bladder Volume, Auto B-Line Counter, NeedleViz. — [BusinessWire, Feb 13, 2024](https://www.businesswire.com/news/home/20240213652085/en/Butterfly-Network-Launches-Next-Generation-Butterfly-iQ3%E2%84%A2-in-the-United-States); [AuntMinnie](https://www.auntminnie.com/clinical-news/ultrasound/article/15664060/butterfly-network-launches-butterfly-iq3)
- Butterfly's own native guidance is limited to ScanLab (iPad-only educational app, "not for diagnostic use," announced ACEP 2023, includes written walkthroughs, animations of probe placement, and a real-time image quality indicator); diagnostic real-time guidance comes only via third-party Garden apps. — [Butterfly ScanLab release](https://www.butterflynetwork.com/press-releases/butterfly-education-scanlab); [Butterfly Garden page](https://www.butterflynetwork.com/ai-marketplace)
- Butterfly Garden (launched Aug 2023) lists 10 apps: 4 available (HeartFocus, MSK VUE, ThinkSono AI, ScanLab) and 6 "coming soon" (BarrelEye, DeepEcho, FAMLI/UNC, iCardio AI, Southwood, UltraSight). Q2 2026: added a needle-guidance AI partner, expects three partner tools to go commercial by end-2026. — [Butterfly Garden page](https://www.butterflynetwork.com/ai-marketplace); [Butterfly Q2 2026 8-K](https://www.sec.gov/Archives/edgar/data/0001804176/000180417626000025/bfly-20260730xexx991.htm)
- Pricing: iQ3 probe $3,899 plus required membership from $299/yr (first-year ~$4,198) per third-party review. — [suresultmed review](https://suresultmed.com/butterfly-iq3-review/); [Butterfly pricing page](https://www.butterflynetwork.com/pricing)
- Financials: Q2 2026 revenue $32.6M (+39%), FY2026 guidance $119–123M; "Home & Community Care" moving from pilot to first commercial implementation 2H 2026 (nurses/novice users scanning in home settings); Butterfly Embedded has 11 chip-licensing partners incl. Midjourney. — [Butterfly Q2 2026 8-K](https://www.sec.gov/Archives/edgar/data/0001804176/000180417626000025/bfly-20260730xexx991.htm); [BFLY Q4 2024 slides](https://s27.q4cdn.com/524696391/files/doc_financials/2024/q4/BFLY-4Q2024-Earnings-Slides-vFINAL-3-7-25.pdf)

**Philips Lumify**
- Reacts tele-ultrasound integration (two-way AV plus live stream for remote supervision) dates to 2018; this is collaboration, not AI guidance. — [ITN](https://www.itnonline.com/content/philips-integrates-reacts-tele-ultrasound-platform-lumify-portable-systems)
- Gates Foundation funded OB AI: $15.4M (2021) + $44.6M (Nov 2023) = $60M; Philips claims Lumify is "the first POCUS device introduced commercially to assist non-expert users by automating image acquisition or image interpretation for a comprehensive set of obstetrics measurements," cutting training "from weeks to hours"; Kenya pilot reported positive. — [MobiHealthNews](https://www.mobihealthnews.com/news/philips-receives-60m-bill-and-melinda-gates-foundation-ai-tech); [ITN](https://www.itnonline.com/content/philips-program-developing-ai-powered-ultrasound-expand-access-maternal-health-receives); [AuntMinnie](https://www.auntminnie.com/clinical-news/ultrasound/article/15638096/philips-receives-additional-funding-boost-from-gates-foundation)
- Lumify 510(k) K252557 cleared Dec 22, 2025 lists ML algorithms incl. lung view quality assessment; whether OB auto-acquisition is included is not stated. — [Innolitics K252557](https://510k.innolitics.com/device/K252557)
- Lumify is the original host platform for UltraSight guidance. — [UltraSight release](https://ultrasight.com/fda-grants-clearance-for-ultrasights-ai-powered-cardiac-ultrasound-technology/)

**Exo (Santa Clara) – Exo Iris**
- Launched Sept 26, 2023 at $3,500; pMUT silicon transducer; "SweepAI" captures images through "a simple wrist movement, minimizing the need for extensive operator training" (sweep-based acquisition, not probe-steering guidance). — [Fierce Biotech](https://www.fiercebiotech.com/medtech/exo-officially-enters-handheld-ultrasound-race-launch-ai-powered-iris-system); [AuntMinnie](https://www.auntminnie.com/clinical-news/ultrasound/pocus/article/15635088/exo-introduces-exo-iris-ultrasound-device)
- FDA-cleared cardiac (LVEF from PLAX/A4C) and lung (B-lines) AI April 23, 2024; pleural effusion and consolidation/atelectasis AI June 18, 2025, bringing "14 FDA-cleared AI indicators." — [Exo release](https://www.exo.inc/article/exo-launches-fda-cleared-ai-on-exo-iris-to-address-heart-failure); [BusinessWire, June 18, 2025](https://www.businesswire.com/news/home/20250618533743/en/Exo-Launches-a-New-Era-in-Disease-Diagnosis-with-the-First-FDA-cleared-Ultrasound-AI-for-Detection-of-Pleural-Effusion-and-ConsolidationAtelectasis)
- Samsung Medison strategic partnership May 27, 2025; Aug 4, 2026 subscription-free standalone Iris option (one-time activation; both tiers keep PACS, AI indicators and updates). — [Exo newsroom](https://www.exo.inc/newsroom); [AuntMinnie, Aug 2026](https://www.auntminnie.com/clinical-news/ultrasound/news/15831624/exo-imaging-exo-expands-iris-handheld-ultrasound-with-subscriptionfree-option)
- No 3D/volumetric imaging claim found for Iris. — [Fierce Biotech](https://www.fiercebiotech.com/medtech/exo-officially-enters-handheld-ultrasound-race-launch-ai-powered-iris-system)

**Clarius Mobile Health (Vancouver)**
- AI clearances: MSK AI (Jan 2023), OB AI fetal biometry (June 25, 2024), Ejection Fraction AI (June 2, 2026, PA/PAL/C3 HD3), Prostate AI (~Sept 2026). None is probe-steering guidance; "T-Mode" labels anatomy live for less-experienced users. — [Diagnostic Imaging OB AI](https://www.diagnosticimaging.com/view/fda-ai-powered-ultrasound-tool-fetal-biometric-measurements); [AuntMinnie EF AI](https://www.auntminnie.com/clinical-news/ultrasound/news/15826589/clarius-mobile-health-clarius-gets-fda-clearance-for-ejection-fraction-ai-tool); [Diagnostic Imaging Prostate AI](https://www.diagnosticimaging.com/view/fda-ai-powered-prostate-volume-measurement-handheld-ultrasound); [clarius.com](https://clarius.com/)
- Clarius is the host hardware for both HeartFocus (pivotal trial) and ThinkSono Guidance (cleared). — [PMC12308015](https://pmc.ncbi.nlm.nih.gov/articles/PMC12308015/); [Endovascular Today](https://evtoday.com/news/fda-clears-thinksonos-ultrasound-AI-guidance-software-to-evaluate-suspected-dvt)
- No 3D/volume sweep feature found on Clarius product pages or press. — [clarius.com](https://clarius.com/)

**EchoNous – Kosmos**
- K193518 (March 2020); K212100 (Aug 2021) states "the new AI-assisted EF Workflow and Trio tool are not yet cleared by the FDA" and relied on COVID enforcement policy; Trio = image-quality grading + guidance + anatomy labeling. — [FDA K212100 PDF](https://www.accessdata.fda.gov/cdrh_docs/pdf21/K212100.pdf); [Diagnostic Imaging](https://www.diagnosticimaging.com/view/echonous-secures-fda-clearance-hand-held-ultrasound-scanner)
- K233826 (Aug 29, 2024) adds Auto EF and "AI FAST" real-time anatomical structure labeling and view identification (cardiac, lung, abdomen); the FDA summary does not mention real-time probe guidance or quality grading. K242321 (Apr 25, 2025) is a general system clearance (Torso-One and Lexsa probes). — [Innolitics K233826](https://fda.innolitics.com/device/K233826); [FDA K242321](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K242321)
- Funding: $7M raised 2023. — [GeekWire](https://www.geekwire.com/2023/echonous-maker-of-an-ai-powered-portable-ultrasound-system-raises-7m/)

**GE SonoLyst / Intelligent Ultrasound**
- GE acquired Intelligent Ultrasound's clinical AI business for ~$51M (announced July 2024, closing Q4 2024); ScanNav Assist powers SonoLyst live (real-time OB image acquisition on Voluson Expert/Signature/Swift) and SonoLyst X/IR; NeedleTrainer and simulation excluded. — [MassDevice](https://www.massdevice.com/ge-healthcare-acquire-ai-intelligent-ultrasound/); [HLTH](https://hlth.com/insights/articles/ge-healthcare-to-acquire-intelligent-ultrasound-s-ai-software-for-51m-2024-07-19)
- ScanNav Anatomy PNB overlays segmented labels for nerve blocks (EU and US). — [GE insights](https://www.gehealthcare.com/en-us/insights/article/ai-guided-ultrasound-from-innovation-to-impact)
- GE/RadNet DeepHealth letter of intent (RSNA 2025) to combine TechLive remote scanning with GE ultrasound. — [Signify RSNA 2025](https://www.signifyresearch.net/insights/from-handheld-to-high-end-ultrasound-product-launched-ai-tools-rsna-2025-highlights/)

**Samsung Medison**
- R20 premium system (RSNA 2025) claims "more than a dozen AI-powered tools for real-time exam guidance, diagnostic assistance, workflow automation, and automated measurements" (no named probe-guidance tool, no clearance detail). — [Samsung Newsroom](https://news.samsung.com/global/samsung-introduces-r20-ultrasound-system-elevating-imaging-performance-and-precision-at-rsna-2025)
- Acquired Sonio (France) May 8, 2024; Sonio Detect is FDA 510(k)-cleared and provides a real-time checklist of exam completeness (views captured/missed) for prenatal exams. — [Samsung Newsroom](https://news.samsung.com/global/samsung-announces-acquisition-of-sonio-to-strengthen-its-leading-position-in-cutting-edge-medical-devices); [Sonio platform](https://www.sonio.ai/platform)
- Samsung–Exo partnership May 2025. — [Exo newsroom](https://www.exo.inc/newsroom)

**Mindray** – TE Air e5M handheld (22 exam types, no subscription, online store) with iTouch+ auto preset detection; Resona A20; no real-time novice probe guidance found. — [Signify RSNA 2025](https://www.signifyresearch.net/insights/from-handheld-to-high-end-ultrasound-product-launched-ai-tools-rsna-2025-highlights/)

**Canon** – Aplio i-series v9.0 (AI 3rd harmonic imaging, SMI Angio, Auto Tune SWE); no novice guidance found. **Siemens** – mentioned only as targeting cardiology; no novice guidance product found. **Fujifilm Sonosite** – PIV Assist (real-time color-coded vessel ID, catheter-to-vein ratio) is the closest thing to procedural guidance among OEMs. — [Signify RSNA 2025](https://www.signifyresearch.net/insights/from-handheld-to-high-end-ultrasound-product-launched-ai-tools-rsna-2025-highlights/)

**ASUS LU800** – K250791 (bench testing only), announced Jan 2026; Signify reports ASUS "is developing real-time AI guidance for non-specialists." — [Innolitics K250791](https://fda.innolitics.com/device/K250791); [ASUS press](https://press.asus.com/news/press-releases/asus-handheld-ultrasound-fda-clearance/); [Signify Jan 2026](https://www.signifyresearch.net/insights/product-launches-ai-advances-and-global-partnerships-kick-off-2026/)

**Sweep-protocol OB AI (guidance by protocol rather than live steering)** – UNC FAMLI blind sweeps: 4,695 volunteers (NC + Zambia), AI gestational age from blind sweeps on Butterfly iQ performed at least as well as sonographer; FAMLI app "coming soon" on Butterfly Garden. Google Research JAMA Netw Open (July 9, 2026): MAE 4.1 days Chicago / 4.3 days Nairobi, noninferior. — [UNC Global Health](https://globalhealth.unc.edu/2023/10/unc-research-validates-ai-powered-gestational-age-calculator-used-on-butterfly-iq-for-global-pregnancy-care/); [JAMA Network Open 2026](https://media.jamanetwork.com/10.1001/jamanetworkopen.2026.22484)

**Independent evidence synthesis** – 2025 narrative review of 9 prospective studies: AI guidance consistently let nonexperts obtain adequate TTE views; adequacy for LV function and effusion "frequently exceeded 90%." — [PMC12621280](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12621280/)

### Inferences
- The cleared guidance market is effectively three cardiac engines (Caption/GE, UltraSight, DESKi) plus two narrow protocols (ThinkSono DVT, Pulsenmore OB); non-cardiac general-purpose probe guidance (abdomen, thyroid, MSK) has no cleared product.
- Guidance UX has converged: directional on-screen prompts + a quality bar + auto-capture; no product uses voice guidance per the sources found.
- Handheld vendors (Butterfly, Clarius) have chosen to host third-party guidance rather than build it; GE is the only OEM owning a cleared guidance engine.
- Pricing for guidance software is almost never public; hardware is $3,500–$4,999 with $299–$1,200/yr subscriptions, and 2026 saw a shift to subscription-free options (Exo, Mindray).

### Gaps
- No K-number was found for Caption Guidance's integration into Venue/Vscan Air SL (likely folded into GE system 510(k)s).
- No public pricing for Caption AI, UltraSight, HeartFocus, ThinkSono or Pulsenmore.
- Samsung R20's "real-time exam guidance" tools are unnamed and their clearance status unknown.
- Whether EchoNous's Trio guidance was ever formally cleared could not be confirmed from the FDA summaries read.
- Which Lumify 510(k) covers the OB auto-acquisition feature, and whether it has commercially launched in the US, is unconfirmed.

---

## Key Question 2: The Caption AI story (De Novo 2020 → GE 2023 → 2025-2026), published novice results, failures/retreats

### Takeaway
Caption Guidance was the first-ever FDA-authorized AI acquisition-guidance device (De Novo Feb 2020), validated by the Narang JAMA Cardiology 2021 nurse study (98.8% diagnostic for LV/effusion), then acquired by GE HealthCare in Feb 2023 and folded into Venue (2023) and Vscan Air SL (2024) under the "Verisound AI" brand; since then it has generated little news, no new novice RCTs, and the Butterfly partnership silently lapsed, while Butterfly itself retrenched in 2022-2023 before recovering.

### Cited Findings
- De Novo DEN190040 granted Feb 7, 2020 to Bay Labs (renamed Caption Health); 510(k) K200755 cleared April 16, 2020. — [FDA De Novo](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID=DEN190040); [FDA K200755](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K200755)
- Narang et al., JAMA Cardiology 2021;6(6):624-632: prospective 2-center study (Northwestern, Minneapolis Heart Institute), Mar–May 2019; 8 nurses with no echo experience, 30 patients each, 240 patients (mean age 61, 32.9% BMI>30); DL algorithm trained on >5M examples; diagnostic quality for LV size, LV function, pericardial effusion 237/240 (98.8%); RV size 222/240 (92.5%); nurse vs sonographer scans not significantly different for most parameters. — [Europe PMC record, DOI 10.1001/jamacardio.2021.0185](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1001/jamacardio.2021.0185&resultType=core&format=json)
- Butterfly signed an "exclusive strategic partnership" with Caption Health in Nov 2021 for AI-guided cardiac assessment. — [BusinessWire, Nov 15, 2021](https://www.businesswire.com/news/home/20211115005705/en)
- GE HealthCare agreed to acquire Caption Health (first acquisition as a standalone company), announced ~Feb 9, 2023, terms undisclosed, funded with cash; GE said it would continue operating Caption Care (technicians performing echo at alternate sites). — [Fierce Biotech](https://www.fiercebiotech.com/medtech/ge-healthcare-snaps-ultrasound-ai-maker-caption-health-first-acquisition-solo-company); [MedTech Dive](https://www.medtechdive.com/news/GEHC-acquisition-caption-health-AI-ultrasound/642514/); [DCVC](https://www.dcvc.com/post/ge-healthcare-acquires-caption-health-energizing-dcvc-s-thesis-around-ai-in-medicine.html)
- Oct 2023: Caption Guidance offered as optional add-on on Venue family; April 2024: Caption AI (guidance + AutoEF) on Vscan Air SL; branded under Verisound AI. — [GE Venue release](https://www.gehealthcare.com/en-us/about/newsroom/press-releases/ge-healthcare-launches-enhanced-venue-family-point-of-care-ultrasound-systems-featuring-ai-driven-caption-guidance); [GE Vscan Air SL release](https://www.gehealthcare.com/en-us/about/newsroom/press-releases/ge-healthcare-introduces-caption-ai-on-vscan-air-sl-wireless-handheld-ultrasound-system-to-help-more-clinicians-capture-diagnostic-quality-cardiac-images); [GE Verisound AI](https://www.gehealthcare.com/products/ultrasound/ultrasound-digital-solutions/verisound-ai)
- Caption Care was still marketing "turnkey, end-to-end echo programs" to health plans as a HLTH 2024 sponsor. — [HLTH 2024 sponsor page](https://hlth.com/2024event/sponsors/caption-care)
- A records-custodian listing shows "Caption Care P.C." (California) closed June 1, 2026; the listing does not link it to GE and the connection is unverified. — [Morgan Records Management](https://morganrecordsmanagement.com/custodian-of-medical-records/caption-care-p-c-california/)
- 2025-2026 activity: the only new publication found is a July 2026 Annals of Family Medicine pilot in 9 Spanish family-medicine clinics (~135,000 patients) using Vscan Air SL + Caption AI with family physicians given 12 hours of training; the paper reports no image-quality or detection results, only cost estimates (~€20 per AI-guided assessment vs ~€280 referral). — [Annals of Family Medicine 24(4):376](https://www.annfammed.org/content/24/4/376)
- GE's 2025 Verisound year-in-review emphasizes ViewPoint 6 worksheets and Verisound Collab, not Caption. — [GE Verisound 2025 review](https://www.gehealthcare.com/insights/article/verisound-makes-a-play-for-ultrasound-efficiency-2025-in-review)
- GE subsequently bought Intelligent Ultrasound's AI unit ($51M, 2024), signalling its guidance strategy is OB/Voluson as well as cardiac. — [MassDevice](https://www.massdevice.com/ge-healthcare-acquire-ai-intelligent-ultrasound/)
- Butterfly retreat: layoffs of ~10% (Aug 2022) and ~25% (Jan 2023), OpEx cut ~$2M/month, Q2 2023 revenue $18.5M (−3.8%), CEO change; restructuring declared complete in 2024; by Q2 2026 revenue was $32.6M (+39%). — [Fierce Biotech](https://www.fiercebiotech.com/medtech/butterfly-network-aims-cut-costs-further-following-staff-reductions); [MobiHealthNews](https://www.mobihealthnews.com/news/butterfly-network-announces-reorganization-after-38-drop-revenue-q2); [Butterfly Q2 2026 8-K](https://www.sec.gov/Archives/edgar/data/0001804176/000180417626000025/bfly-20260730xexx991.htm)
- Butterfly's current cardiac guidance path is third-party (HeartFocus available, UltraSight "coming soon"), not Caption. — [Butterfly Garden page](https://www.butterflynetwork.com/ai-marketplace)

### Inferences
- The Butterfly–Caption exclusive partnership (2021) effectively died with the GE acquisition; no source mentions it after 2023 and Butterfly now hosts GE's competitors.
- Caption's reach appears confined to GE hardware (Venue, Vscan Air SL); there is no evidence of GE licensing it to other platforms, which contrasts with UltraSight/DESKi's multi-vendor strategy and the Jan 2026 UltraSight cross-platform clearance.
- The absence of 2025-2026 GE press on Caption, plus the unverified June 2026 closure of a "Caption Care P.C." entity, suggests Caption Care's service business is at best quiet; this should be treated as a hypothesis.

### Gaps
- No definitive source on Caption Care's operational status in 2026 or on Caption AI unit volumes/revenue.
- No post-acquisition peer-reviewed novice study of Caption AI on Vscan Air SL with outcome numbers was found (the 2026 Spanish pilot reports none).
- The PubMed abstract page could not be fetched (cookie wall); abstract data were taken from the Europe PMC record.

---

## Key Question 3: Companies attempting tracked or sensorless freehand 3D on handhelds, and their status

### Takeaway
Commercial freehand 3D is almost entirely tracked (PIUR's proprietary sensor on cart systems, curefab's magnetic tracking, Velacur's guided sweep) or mechanized (iSono ATUSA, Delphinus, QT Imaging); the only handheld "3D" shipping at scale is Butterfly's electronically-steered bladder sweep (iQ Slice/Auto Bladder), and sensorless (IMU/deep-learning) freehand 3D remains research-stage with no FDA-cleared product found.

### Cited Findings

**PIUR imaging (Vienna) – tomographic ultrasound (tUS)**
- K240036 "PIUR tUS Infinity" cleared Sept 20, 2024: product code QIH (automated radiological image processing software), standalone add-on that upgrades "nearly any 2D ultrasound device" to 3D; CADe for thyroid nodules (TI-RADS), adults ≥22; company cites CPT 76377 reimbursement. — [FDA K240036](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K240036); [PIUR release](https://www.piurimaging.com/post/piur-imaging-receives-fda-clearance-for-revolutionary-3d-ultrasound-technology-piur-tus-infinity-n)
- K250484 "PIUR tUS inside" cleared June 30, 2025: built into select GE LOGIQ scanners; auto-reconstructs sagittal/transverse/coronal views from a single sweep; AI 3D segmentation of nodules/lobes; "compact PIUR Sensor" attaches for 3D and detaches for 2D (sensor modality not disclosed); claims "up to 80% less operator variability" without cited data. — [FDA K250484](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/pmn.cfm?ID=K250484); [AuntMinnie, July 2, 2025](https://www.auntminnie.com/clinical-news/ultrasound/news/15749880/piur-gets-fda-nod-for-new-ultrasound-device); [PIUR tUS inside page](https://piurimaging.com/piur-imaging-receives-fda-clearance-for-piur-tus-inside-bringing-advanced-3d-ultrasound-to-u-s-healthcare/)
- €5.6M growth capital to scale in US/Europe. — [PIUR release](https://piurimaging.com/piur-imaging-secures-e5-6-million-growth-capital-to-scale-tomographic-3d-ultrasound-in-the-usa-and-europe/)
- Pricing: not public. Handheld support: not stated (cart systems only in sources).

**curefab (Munich)**
- Curefab CS is a magnetically tracked freehand 3D add-on for conventional machines (vessel segmentation; carotid/thyroid studies; point accuracy 1.52 mm in an older carotid study). — [Thieme abstract](https://www.thieme-connect.com/products/ejournals/abstract/10.1055/s-0033-1355103); [Dealroom](https://app.dealroom.co/companies/curefab)
- The current curefab.com homepage presents the company as an engineering-services firm (embedded systems, GPU algorithms for "motion correction and 3D image reconstruction," medical navigation) with no product page, CE/FDA status, or news. — [curefab.com](https://www.curefab.com/)

**Sonic Incytes (Vancouver) – Velacur / Velacur ONE**
- Velacur: FDA-cleared point-of-care liver elastography using "machine learning ensures an optimal probe position followed by a guided 3D sweep with a handheld ultrasound" (3D S-WAVE; company product profile Dec 2020). — [Velacur product profile](https://www.sonicincytes.com/wp-content/uploads/2020/12/VelacurProductProfile_Dec2020.pdf); [Sonic Incytes launch release](https://www.sonicincytes.com/sonic-incytes-announces-fda-clearance-and-us-launch-of-velacurtm-to-help-manage-emerging-health-crisis/)
- Velacur ONE 510(k) announced Aug 12, 2025: adds B-mode and an AI organ overlay for liver localization; B-mode "enables 3–4x higher reimbursement." — [Sonic Incytes release](https://www.sonicincytes.com/fda-grants-510k-clearance-to-sonic-incytes-velacur-one/)
- Independent biopsy-referenced accuracy study published 2025. — [MDPI Diagnostics 15(5):615](https://www.mdpi.com/2075-4418/15/5/615)

**ImFusion (Munich)** – sells an SDK/"3D Ultrasound Suite" for freehand 2D/3D/4D processing "with and without available tracking data," supporting GE, Verasonics, Cephasonics, Telemed scanners and NDI/Atracsys/OptiTrack trackers; it is developer tooling, not a cleared end-user device (shop page returned 404 in Oct 2026). — [ImFusion ultrasound page](https://imfusion.com/products-overview/software-development-kit/ultrasound/)

**Butterfly – electronically steered handheld 3D**
- Auto Bladder Volume "acquires 3D bladder volumes by electronically sweeping the ultrasound beam"; stated accuracy ±7.5%; 2025 volunteer study (n=53) found 3D method error −11 to −12% vs −28 to −37% for 2D calipers. — [MDPI Diagnostics 15(17):2229](https://www.mdpi.com/2075-4418/15/17/2229)
- iQ+ quick card: tapping the 3D bar shows an interactive 3D render to verify the whole bladder was captured, "not for diagnostic use." — [URMC quick card](https://urmcpublic-lb1.urmc.rochester.edu/MediaLibraries/URMCMedia/Health%20Lab/images/Auto-Bladder-Volume-Quick-Card-copy.pdf)
- iQ3 (Feb 2024) added iQ Slice (46 simultaneous slices, automated beam steering) and iQ Fan; iQ+ Bladder specialty cart product launched May 2024. — [AuntMinnie iQ3](https://www.auntminnie.com/clinical-news/ultrasound/article/15664060/butterfly-network-launches-butterfly-iq3); [AuntMinnie iQ+ Bladder](https://www.auntminnie.com/clinical-news/ultrasound/article/15670901/butterfly-launches-iq-bladder-scanner)

**Automated/mechanized breast 3D**
- iSono Health ATUSA: K213620 (received Nov 16, 2021, cleared April 22, 2022, code IYO, 892.1560); wearable automated 3D whole-breast scan ~2 min/breast; commercial launch Jan 14, 2026; AI "partner" still in development and not FDA-cleared; 800-patient NIH-funded AUDIBLE study (NCT07505797) vs mammography/MRI; interpretation requires a trained breast physician. — [FDA K213620](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K213620); [BusinessWire, Jan 14, 2026](https://www.businesswire.com/news/home/20260114276390/en/iSono-Health-Unveils-ATUSA-The-Worlds-First-Wearable-Automated-Portable-FDA-Cleared-Breast-Ultrasound-Platform); [ClinicalTrials.gov](https://clinicaltrials.gov/study/NCT07505797); [Pulse2](https://pulse2.com/isono-health-launches-atusa-a-wearable-automated-breast-ultrasound-platform/amp/)
- Delphinus SoftVue: FDA PMA (2021) as adjunct to mammography in dense breasts; first commercial sale to Karmanos; Series D $30.4M Sept 2022; no 2025-2026 news found. — [ITN](https://www.itnonline.com/content/delphinus-receives-fda-approval-its-softvue-3d-whole-breast-ultrasound-tomography-system); [AuntMinnie](https://www.auntminnie.com/clinical-news/womens-imaging/breast/article/15631929/delphinus-raises-30m-to-commercialize-softvue-system)
- QT Imaging Holdings (Nasdaq: QTI): Breast Acoustic CT (510(k), SoftVue cited as predicate); March 10, 2026 clearance for tilted-transmitter configuration improving posterior coverage; Q1 2026 revenue $6.5M (13 scanners), Q2 $7.4M, H1 28 scanners, FY2026 guidance ~$39M; UAE clearance and Olea viewer 2026. — [BusinessWire, Mar 10, 2026](https://businesswire.com/news/home/20260310679250/en/QT-Imaging-Receives-FDA-Clearance-for-Its-Breast-Acoustic-CT-Scanner-Enhanced-Configuration-to-Improve-Posterior-Breast-Imaging-Coverage); [QT Q2 2026 release](https://secure.businesswire.com/news/home/20260812051029/en/QT-Imaging-Delivers-Strong-Second-Quarter-Growth-While-Building-the-Foundation-for-Commercial-Scale); [QT 10-Q Q2 2026](https://www.sec.gov/Archives/edgar/data/0001844505/000162828026056182/qti-20260630.htm)

**GE Voluson / Philips / Clarius / Exo 3D** – GE Voluson is the host of SonoLyst (mechanical/matrix 3D OB), but no freehand-3D or Vscan Air 3D feature was found; no Lumify, Clarius, or Exo Iris volumetric feature was found in any source. — [MassDevice](https://www.massdevice.com/ge-healthcare-acquire-ai-intelligent-ultrasound/); [clarius.com](https://clarius.com/); [Fierce Biotech on Exo](https://www.fiercebiotech.com/medtech/exo-officially-enters-handheld-ultrasound-race-launch-ai-powered-iris-system)

**Vortex Imaging (Sunnyvale/Givatayim)** – $12M seed (May 18, 2026; 10D Ventures, Entrée Capital, Harel T.E.C, Connecticut Innovations, PhiFund) for "Vortex360," a handheld producing 3D images via Full Waveform Inversion (probe with NVIDIA Jetson, cloud GPU reconstruction), urology/nephrology first; no FDA submission confirmed; patent US 11,559,285 B2. — [Founderland](https://www.founderland.ai/articles/vortex-imaging-raises-12m-for-handheld-3d-medical-imaging-de-mpf8nkx2)

**Sensorless / low-cost tracking – research only (2024-2026)**
- MICCAI 2024: "current mainstream solutions, relying on IMUs or deep learning, encounter issues like cumulative drift"; proposes coupling-pad landmarks. — [Springer](https://link.springer.com/chapter/10.1007/978-3-031-72083-3_52)
- Feb 2026: camera-on-probe + QR film on skin, ORB-SLAM pose, DICOM output (research). — [PMC12933897](https://pmc.ncbi.nlm.nih.gov/articles/PMC12933897/)
- 2026 preprints: MLRecon (markerless coarse-to-fine pose), MoNetV2, global-visual-guidance reconstruction. — [arXiv 2603.00990](https://arxiv.org/pdf/2603.00990); [arXiv 2506.15835](https://arxiv.org/pdf/2506.15835); [arXiv 2607.12398](https://arxiv.org/pdf/2607.12398)

### Inferences
- Every cleared freehand-3D product uses an external sensor or a mechanized/steered sweep; "sensorless" 3D on a consumer handheld has no FDA precedent, so a first entrant would likely need a 510(k) under QIH (image processing) with a tracked predicate such as PIUR, or a De Novo.
- The commercial sweet spots for 3D so far are organ-volume quantification (thyroid, bladder, liver, breast) where reimbursement (CPT 76377, breast screening) exists; nobody markets a general-purpose freehand 3D for handhelds.
- Butterfly's electronically steered iQ Slice is the only mechanism that gives a true volume on a handheld without tracking, but it is limited to the transducer's steering angle (bladder-sized FOV).

### Gaps
- PIUR's sensor technology (IMU vs EM vs optical) and pricing are undisclosed; handheld compatibility unknown.
- curefab's current product/CE status could not be confirmed (homepage has no product listing).
- ImFusion pricing could not be retrieved (shop page 404).
- No evidence either way on whether GE's Vscan Air or Philips Lumify have any 3D roadmap.

---

## Key Question 4: 2025-2026 startups and funding in AI ultrasound guidance or freehand 3D

### Takeaway
Funding in 2025-2026 clustered around cardiac guidance (UltraSight $24M B2, Sept 2026), prenatal AI (BrightHeart €11M/$12.8M Series A, Jan 2026), home OB (Pulsenmore Nasdaq listing Jan 2026), and 3D handheld hardware (Vortex Imaging $12M seed, May 2026); no dedicated freehand-3D-software startup round was found.

### Cited Findings
- UltraSight $24M Series B2 (Sept 23, 2026), total $42M; JAMA Cardiology (Aug 28, 2026) Mayo Clinic study: 9 research staff with no ultrasound experience after 4 hours' training; AI analyzed ~97% of exams; 93% sensitivity / 96% specificity for moderate-or-greater aortic stenosis (presented at ESC 2026). — [HIT Consultant](https://hitconsultant.net/2026/09/23/ultrasight-secures-24m-series-b2-ai-cardiac-ultrasound-echosystem-jama-cardiology/); [Mayo Clinic News Network](https://newsnetwork.mayoclinic.org/?p=417632); [HospiMedica](https://mobile.hospimedica.com/medical-imaging/articles/294812874/ai-guided-ultrasound--enables-nonexpert-screening-for-aortic-stenosis.amp.html). Note: Mayo's release refers only to "AI models"; attribution to UltraSight comes from UltraSight/HLTH coverage — [HLTH](https://hlth.com/insights/news/ultrasight-raises-24-million-to-expand-ai-guided-cardiac-ultrasound)
- UltraSight ACC.26 abstracts (Mar 2026): novices with Echosystem detected moderate+ AS with 99.1% accuracy (different cohort from the JAMA paper). — [DAIC](https://www.dicardiology.com/content/acc26-presentations-discuss-how-ultrasight-ai-enables-non-experts-perform-diagnostic)
- BrightHeart (Paris) €11M Series A (Jan 8, 2026), five FDA clearances in 2025 for prenatal AI. — [BusinessWire](https://www.businesswire.com/news/home/20260108664483/en/BrightHeart-Raises-%E2%82%AC11M-Series-A-to-Scale-Expert-Level-AI-Platform-for-Prenatal-Ultrasound)
- Vortex Imaging $12M seed (May 18, 2026) for FWI-based handheld 3D. — [Founderland](https://www.founderland.ai/articles/vortex-imaging-raises-12m-for-handheld-3d-medical-imaging-de-mpf8nkx2)
- Cardio.ai $4.5M led by Cedars-Sinai Technology Ventures (2026); Cardio Vision (AS) and EchoMeasure 510(k)-cleared; integrations pending with Clarius, Butterfly, Vave, GE. — [Signify, May 6, 2026](https://www.signifyresearch.net/insights/partnerships-product-launches-and-ai-innovation-drive-ultrasound-market-momentum/)
- Pulsenmore: Nasdaq listing Jan 2026 (PLSM); Clalit FC deal ~$4.5M; Ouma Health partnership June 2026. — [Pulsenmore](https://pulsenmore.com/); [Signify, Jan 30, 2026](https://www.signifyresearch.net/insights/product-launches-ai-advances-and-global-partnerships-kick-off-2026/)
- PIUR imaging €5.6M growth capital (2025). — [PIUR](https://piurimaging.com/piur-imaging-secures-e5-6-million-growth-capital-to-scale-tomographic-3d-ultrasound-in-the-usa-and-europe/)
- DESKi $6M seed (date per secondary source). — [hyper.ai](https://hyper.ai/en/stories/963ff2b5af76fa63154deea206b42e23)
- Biotics AI fetal AI FDA-cleared Jan 2026, assesses "image quality and anatomical completeness"; Diagnoly "Fetoly" real-time on-device fetal assistant in 20+ countries after a GE collaboration; ASUS developing real-time AI guidance; MAUI Imaging and Qure.ai received Gates grants for POCUS TB/pneumonia AI (Jan 2026). — [Signify, Jan 30, 2026](https://www.signifyresearch.net/insights/product-launches-ai-advances-and-global-partnerships-kick-off-2026/); [Signify, May 6, 2026](https://www.signifyresearch.net/insights/partnerships-product-launches-and-ai-innovation-drive-ultrasound-market-momentum/)
- Butterfly Embedded: Midjourney co-development/licensing deal (Nov 2025) reported as $15M upfront + $10M/yr for five years by a secondary blog (unverified); Butterfly's 8-K confirms the Midjourney partnership but discloses no terms. — [pinggy blog (unverified)](https://pinggy.io/blog/ai_medical_imaging_diagnostics_2026/); [Butterfly Q2 2026 8-K](https://www.sec.gov/Archives/edgar/data/0001804176/000180417626000025/bfly-20260730xexx991.htm)
- Butterfly Q1 2026 headline reports an FDA clearance for an AI gestational-age tool (headline only; details not retrieved). — [Munich Startup feed](https://insights.munich-startup.de/news/feed/butterfly-network-q1-revenue-up-25-to-26-5m-wins-fda-nod-for-ai-gestational-age-tool)
- ThinkSono: Breakthrough designation Feb 2026, 510(k) July 2026; funding not found. — [Endovascular Today](https://evtoday.com/news/fda-clears-thinksonos-ultrasound-AI-guidance-software-to-evaluate-suspected-dvt)

### Inferences
- Investors are backing guidance + automated interpretation bundles with a narrow clinical question (AS, HF, DVT, gestational age) rather than general-purpose guidance; this is where the evidence base and reimbursement arguments are strongest.
- Freehand 3D has attracted only hardware-centric (Vortex) or add-on (PIUR) money; no software-only sensorless 3D startup has disclosed a round.

### Gaps
- Crunchbase/PitchBook were not directly accessible; smaller 2025 seed rounds may be missed.
- Funding amounts for ThinkSono, Diagnoly, Biotics AI, iSono Health (2025-26) were not found.

---

## Key Question 5: Products combining guidance with a 3D map / coverage map / scan completeness, and known gaps where no commercial product exists

### Takeaway
No shipping product combines real-time probe guidance with a spatial 3D "coverage map" of what has been scanned; the closest commercial analogues are view-checklist completeness (Sonio, Biotics AI), sweep-protocol acquisition (Exo SweepAI, FAMLI blind sweeps, Pulsenmore), and 3D "did I capture the whole organ" renders (Butterfly bladder), while spatial coverage tracking exists only in patents and academic prototypes.

### Cited Findings
- Spatial coverage mapping over a body diagram (recording probe pose, drawing covered area, steering operator to unscanned regions, post-exam completeness display) is described in a patent family "System and method for tracking completeness of co-registered medical image data" (breast), not in a marketed product. — [USPTO 11839511](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11839511); [USPTO 10835204](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10835204)
- Sonio (Samsung) provides "real-time oversight of exam completeness" via a visual checklist that updates as images arrive and reports commonly missed views; FDA-cleared. — [Sonio platform](https://www.sonio.ai/platform)
- Biotics AI fetal AI (FDA Jan 2026) "assesses image quality and anatomical completeness." — [Signify, Jan 30, 2026](https://www.signifyresearch.net/insights/product-launches-ai-advances-and-global-partnerships-kick-off-2026/)
- Butterfly's Auto Bladder 3D render exists specifically "to validate that the whole bladder has been captured in the sweep." — [URMC quick card](https://urmcpublic-lb1.urmc.rochester.edu/MediaLibraries/URMCMedia/Health%20Lab/images/Auto-Bladder-Volume-Quick-Card-copy.pdf)
- PIUR tUS inside reconstructs three orthogonal planes from a single tracked sweep (3D from guided sweep, but no real-time novice guidance claimed). — [AuntMinnie](https://www.auntminnie.com/clinical-news/ultrasound/news/15749880/piur-gets-fda-nod-for-new-ultrasound-device)
- Velacur combines ML probe-position optimization with a guided 3D sweep (liver elastography only). — [Velacur product profile](https://www.sonicincytes.com/wp-content/uploads/2020/12/VelacurProductProfile_Dec2020.pdf)
- Academic: AI real-time guidance cut shoulder exam time 34% for junior residents (multicenter, 2026). — [PubMed 41904092](https://pubmed.ncbi.nlm.nih.gov/41904092/); EUS navigation RCT significantly improved scan completeness. — [PubMed 40990678](https://pubmed.ncbi.nlm.nih.gov/40990678)
- Academic: Echo-QR AR guidance (QR markers on probe and chest) let novices find the acoustic window for 92% of organs but only 41% of images were acceptable; JHU APL mixed-reality predictive-anatomy guidance for novices (headset). — [PMC11257884](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11257884/); [optics.org](https://optics.org/news/predictive-anatomical-guidance-system-helps-novices-acquire-ultrasound-images)
- Research freehand-3D note: reconstruction "is only able to reconstruct 3D volumes if the scanned region is static during a probe swipe." — [PMC12933897](https://pmc.ncbi.nlm.nih.gov/articles/PMC12933897/)
- General-purpose handheld apps that track probe pose over a body map were not found; Clarius T-Mode (live anatomy labels) and reference atlases are the nearest commercial features. — [clarius.com](https://clarius.com/); [Ultrasound Anatomy Atlas](https://apps.apple.com/us/app/ultrasound-anatomy-atlas/id6760451635)

### Inferences
- Known gaps with no commercial product as of Oct 2026: (1) real-time novice guidance for any non-cardiac organ on a handheld (abdomen, thyroid, kidney, MSK) except DVT; (2) sensorless freehand 3D reconstruction on a consumer handheld; (3) a spatial coverage/completeness map that tells a novice which regions remain unscanned; (4) guidance that is cleared for lay/consumer use outside pregnancy (Pulsenmore is the only lay-use authorization); (5) voice-delivered guidance.
- The regulatory pieces for a guidance + 3D-map product already exist separately (QJU for guidance; QIH for 3D processing; Pulsenmore De Novo for lay use), so a combined product would most plausibly be cleared as two functions rather than one new De Novo.
- Multi-vendor compatibility (UltraSight Jan 2026, DESKi PCCP, ThinkSono on Clarius) is now the commercial norm for guidance software; a 3D-map feature would be expected to ride on Butterfly/Clarius/Lumify rather than new hardware.

### Gaps
- No vendor was found publicly describing a coverage-map feature on a roadmap; absence of evidence here may reflect confidential development.
- Independent performance data for most 3D products (PIUR's 80% variability claim, iSono operator-independence) are company claims without cited studies.
- Signify Research reports were read only through free insight posts; paid market-size data were not accessed.

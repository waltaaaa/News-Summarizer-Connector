# Proposed Keyword Taxonomy (v1)

Built from a stratified sample of 400 headlines (seed 42) across the 8,926-article corpus.
Edit this table directly: change names/definitions/aliases, set **Keep?** to `no` to drop a row,
or add new rows. Then run `python3 scripts/finalize_taxonomy.py` to freeze it into `taxonomy.json`.

Conventions: keyword names are short Title Case; aliases (semicolon-separated) catch the
model's near-miss phrasings and normalize them to the canonical name. Region keywords let the
graph cluster by geography as well as theme.

## Regions

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Canada | Canadian companies, policy, or ecosystem | Canadian | "Canada's AI edge is human"; "Is BDC too big to change?" | yes |
| United States | US policy, politics, and companies | US; USA; America; American | "Trump to endorse coal for data center power" | yes |
| Europe & UK | EU, UK, and European policy and tech | EU; Europe; European Union; UK; Britain | "European Innovation Scoreboard" | yes |
| China | Chinese tech, policy, and competition | Chinese | "China is running multiple AI races" | yes |
| Global & Emerging Markets | Multilateral bodies, global trends, developing economies | global south; emerging markets; G7; UN; multilateral | "Harnessing IP for development: Latin America" | yes |

## AI & Digital

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| AI Models & Research | New models, AI labs, capabilities, AI science | foundation models; frontier AI; AI research; LLMs | "OpenAI launches two 'open' AI reasoning models" | yes |
| AI Adoption | Deployment of AI in firms, government, and sectors | AI deployment; enterprise AI; AI in business; applied AI | "How to take AI from demo to real-world deployment" | yes |
| AI Agents | Agentic AI, AI assistants, task automation | agentic AI; AI assistants | "Software needs to evolve to make way for the agents" | yes |
| AI Policy & Regulation | AI laws, national strategies, governance | AI regulation; AI governance; AI strategy; AI law | "Draft federal AI strategy aims to scale up adoption" | yes |
| AI Safety & Ethics | Alignment, bias, risk, responsible AI | responsible AI; AI ethics; AI bias; AI risk; AI alignment | "MIT study finds that AI doesn't, in fact, have values" | yes |
| AI & Work | AI's impact on jobs, labour automation | AI and jobs; automation and labour; AI job losses; future of work | "Automation, Learning, and Career Dynamics" | yes |
| AI Economics | AI valuations, bubble debate, macro effects of AI | AI bubble; AI investment; economics of AI | "Forecasting the Economic Effects of AI" | yes |
| AI Infrastructure | Compute buildout, AI chips deals, AI energy demand | AI compute; AI chips; compute infrastructure | "Meta signs deal for millions of Amazon AI CPUs" | yes |
| Semiconductors | Chips, fabs, chipmakers, chip supply | chips; chipmakers; fabs; chip industry | "Everything is chips now" | yes |
| Data Centres | Data-centre construction, siting, energy use | data centers; datacentres; datacenters | "The climate impact of data centres" | yes |
| Cloud Computing | Cloud market, providers, cloud policy | cloud; cloud market | "3 U.S. tech firms own 85% of Canada's cloud market" | yes |
| Quantum | Quantum computing and quantum tech | quantum computing; quantum tech | "Advisory council urges Ottawa to spend $2B on quantum" | yes |
| Cybersecurity | Hacks, breaches, security tools and policy | security; hacks; breaches; infosec | "The worst hacks and breaches of 2026 (so far)" | yes |
| Data Privacy | Privacy law, data protection, surveillance | privacy; GDPR; surveillance; data protection | "EU draft would wreck core principles of the GDPR" | yes |
| Digital Sovereignty | National control over digital infrastructure and data | tech sovereignty; sovereign AI; sovereign cloud | "Microsoft's sovereignty-focused pitch to Canada" | yes |
| Digital Platforms | Social media, marketplaces, apps, platform business | social media; platforms; online platforms | "Reddit looks to AI search as its next big opportunity" | yes |
| Big Tech | Strategy and conduct of the major tech firms | large tech companies; tech giants | "Big Tech to work with Trump administration" | yes |
| Antitrust & Competition | Competition policy, monopoly, market power | competition policy; monopoly; antitrust | "Y Combinator says Google is a 'monopolist'" | yes |
| Content & Copyright | Copyright, AI training data rights, creator rights | copyright; AI training data; licensing | "Studio Ghibli wants OpenAI to stop training on its work" | yes |

## Startups & Capital

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Startup Funding | Individual funding rounds, seed to late stage | funding round; fundraising; raises; seed round; series A | "Doji raises $14M for virtual try-ons" | yes |
| Venture Capital | VC firms, funds, and investment trends | VC; venture investment; venture funds | "Capital concentrates as Canadian VC market narrows" | yes |
| Mergers & Acquisitions | M&A, acquihires, takeovers | M&A; acquisitions; acquihire; takeover | "Nvidia has acquired Canadian AI startup CentML" | yes |
| IPOs & Public Markets | Listings, public-company finance, stock markets | IPO; stock market; public markets; listings | "A year after filing to IPO, Cerebras raises $1.1B" | yes |
| Scaleups & Unicorns | Late-stage growth, unicorn milestones, ARR milestones | unicorn; scaleup; scale-up; growth stage | "Koho becomes Canada's latest unicorn" | yes |
| Startup Ecosystem | Community, accelerators, incubators, awards, events | incubators; accelerators; startup community | "Former analyst to launch new Vancouver incubator" | yes |
| Layoffs & Restructuring | Job cuts, downsizing, corporate restructuring | layoffs; job cuts; downsizing | "eBay to lay off 800 staff" | yes |
| Fintech | Financial technology, payments, banking tech | payments; banking tech; financial technology | "Nesto secures nearly $1.5B valuation" | yes |
| Crypto & Blockchain | Crypto assets, stablecoins, web3 | crypto; stablecoins; blockchain; bitcoin; web3 | "Stablecoins and the Future of Finance" | yes |
| Institutional Capital | Pension funds, sovereign funds, public investment banks | pension funds; CPP; sovereign wealth; BDC; institutional investors | "La Caisse puts up $240M for Montreal AI data centre" | yes |

## Innovation & Industrial Policy

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Industrial Policy | Sectoral strategy, subsidies, state economic intervention | industrial strategy; sectoral policy; state intervention | "Quantifying industrial strategies across 20 OECD countries" | yes |
| Innovation Policy | Innovation programs, strategy, and policy design | innovation strategy; innovation programs | "Canada's innovation policies need overhaul" | yes |
| Mission-Driven Innovation | Mission-oriented policy, moonshots, grand challenges | mission-oriented innovation; moonshots; grand challenges; missions | "How do mission-oriented innovation policies work?" | yes |
| Public Procurement | Government purchasing as an innovation/industry lever | government procurement; buy Canadian; defence procurement | "Buying What We Build: Public Buying for Canadian Innovation" | yes |
| R&D Funding | Public and private research funding, grants | research funding; science funding; grants; research investment | "UK R&D spending falls again" | yes |
| Research Policy | How science is organized, evaluated, and governed | science policy; research assessment; evidence-informed policy; metascience | "Reducing waste in the competition for research grants" | yes |
| Tax & Incentives | Tax credits, investment incentives, subsidies | tax credits; subsidies; incentives; SR&ED | "US chipmakers could see bigger tax credits" | yes |
| SME Policy | Small and medium business support and performance | SMEs; small business; mittelstand | "Monitoring SMEs' performance in Europe" | yes |
| Regional Innovation | Regional development, clusters, smart specialization | clusters; regional development; smart specialization; innovation districts | "How regions make missions work" | yes |
| Productivity | Productivity growth, gaps, and drivers | productivity crisis; productivity gap | "Most of you think Canada has a productivity crisis" | yes |
| Economic Growth | Growth, GDP, macroeconomic performance and policy | macroeconomics; GDP; economic performance; fiscal policy | "Canada Can Grow Faster by Unlocking Its Own Market" | yes |
| State Capacity | Government capability, public-sector innovation, regulatory reform | public sector innovation; government capacity; regulatory reform; govtech | "How Regulatory Reform Happens" | yes |

## Research, Universities & Talent

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Universities & Research | Higher education institutions and academic research | higher education; academia; universities; research institutions | "University-business collaboration readiness index" | yes |
| Commercialization | Tech transfer, spinouts, lab-to-market | tech transfer; spinouts; IP commercialization; lab to market | "Closing the IP Commercialization Gap in Canada" | yes |
| Intellectual Property | Patents, IP strategy and protection | IP; patents; patent policy | "CSIS warning shows Ottawa can't ignore Canada's IP crisis" | yes |
| Talent & Skills | Workforce skills, training, STEM education | skills; workforce development; upskilling; STEM; education | "Why Canada's nation-building moment demands a skills revolution" | yes |
| Brain Drain & Migration | Talent mobility, immigration, retention | immigration; talent mobility; brain drain; emigration | "Curbing brain drain: Incentive programs" | yes |
| Labour Market | Employment data, hiring trends, job market | employment; jobs; labour force; hiring | "Labour Force Survey, January 2026" | yes |

## Energy & Climate

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Clean Energy | Renewables deployment: solar, wind, hydro, geothermal | renewables; solar; wind; geothermal; renewable energy | "Solar to dominate energy by 2035" | yes |
| Cleantech | Climate-tech startups and innovation | climate tech; greentech; green innovation | "Acceleration of cleantech startups through open innovation" | yes |
| Climate Policy | Climate strategy, net zero, emissions rules, adaptation | net zero; emissions policy; decarbonization; climate adaptation | "The Cost of Net Zero" | yes |
| Energy & Grid | Electricity systems, grid, utilities, energy markets | grid; electricity; utilities; energy transition; energy markets | "Gridcare thinks 100 MW is hiding in the grid" | yes |
| Nuclear & Fusion | Nuclear power and fusion energy | fusion; nuclear power; SMRs | "Avalanche thinks fusion should think smaller" | yes |
| EVs & Batteries | Electric vehicles and the battery industry | electric vehicles; batteries; EV charging; battery industry | "The true cost of Quebec's EV battery dream" | yes |
| Critical Minerals | Mining, minerals, resource value chains | mining; rare earths; minerals; lithium | "The Critical Minerals Value Chain" | yes |
| Carbon Management | Carbon capture, removal, markets, accounting | carbon capture; CCUS; direct air capture; carbon markets; hydrogen | "Deep Sky boots up direct air carbon capture facility" | yes |

## Sectors

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Biotech & Health | Life sciences, pharma, healthtech, medtech | healthtech; life sciences; pharma; medtech; biotech; health innovation | "ABK Biomedical raises $35M for liver cancer treatment" | yes |
| Defence Tech | Defence industry, military tech, dual-use | defense tech; military tech; dual-use; defence industry | "The defence-tech gold rush is testing venture capital" | yes |
| Space | Space industry, rockets, satellites | space tech; satellites; rockets; aerospace | "Kepler's CEO on Canada's space ambitions" | yes |
| Robotics & Autonomy | Robots, self-driving vehicles, drones | autonomous vehicles; self-driving; drones; robots | "Waymo bought Apple's self-driving proving ground" | yes |
| Agtech & Food | Agriculture and food innovation | agriculture; food tech; farming | "Fostering a Sustainability Transition Toward Organic Farming" | yes |
| Telecom | Telecommunications and connectivity | telecommunications; 5G; broadband | "Telecom workers say AI being used to monitor employees" | yes |
| Consumer Tech | Devices, gadgets, consumer apps and services | gadgets; devices; consumer apps | "Chipolo debuts rechargeable trackers" | yes |
| Enterprise Software | B2B software, SaaS, developer tools | SaaS; B2B software; developer tools; dev tools | "1Password crosses $400-million USD ARR milestone" | yes |
| Media & Creators | Streaming, gaming, publishing, creator economy | streaming; gaming; creator economy; publishing; entertainment | "Streaming platforms say CRTC's Cancon demand violates trade pact" | yes |

## Trade & Geopolitics

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Trade & Tariffs | Trade policy, tariffs, trade agreements | tariffs; trade policy; trade war; trade agreements | "The problem with Canada's counter-tariffs on U.S. steel" | yes |
| Supply Chains | Supply-chain resilience, reshoring, onshoring | reshoring; onshoring; supply chain resilience; nearshoring | "An update on the great reallocation in US supply chain trade" | yes |
| Export Controls | Tech export restrictions and decoupling | decoupling; tech restrictions; chip controls | "How Semiconductor Export Controls Could Harm US Chipmakers" | yes |
| Foreign Investment | FDI, investment screening, foreign ownership | FDI; investment screening; foreign ownership | "FDI and innovation spillovers: evidence from Chilean firms" | yes |
| Tech Geopolitics | Technology competition between powers | tech rivalry; technology competition; geopolitics of tech; geoeconomics | "Deepseek and the New Geopolitics of AI" | yes |

## Society & Inclusion

| Keyword | Definition | Aliases | Example headlines | Keep? |
|---|---|---|---|---|
| Tech & Society | Social impacts of technology, democracy, information | democracy; misinformation; social impact; civil society | "The impact of advanced AI systems on democracy" | yes |
| Inequality & Inclusion | Distributional effects, inclusive innovation, accessibility | inclusion; inclusive innovation; accessibility; equity | "Skill-biased technological change... automation and inequality" | yes |
| Indigenous Innovation | Indigenous-led business and innovation | First Nations; Indigenous; Indigenous-led | "The Critical Minerals Value Chain: What First Nations Need to Know" | yes |
| Social Innovation | Social-purpose innovation, common good, welfare innovation | common good; social purpose; welfare innovation | "Starting, Scaling and Sustaining Social Innovation" | yes |

# 🎓 College Darpan — AI-Powered College Discovery & Transparency Platform

> **Tagline:** *Your Future. Your College. Your Choice.*  
> **Target Region:** Telangana, India  
> **Academic Scope:** TS ECET (Diploma Lateral Entry to 2nd Year) & TS EAPCET (First-Year B.Tech)  
> **Theme:** Pastel Pink (`#F6C9D5`) & Pastel Blue (`#C9E2F7`)

---

## 🌟 1. Project Overview

**College Darpan** is a full-stack, AI-powered college recommendation and transparency platform specifically designed for engineering aspirants in Telangana. Built by a third-year AIML diploma student as an academic capstone project, it addresses the deceptive practices of commercial college portals: inflated placement figures, hidden fee extras, sponsored rankings, and the total neglect of diploma students seeking lateral entry into the second year of engineering.

### Key Pillars:
- **Zero-Fabrication Guarantee:** Every fee and placement figure is audited against official Telangana government notifications (TAFRC & TGCHE) or marked with transparent data confidence labels (`Verified`, `Needs Verification`, or `Information Unavailable`).
- **TS ECET Lateral Entry Specialization:** Direct closing rank analysis and branch transition mapping for SBTET diploma graduates entering 2nd-year B.Tech.
- **Explainable Hybrid AI Recommendation Engine:** Normalized multi-criteria scoring with plain-English rationales explaining *why* a college matches your goals.
- **Offline-Ready AI Chatbot (Darpan AI Assistant):** Conversational counselor running on a rule-backed database engine without paid external APIs or cloud dependencies.
- **Side-by-Side Comparison Matrix:** Compare up to 4 colleges simultaneously. The chatbot provides a pairwise explainer for financial and placement trade-offs.

---

## 🎨 2. Design System & Color Palette

College Darpan strictly follows an educational **pastel pink and pastel blue** aesthetic:

| Design Token | Hex Code | Visual Application |
| :--- | :--- | :--- |
| **Canvas Background** | `#FFF8FB` | Main website background |
| **Primary Pastel Pink** | `#F6C9D5` | Highlights, badges, hero gradients |
| **Soft Blush Pink** | `#FBE3EA` | Active tabs, chips, subtle cards |
| **Primary Pastel Blue** | `#C9E2F7` | Action buttons, focus rings |
| **Light Sky Blue** | `#E5F2FC` | Explanation boxes, diff rows |
| **Lavender Accent** | `#E7DDF8` | Accreditation badges, subtle borders |
| **Card Background** | `#FFFFFF` | Rounded cards with soft shadows |
| **Main Typography** | `#374151` | Primary readable text |
| **Secondary Typography**| `#6B7280` | Subtitles, labels, metadata |
| **Success Accent** | `#BFE6D0` | Verified status badges |

---

## 🛠️ 3. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Jinja2 Templates, Chart.js
- **Backend:** Python 3, Flask Web Framework, REST JSON APIs
- **Database:** SQLite 3 with parameterized queries and foreign key constraints
- **Testing:** Pytest (19 automated tests covering scoring, safeguards, and web routes)
- **AI / NLP:** Rule-backed intent matching with database context querying (offline, 0 external API cost)

---

## 🚀 4. Simple Setup & Installation Guide

Follow these simple steps in your terminal or Command Prompt:

### Step 1: Open Terminal in the Project Folder
```bash
cd "c:\Users\user\Desktop\college darpan website"
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `Flask` and `pytest`)*

### Step 3: Initialize the Database (One-time setup)
```bash
python database/init_db.py
```
*This creates the SQLite database tables and seeds 14 verified Telangana engineering institutions with full metrics, branches, and cutoffs.*

### Step 4: Run Automated Tests
```bash
python -m pytest tests/
```
*Runs the test suite against a temporary copy of the local database. Test results depend on your environment and are not assumed here.*

### Step 5: Start the College Darpan Web Server
```bash
python app.py
```
Open your web browser and visit:
```
http://127.0.0.1:5000
```

---

## 📁 5. Folder & Architecture Structure

```
college darpan website/
├── app.py                      # Flask application entry point with all web & API routes
├── config.py                   # Global configuration (paths, secret keys, default weights)
├── requirements.txt            # Python dependencies (Flask, pytest)
├── README.md                   # Comprehensive project documentation
├── database/
│   ├── schema.sql              # Clean SQLite DDL schema with foreign keys
│   ├── db.py                   # Reusable connection & parameterized SQL query helper
│   ├── init_db.py              # Database initialization script
│   └── seed_data.py            # Verified Telangana institutions dataset
├── services/
│   ├── college_service.py      # Querying, filtering, metrics, and comparisons
│   ├── recommendation_engine.py# Hybrid recommendation engine with normalized weights
│   └── chatbot_service.py      # Darpan AI Assistant conversational logic
├── templates/
│   ├── base.html               # Shared layout: pastel navbar, footer, floating chatbot
│   ├── index.html              # Home page: Hero, live stats, search, featured colleges, FAQ
│   ├── colleges.html           # College directory: multi-criteria filter sidebar & cards
│   ├── college_detail.html     # College profile: fees, placements, academics, cutoffs
│   ├── recommendations.html    # AI recommendation wizard & ranked match scorecards
│   ├── compare.html            # 2-to-3 side-by-side comparison matrix with AI explainer
│   ├── chatbot.html            # Dedicated full-page Darpan AI Assistant interface
│   ├── admission_guide.html    # TS ECET (lateral entry) & TS EAPCET admission guide
│   └── about.html              # Project story, transparency methodology, tech stack
├── static/
│   ├── css/
│   │   └── style.css           # Pastel pink & blue theme styling & responsive layout
│   └── js/
│       ├── main.js             # General navigation, comparisons state, toast alerts
│       ├── recommendations.js  # Slider updates & recommendation form interactivity
│       ├── compare.js          # Comparison matrix controller & AI trade-off explainer
│       └── chatbot.js          # Markdown parser, chat bubbles & typing indicators
└── tests/
    ├── test_recommendations.py # Unit tests for the recommendation algorithm
    └── test_routes.py          # Integration tests for web routes & JSON API endpoints
```

---

## 🧠 6. AI Recommendation Algorithm Explained

The hybrid recommendation engine combines three mathematical and logical screening phases:

### Phase 1: Content-Based Compatibility
1. **Branch Compatibility ($S_{\text{branch}}$):**
   - Direct Code Match (e.g. user selects `AIML` and college offers `AIML`): **100%**
   - Allied Discipline (e.g. user selects `AIML` and college offers `CSE` or `Data Science`): **75%**
   - Any Branch Option: **100%**
2. **Tuition Affordability ($S_{\text{fee}}$):**
   - College tuition $\le$ stated budget: **100%**
   - College tuition within $+15\%$ of budget: **75%**
   - College tuition within $+30\%$ of budget: **50%**
   - Missing/Unverified fee: **Neutral 60%** (avoids penalizing colleges for unverified data)
3. **Placement Performance ($S_{\text{place}}$):**
   - Based on verified placement percentage ($0–50\text{ pts}$) + average package ($0–50\text{ pts}$). Missing placement data defaults to a neutral 55% with a visible verification alert.
4. **Location Convenience ($S_{\text{loc}}$):**
   - Target district match: **100%**
   - Greater Hyderabad region (Medchal / Ranga Reddy): **80%**
5. **Infrastructure & Faculty ($S_{\text{infra}}$):**
   - Scored using NAAC grade ($A^{++}$, $A^{+}$, $A$), NIRF ranking, and doctoral faculty density.

### Phase 2: Priority Weight Normalization
User slider values ($w_i \in [1, 5]$) are normalized:
$$W_i = \frac{w_i}{\sum_{j} w_j}$$
*(Defaults: Branch 30%, Affordability 25%, Placements 20%, Location 10%, Infrastructure 15%)*

### Phase 3: Overall Match Score Calculation
$$\text{Match Score} = \sum (S_i \times W_i) \in [0, 100]$$

### Phase 4: Admission Eligibility Safeguard
To protect students from false guarantees:
- Past cutoffs are checked for the candidate's specific entrance exam (`TS ECET` or `TS EAPCET`), rank, branch, and category (`OC_BOYS`, `BC_B`, `SC`, etc.).
- If data is absent, the system displays:
  > *"Admission eligibility cannot be confirmed with the available data."*
- Distinguishes explicitly between **Preference Match** and **Historical Counselling Standing**.

---

## 🤖 7. Darpan AI Assistant (Chatbot Capabilities)

The conversational assistant operates locally using a rule-based NLP intent classifier and database query engine. Try asking:
- *"Which colleges offer AIML in Hyderabad?"*
- *"Suggest colleges within my tuition budget of 1 lakh."*
- *"Compare OU and Geethanjali College."*
- *"Which colleges should I investigate for ECET lateral entry?"*
- *"What is the difference between ECET and EAPCET?"*
- *"What factors should I consider when choosing a college?"*
- *"Which college information is still unverified?"*
- *"Tell me about CBIT."*

---

## 🏛️ 8. Telangana College Dataset (Initial Targets)

The database includes 14 premier and representative institutions across Telangana:
1. **OUCE** — University College of Engineering, Osmania University *(University / Public)*
2. **JNTUH** — JNTUH University College of Engineering, Hyderabad *(University / Public)*
3. **CBIT** — Chaitanya Bharathi Institute of Technology, Gandipet *(Private Autonomous)*
4. **VCE** — Vasavi College of Engineering, Ibrahimbagh *(Private Autonomous)*
5. **VNRV** — VNR Vignana Jyothi Institute of Engineering and Technology, Bachupally *(Private Autonomous)*
6. **GRIET** — Gokaraju Rangaraju Institute of Engineering and Technology, Bachupally *(Private Autonomous)*
7. **CVRH** — CVR College of Engineering, Ibrahimpatnam *(Private Autonomous)*
8. **MREC** — Malla Reddy Engineering College, Maisammaguda *(Private Autonomous)*
9. **GCET** — Geethanjali College of Engineering and Technology, Keesara *(Private Autonomous)*
10. **IARE** — Institute of Aeronautical Engineering, Dundigal *(Private Autonomous)*
11. **ANUR** — Anurag University, Ghatkesar *(State Private University)*
12. **MGIT** — Mahatma Gandhi Institute of Technology, Gandipet *(Private Autonomous)*
13. **BVRW** — BVRIT Hyderabad College of Engineering for Women, Nizampet *(Private Autonomous)*
14. **VMEG** — Vardhaman College of Engineering, Shamshabad *(Private Autonomous)*

---

## 📄 9. Project Submission Details

- **Project Title:** College Darpan — AI-Powered College Discovery & Transparency Platform
- **Academic Program:** Diploma in Artificial Intelligence & Machine Learning (3rd Year Capstone)
- **Board:** State Board of Technical Education and Training (SBTET), Telangana
- **Year of Submission:** October 2026
- **License:** Open Educational Academic Resource

## Sourced directory update (2026–27)

The app adds 54 institution listings from the official SBTET Telangana LPCET
2026–27 booklet. Each added row carries the source URL, source name, academic
year, and an identity-listing verification status. The importer is additive and
idempotent; it inserts missing records only and does not populate fees, cutoffs,
placements, hostel data, or programme branches.

Existing database rows are preserved. Their older source and verification
fields have not been re-audited as part of this update. Missing or stale fee,
cutoff, placement, and programme data should be checked against current official
notices. Do not run database/init_db.py against an existing database; that
initializer recreates the schema.

The assistant remains local and rule-based. It searches the database, marks
legacy programme results as needing current verification, and links to sources
where available. An external language model is not configured; using one would
require an API credential and could involve a paid service.

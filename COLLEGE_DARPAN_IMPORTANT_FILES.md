# College Darpan Important Project Files

## Project Overview

College Darpan is a Flask web application for browsing Telangana colleges, viewing institution details, comparing colleges, and getting rule-based recommendations. It uses Jinja templates, browser-side JavaScript and CSS, and a local SQLite database.

This appendix lists the main source files that explain the project’s structure and implementation. It excludes generated caches, backups, and raw database records.

## Application and Configuration

| File | Purpose |
|---|---|
| `app.py` | Creates the Flask app; defines website routes, JSON API endpoints, request validation, comparison session handling, and error pages. |
| `config.py` | Sets platform configuration, database path, session signing key, debug setting, and default recommendation weights. |
| `requirements.txt` | Lists the Python packages required to run the application and its tests. |

## Database Files

| File | Purpose |
|---|---|
| `database/db.py` | Opens SQLite connections and provides parameterized query and write helpers. |
| `database/schema.sql` | Defines the tables and indexes for colleges, branches, metrics, admission cutoffs, chat sessions, and shortlists. It begins with `DROP TABLE` statements, so executing it recreates the schema and can erase existing records. |
| `database/init_db.py` | Initializes the database schema and project seed data. |
| `database/seed_data.py` | Provides the project’s seed records. |
| `database/import_sbtet_directory.py` | Adds missing polytechnic directory entries from the bundled source data; it is designed to be additive and idempotent. |
| `database/sbtet_polytechnics_2026.json` | Bundled source data consumed by the SBTET polytechnic directory importer. |
| `database/college_darpan.db` | Local SQLite database used by the default configuration. Treat this as data, not source code; do not publish it without checking its contents and permissions. |

## Business Logic and Services

| File | Purpose |
|---|---|
| `services/college_service.py` | Queries colleges and their metrics, branches, cutoffs, statistics, filters, details, and comparison data. |
| `services/recommendation_engine.py` | Scores college matches using supported preferences and provides explanations and admission-data safeguards. |
| `services/chatbot_service.py` | Implements local intent matching and database-backed responses for college, course, fee, placement, and comparison questions. |

## Website Pages

| File | Purpose |
|---|---|
| `templates/base.html` | Shared page layout, navigation, footer, and common script inclusion. |
| `templates/index.html` | Homepage with entry points to the directory and discovery features. |
| `templates/colleges.html` | Searchable and filterable college directory. |
| `templates/college_detail.html` | Institution detail page. |
| `templates/compare.html` | Side-by-side college comparison page. |
| `templates/recommendations.html` | Student preference form and ranked recommendation results. |
| `templates/chatbot.html` | Full-page chatbot interface. |
| `templates/polytechnic.html` | Polytechnic discovery page. |
| `templates/engineering.html` | Engineering discovery page. |
| `templates/pharmacy.html` | Pharmacy discovery page. |
| `templates/admission_guide.html` | Admission pathway guidance page. |
| `templates/data_methodology.html` | Data sources and verification methodology page. |
| `templates/about.html` | Project overview and about page. |

## Frontend Assets

| File | Purpose |
|---|---|
| `static/css/style.css` | Shared visual styling and responsive layout. |
| `static/js/main.js` | Shared site interactions, including directory and comparison controls. |
| `static/js/compare.js` | Comparison tray and comparison summary interactions. |
| `static/js/recommendations.js` | Recommendation form controls, dynamic options, and preference sliders. |
| `static/js/chatbot.js` | Chat message display and requests to the chatbot API. |

## Tests and Documentation

| File | Purpose |
|---|---|
| `tests/conftest.py` | Configures route tests to use a temporary copy of the project database. |
| `tests/test_routes.py` | Tests website pages and API route behavior, including comparison and request validation. |
| `tests/test_recommendations.py` | Tests recommendation scoring helpers and the recommendation pipeline. |
| `tests/test_sbtet_directory_import.py` | Tests importer idempotency and preservation of existing records. |
| `README.md` | Project overview, setup instructions, technology stack, and usage notes. |

## Main Request Flow

1. A browser requests a page or API endpoint defined in `app.py`.
2. The route validates request values and calls a service in `services/`.
3. The service obtains data through `database/db.py` from the configured SQLite database.
4. Website routes render Jinja templates; API routes return JSON for the JavaScript in `static/js/`.
5. The test files exercise route behavior, recommendation logic, and the additive data importer.

## Recommended Files to Reference in a Project Report

For a concise technical explanation, use `app.py`, `config.py`, `database/schema.sql`, `database/db.py`, the three service modules, `templates/base.html`, `templates/colleges.html`, `templates/recommendations.html`, `templates/compare.html`, the corresponding frontend JavaScript files, and the three test modules. Refer to the database by schema and role; include the raw `.db` file only if the report submission explicitly requires the data file.

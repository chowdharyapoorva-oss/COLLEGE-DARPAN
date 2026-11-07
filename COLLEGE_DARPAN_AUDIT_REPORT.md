# College Darpan Audit Report

**Audit date:** 2026-10-28  
**Scope:** Source inspection, read-only SQLite audit, isolated project copy, and available syntax checks.  
**Overall status:** PARTIAL — the project test suite and selected browser workflows passed after one confirmed chatbot filter bug was fixed. Official data completeness, accessibility/responsive matrix, and additional edge cases remain unverified.

## A. Executive summary

The project is a Flask/Jinja website with a local SQLite database, parameterized SQL services, a rule-based database chatbot, a weighted recommendation engine, and a session-backed comparison feature. Source inspection found a coherent route/template structure and an existing pytest suite. The configured data file is `database/college_darpan.db` (172,032 bytes at inspection).

The configured SQLite database was queried using Python 3.12 sqlite3 in read-only mode. Flask and pytest were installed only in an isolated copy, where the existing project test suite passed 29 tests. Node.js syntax checks passed, and selected browser workflows ran against the copied database. A chatbot district-filter bug was reproduced and fixed in the project after creating a fresh backup; database contents were not changed.

## B. Technologies and architecture

- Backend: Python 3 / Flask, route functions in `app.py`.
- Frontend: Jinja templates, CSS, and browser JavaScript under `templates/` and `static/`.
- Database: SQLite, configured by `COLLEGE_DARPAN_DATABASE_PATH` or defaulting to `database/college_darpan.db`.
- Data access: `database/db.py`; SQL statements in services use bound parameters in the reviewed query paths.
- Features: college directory and filters, detail pages, recommendations, chatbot, comparison, live statistics, methodology/about/admission pages, and JSON APIs.
- External AI: none evident in the inspected chatbot implementation. `services/chatbot_service.py` uses local intent/keyword logic and database queries; describing it as generative AI would be inaccurate.
- Dependencies listed: Flask and pytest. No ORM or browser-test dependency is listed.

Schema names in `database/schema.sql`: `colleges`, `branches`, `college_metrics`, `admission_cutoffs`, `chat_sessions`, and `shortlists`. The schema includes indexes for common category, district, type, branch, metric, and cutoff lookups. `database/import_sbtet_directory.py` contains an additive importer that can add missing directory records and metadata columns when the application is run directly; it was not executed during this audit.

## C. Exact database counts and coverage

**PASS (database query) / NOT RUN (official completeness):** The configured database was queried read-only with Python sqlite3. Counts below describe stored rows only; they do not prove completeness against Telangana’s official college lists.

| Requested measure | Result | Status |
|---|---:|---|
| Total college records | 83 | PASS (exact row count) |
| Distinct college IDs / codes | 83 IDs; 83 unique codes | PASS |
| Polytechnic | 62 | PASS |
| B.Tech / Engineering | 15 | PASS |
| Pharmacy | 6 | PASS |
| Counts by district and institution type | Queried; see distribution below | PASS (stored values) |
| Missing required name/code/district fields | 0 rows | PASS |
| Duplicate college codes | 0 | PASS |
| Foreign-key violations | 0 | PASS |
| SQLite integrity check | `ok` | PASS |
| Telangana district completeness | Not compared with official reference list | NOT RUN |
| Statewide data coverage | Cannot establish without reference verification | NOT RUN |

The schema shows that names, codes, districts, categories, branches, fees, placements, and cutoffs have database fields. Their record-level population and provenance were not verified. The SBTET importer labels its source and academic year and does not add fees, placements, or cutoffs, but this does not establish that existing records are complete or accurate.

## D. Feature-by-feature results

| Area | Status | Evidence / limitation |
|---|---|---|
| Flask route inventory | PASS (test client) | Existing route tests exercised the application endpoints; selected browser pages also loaded. |
| Template endpoint names | PASS (static check only) | All `url_for()` endpoint names found in templates map to Flask routes or Flask’s built-in `static` endpoint. No rendered-template check was possible. |
| Directory/search/filter behavior | PASS (selected combinations) | Browser exercised category, district, branch, name search, management, fee ceiling, verified placement, and sort controls on the copied database; official results and edge cases remain unverified. |
| College details and invalid IDs | PASS (test client) | Existing route tests rendered a college profile and checked invalid-ID handling. |
| Recommendation engine | PASS (test client/browser sample) | Unit/integration tests passed; browser produced a ranked result for rank 150/AIML and analyzed 15 engineering records. Admissions accuracy remains unverified against official allotments. |
| Chatbot | PASS (tested query) | Rule-based local assistant returned Hyderabad-only results after the confirmed location-filter bug was fixed; the reply labels the programme records as historical leads needing current verification. |
| Comparison | PASS (test client) | Route tests covered add/remove/clear, duplicate/invalid IDs, and the four-college limit; browser comparison UI was not separately exercised. |
| Frontend interactions/responsiveness | PARTIAL | Selected browser workflows passed at one desktop viewport. A full responsive, keyboard, accessibility, and console/network audit remains NOT RUN. |
| JavaScript syntax | PASS | Node `--check` completed successfully for all four files under `static/js/`. |
| API status/error behavior | PASS (covered cases) | Route tests exercised healthy and invalid recommendation/comparison/chat inputs; broad malformed-payload fuzzing remains NOT RUN. |
| Database integrity | PASS | Read-only SQLite integrity and foreign-key checks passed; write behavior was not run. |

## E. Recommendation-system audit

The implementation is a local, weighted multi-criteria scoring engine, not evidence of a trained or external AI model. `app.py` validates category, exam, rank, budget, reservation category, branch, district, institution preference, and weights before calling `get_recommendations`. The recommendation module has scoring helpers for branch match, affordability, placements, and admission safeguards. Missing fee data is treated as unverified in the unit tests’ expected behavior. The test suite and a rank-150 AIML profile produced ranked records and explanations. Official admission outcomes and broader profile/category combinations remain unverified.

## F. Chatbot audit

The chatbot is a rule-based/local database assistant. `process_chat_message` routes intents such as comparisons, pharmacy, polytechnic, ECET, fees, placements, and college lookup to local handlers. The API limits messages to 1,000 characters and returns structured responses. The client escapes HTML before applying its lightweight Markdown formatting. The browser rendered a real assistant answer; the pytest API test covered a branch/location query and verifies every matched record is in Hyderabad. Timeout and broader factual grounding remain unverified.

## G. Search and filters

`get_all_colleges` uses parameterized SQL and supports name/code/location/address/branch search, exact district/type filters, branch filters, fee ceiling, source-backed verified placement filtering, hostel, admission pathway, and sorting. `max_fee` values that are not all digits are silently ignored by the service; the UI/API behavior for malformed values has not been tested. Normal combinations and returned counts were smoke-tested in the browser. Unicode and malformed-filter handling remain NOT RUN; no pagination parameter was identified in the reviewed route.

## H. Comparison

The inspected API stores selected IDs in the Flask session, validates current records, removes duplicates, and limits the list to four. The comparison page resolves IDs from session and calls `compare_colleges`. Existing route tests passed and exercised this workflow end to end through Flask’s test client. Cookie settings explicitly include `HttpOnly` and `SameSite=Lax`; `Secure` is not explicitly set in `app.py` and should be configured for HTTPS deployments.

## I. Frontend and accessibility

The expected pastel pink/blue design is documented in the README and present in frontend styling. The homepage and feature pages rendered at the browser’s default desktop size. Mobile/tablet layout, keyboard operation, focus visibility, accessibility, and broad console/network checks remain NOT RUN. No redesign or visual edits were made.

## J. Backend, database, and security

- Reviewed service queries use placeholders for user-provided values; no SQL injection issue was confirmed by source inspection.
- Flask sessions use an environment-provided secret key or a randomly generated per-process key. Without `SECRET_KEY`, sessions will not remain valid across application restarts; set a stable secret in deployment configuration and do not publish it.
- `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SAMESITE="Lax"` are set. `SESSION_COOKIE_SECURE` is not explicitly configured.
- No CSRF middleware/token handling was identified in the reviewed app. The JSON APIs accept POST requests and comparison state is stored in a cookie-backed session. Review CSRF protection before exposing state-changing endpoints cross-origin.
- Generic 404/500 handlers avoid returning stack traces in the reviewed source. Actual error responses were not exercised.
- Direct startup calls an additive SBTET importer before launching the server. Do not launch against irreplaceable data during testing until a backup is available; the importer can add records/schema columns. It was not run here.

## K. Performance and accessibility findings

The directory service loads branch summaries with one additional query per college, so it has an N+1 query pattern as the dataset grows. No performance benchmark was possible. Schema indexes exist for several major lookup fields. Accessibility and responsive performance were NOT RUN.

## L. Bugs and fixes

One confirmed bug was fixed: chatbot branch queries ignored a district stated in the user question. The handler now detects a matching stored district and applies it to both current/source-linked and legacy programme queries. A regression assertion verifies that “Which colleges offer AIML in Hyderabad?” returns only Hyderabad records. The fix passed the project suite and browser recheck.

## M. Files changed

- Added this report.
- Added `.audit_backup_20261028.zip` before writing the report; it contains the project source, tests, templates, static assets, and database snapshot as they existed before the report was added.
- The continuation audit fixed one confirmed chatbot district-filter bug in `services/chatbot_service.py` and strengthened `tests/test_routes.py`. The pre-existing `.audit_backup_20261028.zip`, created before the earlier report and containing the original source, tests, and database, was retained as the rollback snapshot. No database records were changed.

## N. Tests executed and exact results

- Static route/template endpoint-name cross-check: **PASS** — all template endpoints resolve to app endpoints or Flask `static`.
- Project pytest suite: **PASS** — 29 passed, 0 failed, 0 skipped (executed against the isolated copy).
- Python launcher shims: **UNAVAILABLE** — `py.exe` and `python.exe` from WindowsApps could not start.
- SQLite counts/integrity checks: **PASS** — Python sqlite3 queried the original configured database with `mode=ro`; no writes were issued.
- Python syntax check: **PASS** — `python -m compileall -q .` completed on the isolated project copy.
- JavaScript syntax checks: **PASS** — Node.js v24.22.1 `--check` passed all four frontend JavaScript files.
- Browser smoke checks: **PASS** — home, pharmacy filter, category/district/branch/search filters, engineering district/branch/management/fee/verified/sort controls, recommendation form, and local assistant were exercised on the isolated copy. Comparison session behavior is covered by the passing route tests.

**Executed-check summary:** Project suite 29 passed; Python compileall passed; Node syntax passed for 4 scripts; read-only original database and isolated copy checks passed; selected browser workflows passed. No failed project tests. Broad responsive/accessibility and official data-completeness checks remain not run.

## O. Runtime isolation details

Dependencies were installed into the isolated copy after network access was approved. Project routes, recommendation API/form, chatbot API/UI, and comparison session flows executed through pytest; selected manual browser workflows also ran against a localhost server configured to use only the copied database. The real database was accessed only through read-only SQLite queries. The SBTET startup importer was not invoked.

## P. Remaining known issues / limitations

- Stored counts, duplicate college-code check, required-field check, and database integrity are now verified. Completeness against official lists, district coverage, and source accuracy remain unknown.
- Additional viewport sizes, accessibility, malformed/Unicode search edge cases, and independent official verification of database coverage remain unverified.
- The directory’s per-college branch queries may become slow with a larger dataset.
- HTTPS deployments should explicitly set secure session cookies; state-changing session APIs should be reviewed for CSRF protection.
- This report cannot certify submission readiness until official data completeness, current accuracy, accessibility, and the remaining edge cases are checked.

## Q. Recommended next steps before submission

1. Compare the stored directory against current official TGCHE, SBTET, TAFRC, and PCI lists to establish data completeness and correctness.
2. Check responsive layouts and accessibility at phone, tablet, and desktop sizes, including keyboard flow and focus visibility.
3. Review secure cookie and CSRF settings for the intended deployment environment.


## R. Continuation audit: runtime discovery and executed evidence (2026-10-28)

### Runtime inventory

- **Python:** Bundled Python 3.12.14 is runnable. The WindowsApps `py.exe` and `python.exe` launchers fail to start. No project virtual environment was found.
- **Python packages:** The base runtime includes `sqlite3` and pip; Flask and pytest were installed under `_deps` in the isolated project copy only. No system-wide packages were installed.
- **Node.js:** v24.22.1 is available.
- **Browser:** Chrome is installed/running and the Codex browser-control runtime is available; a Flask test server was started on `127.0.0.1` with the isolated database copy. The user’s existing Chrome page was not navigated or changed.
- **Isolation:** A copy of the project, including a copy of the SQLite database, was made under the current audit workspace at `work/college-darpan-audit-copy`. No application tests or app startup were run against the original folder; only the explicitly read-only SQL audit accessed its database.

### Database evidence

The configured original database at `database/college_darpan.db` was opened with SQLite URI `mode=ro`. Query results: 83 total college rows and 83 distinct IDs; primary categories are `polytechnic` 62, `engineering` 15, and `pharmacy` 6. There are 74 branch rows connected to 29 distinct colleges. 26 distinct district labels contain a specified location, and 7 records use `Not specified in source`. Institution types: Government Polytechnic 61, Private Autonomous 13, Private Unaided 4, State Private University 2, University College 3. Required name/code/district fields are nonempty on all 83 rows; college codes have no duplicates. `PRAGMA integrity_check` returned `ok`; `PRAGMA foreign_key_check` returned no rows. These figures are database contents, not proof that all Telangana institutions are included or currently licensed.

### Executed checks and feature status

| Check | Result | Evidence / limit |
|---|---|---|
| Original SQLite integrity | PASS | Read-only `PRAGMA integrity_check` returned `ok`. |
| Foreign-key relationships | PASS | Original database and isolated copy returned empty `PRAGMA foreign_key_check` results. |
| College counts/categories | PASS | Original database and isolated copy agree: 83 total, 62 polytechnic, 15 engineering, 6 pharmacy. |
| Required identity/location fields and duplicate codes | PASS | 0 missing name/code/district values; 0 duplicate college codes. |
| Frontend JavaScript syntax | PASS | Node `--check` passed `chatbot.js`, `compare.js`, `main.js`, and `recommendations.js`. |
| Python source syntax | PASS | `python -m compileall -q .` completed on the isolated project copy. |
| Existing route/template endpoint-name scan | PASS (static only) | Prior static result remains; no Jinja rendering was run. |
| Project pytest suite | PASS | 29 passed, 0 failed, 0 skipped in the isolated copy. |
| Flask routes, search/filter combinations, recommendations, chatbot, comparison APIs | PASS (covered workflows) | Project test client passed; browser smoke exercised selected filter, recommendation, and chatbot flows. |
| Browser rendering/responsiveness/interactions | PARTIAL | Selected pages/workflows passed at one viewport; full responsive/accessibility audit remains NOT RUN. |
| Startup/importer | NOT RUN | Direct startup can write/add records; it was intentionally not invoked. |

One chatbot location-filter bug was reproduced and fixed in the isolated copy; its regression test passes. The original source changes were applied only after creating `.audit_backup_before_chatbot_fix_20261028.zip`. The database was not changed.

### Remaining next steps

Compare all records with current official TGCHE, SBTET, TAFRC, and PCI publications; validate omitted districts and licenses; then complete phone/tablet accessibility and visual checks. Continue running the app only against a disposable database copy because direct startup can invoke the additive SBTET importer.


## S. Final runtime and fix results (2026-10-28)

### Runtime and safety

Dependencies declared in `requirements.txt` (Flask and pytest) were installed under `_deps` in the isolated workspace copy. The test run used the project’s unchanged `tests/` directory; temporary database files were directed into the isolated copy because the system temp directory was not writable. The localhost Flask server bound only to `127.0.0.1` and used `work/college-darpan-audit-copy/database/college_darpan.db`; `prepare_database()` and the additive importer were not run. The original project database remained unchanged.

### Test results

- **Project pytest suite: PASS — 29 passed, 0 failed, 0 skipped.** It passed in the isolated copy and was rerun from the requested Desktop project after applying the fix. The run used disposable database copies and temporary paths in the audit workspace. Coverage includes directory routes, recommendation form/API validation, chatbot API, comparison session flow and limits, health, and importer idempotency.
- **Python syntax: PASS** — `python -m compileall -q .` completed on the isolated copy.
- **JavaScript syntax: PASS** — Node `--check` passed all four frontend scripts.
- **Database: PASS** — 83 stored records: 62 polytechnic, 15 engineering, and 6 pharmacy; 83 unique college IDs/codes, no missing required name/code/district values, SQLite integrity `ok`, no foreign-key violations. The copied database produced the same category counts.
- **Browser smoke: PASS (selected workflows)** — homepage showed 83 records; pharmacy category returned 6 and pharmacy + Hyderabad returned 2. The directory UI accepted category, district, branch, name search, management, maximum fee, verified-placement, and sort selections. A sample rank 150 AIML recommendation ranked 15 engineering records and rendered explanations. The assistant answered its suggested AIML-in-Hyderabad question. The route suite exercised comparison workflows; browser comparison was not separately repeated.
- **Still NOT RUN:** full device-size/accessibility audit, malformed and Unicode search edge cases, live deployment behavior, official-source completeness, and current accuracy/licensing verification of college data.

### Confirmed chatbot bug and correction

Before the correction, the question “Which colleges offer AIML in Hyderabad?” returned six legacy programme records from Hyderabad, Medchal-Malkajgiri, and Ranga Reddy because `handle_branch_query` ignored the district in the question. I updated `handle_branch_query` to detect a district present in the query and apply it to both source-linked and legacy programme queries. The same browser question now returns five records, all with district `Hyderabad`, and still clearly labels them historical leads needing current verification. `tests/test_routes.py` now asserts that every matched college for this query is in Hyderabad. The 29-test suite passed after the change.

### Backups and changed files

The pre-existing `.audit_backup_20261028.zip` predates the confirmed fix and contains the original source, tests, and database; it was retained as the rollback snapshot. No new backup archive was created during this continuation. The continuation changes only `services/chatbot_service.py`, `tests/test_routes.py`, and this audit report. No college database content was edited.

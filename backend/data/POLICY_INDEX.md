# NSUT policy corpus (24 original files in `data/documents/`)

Scope: standing policies (any date) + every notice/circular dated 2026. Older notices (2020-2025 circulars, old fee
structures, 2025 calendars/course-committee lists, hostel mess fees, GNCTD guidelines) were removed.
Metadata: `source_register.csv`; rules: `rule_registry.csv` (22 rules, each citing a kept document + clause).
All files are the university's originals, unmodified.

## Standing policies (9)
| doc_id | Document |
|---|---|
| NSUT-BTECH-REG-2019 | B.Tech Regulations 2019-I(A) (attendance Cl. 11, passing Cl. 12, grading, degree Cl. 15) |
| NSUT-BTECH-RULES-2019 | Academic Rules extract (renumbered; attendance = Cl. 5) |
| NSUT-ORD-II-2019 / NSUT-ORD-II-GAZ-2020 | Ordinance-II (UG/PG) and its Delhi Gazette publication |
| SENATE-SUMMER-2020 | Summer-semester guidelines (Senate) |
| COE-UFM-2025 | Unfair-means rules |
| TNP-POLICY-2024-25 | Placement policy (latest public one) |
| CVSPK-RULES-2020 | Scholarship & incentive rules |
| HOSTEL-RULES-2024 | Hostel general rules |

## Released in 2026 (15)
BOM-MAKEUP-2026, DEAN-MAKEUP-GUIDE-2026, DEAN-MAKEUP-NOTIF-2026, ACAD-BACKLOG-MODES-2026, DEAN-SUMMER-2026,
ACAD-ATT-2026 (15 Sep 2026), FEE-2026-27, ACAD-FEE-NOINST-2026, ADM-FIRSTYEAR-2026, HOSTEL-PROHIB-2026,
HOSTEL-BH4-FEE-2026, CAL-ODD-2026-27, CAL-EVEN-2026, CAL-EVEN-2026-ADD, COE-SUMMER-COURSES-2026 (course codes sheet).

## Conflicts still present in this corpus (Annex A test material)
1. Attendance: Regs Cl. 11.3-11.6 (relaxation +10%/+5%, 60% floor) vs ACAD-ATT-2026 (no condonation at MSE, none claimed at ESE).
2. Regs Cl. 12.3 "no supplementary examinations" vs ACAD-BACKLOG-MODES-2026 (Exam-Only Mode) and the make-up exam documents (grade "I").
3. Summer semester: SENATE-SUMMER-2020 (max 2 courses, max grade B) vs DEAN-SUMMER-2026 (max 5 courses, max grade A; fees 14,000 SM / 10,000 EoM).
4. Placement policy: Core "dream" threshold 6 LPA (p.5-6) vs 5 LPA (p.8) inside the same document; hostel quiet hours differ between HOSTEL-RULES-2024 and HOSTEL-PROHIB-2026.

## Gaps and caveats
- No NEP-era (2022+) B.Tech regulations or credit scheme is publicly available; the 2019 Regulations remain the rulebook.
- No placement policy after 2024-25 is public. 2026 hostel-fee/admission notices are in the corpus but only partly mined into rules.
- Scanned documents were OCR'd (RapidOCR) at ingestion; `ocr=Y` is stored per chunk. OCR text can contain errors - check scans before citing exact figures.
- `REPORTED` rows in `rule_registry.csv` were not re-read by me against the source.

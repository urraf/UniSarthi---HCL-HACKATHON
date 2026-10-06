"""Build data/source_register.csv (Annex B) and data/rule_registry.csv (Annex C) for the NSUT corpus.

Every row describes an ORIGINAL file in data/documents/ (downloaded, never rewritten).
Every rule traces to a clause in a document in the register; the clauses marked VERIFIED
were read directly from the PDF/scan by the author, the rest are as reported by the
corpus-collection step (see `verified` column) and should be re-checked before demo.
Dates: effective_from is the printed date of the document where it could be read,
otherwise the notice-board posting date (date_basis column says which).
"""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RETRIEVED = "2026-10-06"
IMS = "https://www.imsnsit.org/imsnsit/notifications.php (Archive)"
DRIVE = "https://www.nsut.ac.in (Drive link, see note)"

SR_COLS = ["doc_id", "title", "issuer", "authority_level", "doc_type", "version", "effective_from",
           "effective_to", "supersedes", "scope_programmes", "scope_batches", "provenance",
           "retrieved_on", "synthetic", "file_name", "scanned", "date_basis"]

# doc_id, title, issuer, level, type, version, eff_from, eff_to, supersedes, programmes, batches, provenance, file, scanned, date_basis
D = [
 ("NSUT-BTECH-REG-2019", "Regulations for Undergraduate Programme of Bachelor of Technology (Regulations-2019-I(A))", "Senate / Board of Management, NSUT", 1, "regulation", "2019-I(A)", "2019-07-01", "", "", "B.Tech", "2019+", "https://drive.google.com/file/d/1CW5WiUt2DGhRRmf-AXastkHqeBC4_5d6", "NSUT_BTech_Regulations_2019_I-A.pdf", "N", "session start 2019-20 (approval dates blank in doc)"),
 ("NSUT-BTECH-RULES-2019", "Academic Rules and Regulations of the NSUT B.Tech Programme (extract, renumbered)", "Coordinator UMC", 3, "notice", "2019", "2019-07-29", "", "", "B.Tech", "2019+", IMS + " 29-07-2019", "NSUT_BTech_Academic_Rules_Extract_2019.pdf", "N", "posting date"),
 ("NSUT-ORD-II-2019", "Ordinance-II: Bachelor's and Master's Programmes", "NSUT Senate / BoM", 1, "regulation", "II", "2019-07-01", "", "", "ALL", "2019+", "https://drive.google.com/file/d/1CTYQr6_46Jriqad87lchZq0CXWwATt6c", "NSUT_Ordinance-II_UG_PG_2019.pdf", "N", "session start 2019-20"),
 ("NSUT-ORD-II-GAZ-2020", "Ordinance-II as published in Delhi Gazette Extraordinary No.122", "Govt. of NCT of Delhi / NSUT", 1, "regulation", "Gazette-2020", "2020-07-02", "", "", "ALL", "2019+", "https://drive.google.com/file/d/1bWZ9fn3ve9jfRYCvQhDUc8rF9Zi6Ae-Q", "NSUT_Ordinance-II_Delhi_Gazette_2020.pdf", "N", "gazette date"),
 ("ACAD-SALIENT-2021", "Salient points of Academic Rules (Table 1 and Cl. 12)", "Asst. Registrar (Academics)", 2, "circular", "F.220(314)/1655", "2021-03-17", "", "", "B.Tech", "2019+", IMS + " 18-03-2021", "NSUT_Salient_Points_Academic_Rules_2021-03-17.pdf", "Y", "printed date"),
 ("ACAD-EXAMINERS-2023", "Notice on examiners under Clause 14.1(e)", "Academic Section", 2, "circular", "F.No.220(364)/193", "2023-05-25", "", "", "B.Tech", "ALL", IMS + " 25-05-2023", "NSUT_Acad_Notice_Examiners_Clause14_2023-05-25.pdf", "Y", "posting date"),
 ("COE-CGPA-PCT-2024", "Conversion of CGPA to percentage of marks", "Controller of Examinations", 2, "circular", "220(138)/1066", "2024-01-29", "", "", "ALL", "ALL", "https://drive.google.com/file/d/1kS2dAB-s3Qsn5lNUH1HKJHQWTtetW3RH", "NSUT_CoE_CGPA_to_Percentage_2024-01-29.pdf", "Y", "posting date"),
 ("COE-UFM-2025", "Rules on unfair means in examinations", "Controller of Examinations", 2, "circular", "2025", "2025-05-05", "", "", "ALL", "ALL", "https://drive.google.com/file/d/17KkBZM7kw5KAMm54nl0ES4kXRjrUKT8f", "NSUT_CoE_Unfair_Means_Rules_2025.pdf", "N", "posting date"),
 ("DEAN-NEP-LAB-2025", "Marking scheme for lab-based (L:T:P=3:0:2) courses under NEP", "Dean Academic", 2, "circular", "F.220(466)/NEP/Acad/1233", "2025-07-07", "", "", "B.Tech", "2022+", IMS + " 09-09-2025 (posted)", "NSUT_DeanAcad_NEP_Lab_Course_Marking_2025-09-09.jpg", "Y", "printed date 7/7/2025 (VERIFIED); posted 2025-09-09"),
 ("DEAN-FE-EO-GRADING-2025", "Grading of FE/EO courses taken via MOOC/NPTEL", "Dean Academics", 2, "circular", "F.220(548)/1364", "2025-01-15", "", "", "B.Tech", "ALL", IMS + " 16-01-2025", "NSUT_DeanAcad_FE_EO_NPTEL_Grading_2025-01-15.pdf", "Y", "posting date"),
 ("DEAN-NPTEL-GUIDE-2025", "NPTEL course guidelines", "Dean Academics", 2, "circular", "F.220/1363", "2025-01-15", "", "", "B.Tech", "ALL", IMS + " 16-01-2025", "NSUT_DeanAcad_NPTEL_Guidelines_2025-01-15.pdf", "Y", "posting date"),
 ("BOM-MAKEUP-2026", "BoM resolution: make-up exams once a year in Summer Semester (Exam-Only Mode)", "Registrar", 1, "regulation", "BOM-22", "2025-07-01", "", "", "ALL", "ALL", IMS + " 30-01-2026", "NSUT_BoM_Makeup_Exam_Resolution_2026-01.pdf", "N", "'w.e.f. Odd Semester 2025' (approx. start); BoM met 2025-11-28"),
 ("DEAN-MAKEUP-GUIDE-2026", "Make-up examination guidelines 2025-26", "Dean Academics", 2, "circular", "2025-26", "2026-01-21", "", "", "ALL", "ALL", IMS + " 21-01-2026", "NSUT_DeanAcad_Makeup_Exam_Guidelines_2025-26.pdf", "N", "posting date"),
 ("DEAN-MAKEUP-NOTIF-2026", "Notification: applications for make-up examination", "Dean Academics", 2, "circular", "F.220(56)/101", "2026-05-07", "", "", "ALL", "ALL", IMS + " 07-05-2026", "NSUT_DeanAcad_Makeup_Exam_Notification_2026-05-07.pdf", "Y", "posting date"),
 ("ACAD-BACKLOG-MODES-2026", "Backlog registration: Exam-Only Mode and Study Mode", "Asst. Registrar (Academics)", 2, "circular", "2026-01", "2026-01-27", "", "", "B.Tech", "ALL", IMS + " 27-01-2026", "NSUT_Acad_Backlog_Registration_Modes_2026-01-27.pdf", "Y", "posting date"),
 ("ACAD-PROMO-2024", "Promotion criteria and year-back students", "Academic Section", 2, "circular", "F.220(190)/376", "2024-06-20", "", "", "B.Tech", "ALL", IMS + " 20-06-2024", "NSUT_Acad_Promotion_Criteria_YearBack_2024-06-20.pdf", "N", "posting date"),
 ("SENATE-SUMMER-2020", "Summer Semester guidelines (4th Senate meeting)", "Senate", 1, "regulation", "F.220(333)/53", "2020-02-26", "", "", "ALL", "ALL", IMS + " 15-04-2021", "NSUT_Senate_Summer_Semester_Guidelines_2020-06-11.pdf", "Y", "Senate meeting date"),
 ("DEAN-SUMMER-2024", "Summer Semester guidelines 2024", "Dean Academics", 2, "circular", "F.220(430)/161", "2024-05-08", "", "", "ALL", "ALL", IMS + " 08-05-2024", "NSUT_DeanAcad_Summer_Semester_Guidelines_2024-05-08.pdf", "N", "posting date"),
 ("DEAN-SUMMER-2026", "Summer Semester guidelines 2026", "Dean Academics", 2, "circular", "F.220(591)/114", "2026-05-08", "", "", "ALL", "ALL", IMS + " 08-05-2026", "NSUT_DeanAcad_Summer_Semester_Guidelines_2026-05-08.pdf", "Y", "posting date"),
 ("ACAD-ATT-2020", "Attendance rules (in-house activities, leave form)", "Academic Section", 2, "circular", "F.220(301)/Notice/2020", "2020-08-29", "", "", "ALL", "ALL", IMS + " 01-09-2020", "NSUT_Acad_Attendance_Rules_2020-08-29.pdf", "N", "printed date"),
 ("DEAN-ATT-2023", "Attendance guidelines (Annexure A = Cl. 11)", "Dean Academics", 2, "circular", "F.220(277)/Acad/Notice", "2023-08-16", "", "", "B.Tech", "ALL", IMS + " 17-08-2023", "NSUT_DeanAcad_Attendance_Guidelines_2023-08-16.pdf", "N", "printed date"),
 ("DEAN-ATT-2024", "Attendance guidelines 2024", "Dean Academics", 2, "circular", "F.220(277)/Acad/Notice", "2024-08-05", "", "", "B.Tech", "ALL", IMS + " 04-08-2024", "NSUT_DeanAcad_Attendance_Guidelines_2024-08-05.pdf", "N", "printed date"),
 ("ACAD-ATT-CLARIF-2024", "Clarification on attendance rule (no affidavits at ESE)", "Academic Section", 2, "circular", "F.220(57)/22", "2024-04-04", "", "", "ALL", "ALL", IMS + " 05-04-2024", "NSUT_Acad_Attendance_Rules_Clarification_2024-04-04.jpg", "Y", "posting date"),
 ("ACAD-BUNKING-2024", "Notification on mass bunking", "Academic Section", 2, "circular", "F.220(360)/849", "2024-08-16", "", "", "ALL", "ALL", IMS + " 16-08-2024", "NSUT_Acad_Mass_Bunking_Notification_2024-08-16.pdf", "Y", "posting date"),
 ("DEAN-ATT-NOTICE-2025", "Attendance notice: no special relaxation for re/late registration", "Dean Academic", 2, "circular", "F.220(312)/ShortAtt/2018/1234", "2025-09-09", "", "", "ALL", "ALL", IMS + " 09-09-2025", "NSUT_DeanAcad_Attendance_Notice_2025-09-09.jpg", "Y", "posting date"),
 ("ACAD-ATT-2026", "Notification regarding attendance", "Assistant Registrar, Academics", 2, "circular", "F.220(312)/ShortAtt/2026-27/1005", "2026-09-15", "", "", "ALL", "ALL", IMS + " 15-09-2026", "NSUT_Acad_Attendance_Notification_2026-09-15.pdf", "Y", "printed date 15/9/26 (VERIFIED)"),
 ("FEE-2023-24", "Annual fee structure for students admitted 2023-24", "Registrar / BoM", 2, "circular", "2023-24", "2023-05-18", "", "", "B.Tech", "2023", "https://drive.google.com/file/d/1gAikLgJZHKlcYdE645im6pss1IxeChyv", "NSUT_Annual_Fee_Structure_Admission_2023-24.pdf", "Y", "posting date"),
 ("FEE-2024-25", "Annual fee structure for students admitted 2024-25", "Registrar / BoM", 2, "circular", "F.220(287)/654", "2024-07-23", "", "", "B.Tech", "2024", "https://drive.google.com/file/d/16t5lmlN_aSglASvbBoIzbenEi7FDQPya", "NSUT_Annual_Fee_Structure_Admission_2024-25.pdf", "N", "printed date"),
 ("FEE-2025-26", "Annual fee structure for students admitted 2025-26", "Registrar / BoM", 2, "circular", "2025-26", "2025-07-01", "", "", "B.Tech", "2025", "https://drive.google.com/file/d/1uayccnPvMdwBCu_qrWvWpmAnmXQcodj3", "NSUT_Annual_Fee_Structure_Admission_2025-26.pdf", "Y", "approx. (not read)"),
 ("FEE-2026-27", "Annual fee structure for students admitted 2026-27", "Registrar / BoM", 2, "circular", "F.220(558)/AnnualFeeStructure/2025/147", "2026-05-14", "", "", "B.Tech", "2026", "https://drive.google.com/file/d/11iCdBponIqMugJsa_LPB75hS2zx6-MJ4", "NSUT_Annual_Fee_Structure_Admission_2026-27.pdf", "Y", "printed date"),
 ("ACAD-FEE-INST-2024", "Payment of fee in two instalments (2024-25 only)", "Academic Section", 2, "circular", "F.220(75)/fees-13/702", "2024-07-29", "2025-06-30", "", "B.Tech", "2024", IMS + " 29-07-2024", "NSUT_Acad_Fee_Two_Instalments_2024-07-29.pdf", "N", "posting date; effective_to assumed end of 2024-25"),
 ("ACAD-FEE-NOINST-2026", "No instalments for Annual University Fee", "Academic Section", 2, "circular", "F.220(558)/236", "2026-06-02", "", "", "B.Tech", "ALL", IMS + " 02-06-2026", "NSUT_Acad_Fee_Payment_No_Instalments_2026-06-02.pdf", "Y", "posting date"),
 ("ADM-FIRSTYEAR-2026", "Admissions-2026 circular: first-year fee and joining", "Chairman, Admissions-2026", 2, "circular", "2026", "2026-07-27", "", "", "B.Tech", "2026", "https://drive.google.com/file/d/1aZ_CX9PH9oHnN23BCMWtCH__HOtIyJoZ", "NSUT_Admissions_Circular_First_Year_2026-07-27.pdf", "N", "posting date"),
 ("TNP-POLICY-2024-25", "Placement Policy 2024-25", "Training & Placement Cell", 2, "regulation", "2024-25 final", "2024-07-01", "2025-06-30", "", "B.Tech", "ALL", "https://tnpnsut-files.s3.ap-south-1.amazonaws.com/Placement_Policy_2024_25_final_b6588b530d.pdf", "NSUT_TnP_Placement_Policy_2024-25.pdf", "N", "season start assumed; no later policy published"),
 ("CVSPK-RULES-2020", "CVSPK Scholarship and Incentive Rules 2020", "NSUT (CVSPK)", 1, "regulation", "2020", "2020-01-01", "", "", "B.Tech", "ALL", "https://drive.google.com/file/d/1RyYTumb56zTUToEjoivle-qD6iGcumsu", "NSUT_CVSPK_Scholarship_Incentive_Rules_2020.pdf", "N", "year only"),
 ("GNCTD-MCM-2023", "GNCTD e-District scholarship guidelines (posted by NSUT Academic Section)", "GNCTD SC/ST/OBC Dept (external)", 3, "notice", "2023", "2023-08-25", "", "", "ALL", "ALL", IMS + " 25-08-2023", "GNCTD_EDistrict_Scholarship_Guidelines_via_NSUT_2023.pdf", "N", "posting date"),
 ("HOSTEL-RULES-2024", "Hostel general rules", "Chief Warden", 2, "circular", "2024", "2024-07-03", "", "", "ALL", "ALL", "https://drive.google.com/file/d/17o8EH_-dUHECJvOgcpHFqSa8ZVl22jdq", "NSUT_Hostel_General_Rules_2024-07-03.pdf", "N", "file date"),
 ("HOSTEL-PROHIB-2026", "Hostel prohibited items notice", "Warden, Ramanujan/JC Bose Hostel", 3, "notice", "NSUT/Ramanujan Hostel/Adm/2026/03", "2026-08-19", "", "", "ALL", "ALL", "NSUT hostel notice board", "NSUT_Hostel_Prohibited_Items_2026-08-19.pdf", "N", "file date"),
 ("HOSTEL-MESS-2025-26", "Hostel and mess fee 2025-26", "Chief Warden", 2, "circular", "Order 429", "2025-05-09", "", "", "ALL", "ALL", "NSUT hostel notice board", "NSUT_Hostel_Mess_Fee_2025-26.pdf", "N", "printed date; text layer is poor OCR"),
 ("HOSTEL-MESS-EVEN-2025", "Hostel and mess fee, even semester 2025-26", "Chief Warden", 2, "circular", "Order 533", "2025-11-26", "", "", "ALL", "ALL", "NSUT hostel notice board", "NSUT_Hostel_Mess_Fee_Even_Sem_2025-11-26.pdf", "N", "file date"),
 ("HOSTEL-BH4-FEE-2026", "Hostel fee deadline notice", "Warden, Ramanujan Hostel", 3, "notice", "2026", "2026-08-12", "", "", "ALL", "ALL", "NSUT hostel notice board", "NSUT_Hostel_BH4_Fee_Deadline_2026-08-12.pdf", "N", "file date"),
 ("CAL-ODD-2026-27", "Academic calendar, odd semester 2026-27", "Academic Section", 2, "circular", "2026-27", "2026-07-20", "", "", "B.Tech", "ALL", IMS + " 20-07-2026", "NSUT_Academic_Calendar_Odd_2026-27.pdf", "Y", "posting date"),
 ("CAL-EVEN-2026", "Academic calendar, even semester 2026 (revised)", "Academic Section", 2, "circular", "No.1917", "2026-01-08", "", "", "B.Tech", "ALL", IMS + " 08-01-2026", "NSUT_Academic_Calendar_Even_2026_Revised.pdf", "N", "printed date; jumbled text layer"),
 ("CAL-EVEN-2026-ADD", "Addendum to even-semester calendar 2026", "Academic Section", 2, "circular", "Addendum", "2026-03-23", "", "CAL-EVEN-2026", "B.Tech", "ALL", IMS + " 2026-03-23", "NSUT_Academic_Calendar_Even_2026_Addendum_2026-03-23.pdf", "Y", "posting date"),
 ("CCC-SEM3-2025-26", "Course Coordination Committee list, B.Tech Sem 3 (NEP) 2025-26", "Academic Section", 3, "notice", "2025-26", "2025-07-01", "", "", "B.Tech", "2024", "NSUT Academic Section notice", "NSUT_CCC_BTech_Sem3_NEP_2025-26.pdf", "N", "approx."),
 ("CCC-SEM4-2024-25", "Course Coordination Committee list, B.Tech Sem 4 (NEP) 2024-25", "Academic Section", 3, "notice", "2024-25", "2025-01-01", "", "", "B.Tech", "2023", "NSUT Academic Section notice", "NSUT_CCC_BTech_Sem4_NEP_2024-25.pdf", "N", "approx."),
 ("CCC-SEM5-2025-26", "Course Coordination Committee list, B.Tech Sem 5 (NEP) 2025-26", "Academic Section", 3, "notice", "2025-26", "2025-07-01", "", "", "B.Tech", "2023", "NSUT Academic Section notice", "NSUT_CCC_BTech_Sem5_NEP_2025-26.pdf", "N", "approx."),
 ("COE-SUMMER-COURSES-2026", "Summer semester 2026 course list (Google Sheet export)", "Controller of Examinations", 2, "notice", "2026", "2026-05-12", "", "", "B.Tech", "ALL", "https://docs.google.com/spreadsheets/d/1lQrFzKYaxM0reHWHh9C3fDtQ7C5rvBXUO3vXWvqVP2o", "NSUT_CoE_Summer_Semester_Courses_2026.xlsx", "N", "posting date"),
]

# Corpus scope: standing policies (any date) + every notice dated 2026. Older notices were removed from data/documents.
KEEP = {
    # standing policies / regulations / rules
    "NSUT-BTECH-REG-2019", "NSUT-BTECH-RULES-2019", "NSUT-ORD-II-2019", "NSUT-ORD-II-GAZ-2020", "SENATE-SUMMER-2020",
    "COE-UFM-2025", "TNP-POLICY-2024-25", "CVSPK-RULES-2020", "HOSTEL-RULES-2024",
    # notices / circulars released in 2026
    "BOM-MAKEUP-2026", "DEAN-MAKEUP-GUIDE-2026", "DEAN-MAKEUP-NOTIF-2026", "ACAD-BACKLOG-MODES-2026", "DEAN-SUMMER-2026",
    "ACAD-ATT-2026", "FEE-2026-27", "ACAD-FEE-NOINST-2026", "ADM-FIRSTYEAR-2026", "HOSTEL-PROHIB-2026",
    "HOSTEL-BH4-FEE-2026", "CAL-ODD-2026-27", "CAL-EVEN-2026", "CAL-EVEN-2026-ADD", "COE-SUMMER-COURSES-2026",
}
D = [d for d in D if d[0] in KEEP]

RR_COLS = ["rule_id", "description", "parameter", "operator", "value", "scope_programmes", "scope_batches",
           "effective_from", "effective_to", "source_doc_id", "source_section", "verified"]
# rule_id, description, parameter, operator, value, programmes, batches, eff_from, eff_to, doc, section, verified
R = [
 ("ATT-MIN-01", "Minimum attendance (lectures+tutorials+practicals, per subject) needed to appear in MSE/ESE", "min_attendance_pct", ">=", "75", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 11.2 (PDF p.18)", "VERIFIED"),
 ("ATT-REL-01", "Dean Academics may relax attendance by up to 10 percentage points on documented grounds", "attendance_relaxation_pct", "<=", "10", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 11.3 (PDF p.18)", "VERIFIED"),
 ("ATT-REL-02", "Further relaxation up to 5 percentage points in exceptional circumstances", "attendance_extra_relaxation_pct", "<=", "5", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 11.4 (PDF p.18)", "VERIFIED"),
 ("ATT-REL-03", "Maximum number of attendance relaxations in the whole programme", "max_relaxations", "<=", "2", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 11.5 (PDF p.18)", "VERIFIED"),
 ("ATT-FLOOR-01", "Not permitted to appear in MSE/ESE if attendance is below this value even after relaxation", "attendance_floor_pct", ">=", "60", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 11.6 (PDF p.18)", "VERIFIED"),
 ("ATT-NOCONDONE-01", "No shortage-of-attendance condonation at MSE; no relaxation claims at ESE; below 75% = detained from ESE", "min_attendance_pct", ">=", "75", "ALL", "ALL", "2026-09-15", "", "ACAD-ATT-2026", "Para 1 (p.1, scanned)", "VERIFIED"),
 ("PASS-ESE-01", "Minimum share of ESE marks (theory and practical separately) to pass a course", "min_ese_pct", ">=", "30", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 12.7 (PDF p.19)", "VERIFIED"),
 ("PASS-GRADE-D-01", "Absolute grading (class size <= 30): minimum total marks for lowest passing grade D", "min_total_marks_pct_for_D", ">=", "35", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Table 5 (PDF p.15-16); Table 3 (p.14)", "REPORTED (D>=35 not re-read; O>=90..B>=54 VERIFIED)"),
 ("SUPP-01", "No supplementary examinations; failed course must be re-registered (as amended by Exam-Only Mode / make-up exam circulars)", "supplementary_allowed", "=", "false", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 12.3 (PDF p.19)", "VERIFIED"),
 ("PROMO-01", "Promotion odd->even semester has no restriction", "promotion_odd_to_even_restricted", "=", "false", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 12.1", "REPORTED"),
 ("DEGREE-CREDITS-01", "Credits to be earned for the B.Tech degree (out of 170 registered)", "min_credits_degree", ">=", "162", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 7.8 (PDF p.11); Cl. 15.1 (p.20)", "VERIFIED"),
 ("DEGREE-CGPA-01", "Minimum CGPA for award of B.Tech degree", "min_cgpa_degree", ">=", "5.00", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 15.1 (PDF p.20)", "VERIFIED"),
 ("HONOURS-CGPA-01", "Minimum CGPA for B.Tech (Honours)", "min_cgpa_honours", ">=", "8.50", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 7.9 / 15.4", "REPORTED"),
 ("DIV-FIRST-01", "Minimum CGPA for First Division", "min_cgpa_first_division", ">=", "6.50", "B.Tech", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 15", "REPORTED"),
 ("CGPA-PCT-01", "Percentage of marks = CGPA multiplied by 10", "cgpa_to_pct_multiplier", "=", "10", "ALL", "ALL", "2019-07-01", "", "NSUT-BTECH-REG-2019", "Cl. 9.7(d) (PDF p.17)", "VERIFIED"),
 ("SUMMER-MAXCOURSES-01", "Summer semester: max backlog/improvement courses (2026: 5 in total, at most 2 in Study Mode)", "summer_max_courses", "<=", "5", "ALL", "ALL", "2026-05-08", "", "DEAN-SUMMER-2026", "Para on course limit (scanned)", "REPORTED"),
 ("SUMMER-ATT-01", "Summer semester Study Mode: 75% attendance with no relaxation", "min_attendance_pct", ">=", "75", "ALL", "ALL", "2026-05-08", "", "DEAN-SUMMER-2026", "Attendance clause (scanned)", "REPORTED"),
 ("REREG-FEE-01", "Re-registration fee per subject in a regular semester (INR)", "reregistration_fee_inr", "=", "7000", "B.Tech", "2026+", "2026-05-14", "", "FEE-2026-27", "Cl. 13 (scanned)", "REPORTED"),
 ("SUMMER-FEE-SM-01", "Summer semester fee per paper, Study Mode (INR)", "summer_fee_study_mode_inr", "=", "14000", "ALL", "ALL", "2026-05-08", "", "DEAN-SUMMER-2026", "Fee clause (scanned)", "REPORTED"),
 ("SUMMER-FEE-EOM-01", "Summer semester fee per paper, Exam-Only Mode (INR)", "summer_fee_eom_inr", "=", "10000", "ALL", "ALL", "2026-05-08", "", "DEAN-SUMMER-2026", "Fee clause (scanned)", "REPORTED"),
 ("PLACE-DROP-01", "Final-year students may drop at most this many active backlogs for placement CGPA purposes", "max_dropped_backlogs", "<=", "2", "B.Tech", "ALL", "2024-07-01", "2025-06-30", "TNP-POLICY-2024-25", "Drop Subject Rules (PDF p.11)", "VERIFIED"),
 ("PLACE-CGPA-01", "No university-wide minimum CGPA for placement; each company sets its own", "univ_min_cgpa_placement", "=", "none", "B.Tech", "ALL", "2024-07-01", "2025-06-30", "TNP-POLICY-2024-25", "Eligibility (PDF p.4)", "VERIFIED"),
]


def write(path, cols, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)


def main():
    docs = Path(DATA / "documents")
    sr = []
    for (doc_id, title, issuer, lvl, typ, ver, eff, eff_to, sup, prog, bat, prov, fname, scanned, basis) in D:
        if not (docs / fname).exists():
            raise SystemExit(f"missing file {fname}")
        sr.append([doc_id, title, issuer, lvl, typ, ver, eff, eff_to, sup, prog, bat, prov, RETRIEVED, "N", fname, scanned, basis])
    ids = {r[0] for r in sr}
    assert len(ids) == len(sr), "duplicate doc_id"
    for r in R:
        assert r[9] in ids, f"rule {r[0]} cites unknown doc {r[9]}"
    write(DATA / "source_register.csv", SR_COLS, sr)
    write(DATA / "rule_registry.csv", RR_COLS, R)
    print(f"source_register.csv: {len(sr)} docs; rule_registry.csv: {len(R)} rules")


if __name__ == "__main__":
    main()

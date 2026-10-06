# Prompts used to produce the synthetic data (verbatim)

Model: claude-sonnet-5-5 / claude-opus-5-5 via Claude Code (the session switched models mid-way). No sampling parameters
are exposed by the tool, so temperature is unknown/default.

## Prompt 1: user's request (verbatim)

> Go through the pdf thoroughly. search and give all the university policy available for netaji subhas university of technology, dwarka (Main campus). After this generate the the fabricated data for atleast 30 students, 2 programmes, 2 batches and 6 courses. go through all the instructions regarding these. i want policy all the policies in pdf and it should be original. student data must be fabricated but use some real notations like roll number like 2023UITXXXX, etc.

## Prompt 2: delegated corpus-collection task

Sent to a sub-agent: collect ORIGINAL, publicly available NSUT policy PDFs (regulations, examination, attendance, fee,
placement, scholarship, hostel, calendars, scheme/course codes), download without rewriting, exclude any document with
real student names/roll numbers, report clause numbers and conflicts. (Full text is in the session transcript.)

## Prompt 3: data design brief (what the generator encodes)

> Fabricate at least 30 students, 2 programmes, 2 batches, 6+ courses in the Annex C schema. Use NSUT-style roll numbers
> (20NNU{IT|CS}NNNN). Use real NSUT course codes. Include deliberately: attendance exactly at the threshold; one class
> below it; a fail just under the pass mark; an absent result; a detained student; multiple backlogs; CGPA exactly at
> cut-offs found in the documents. Student IDs S1001-S1032 only (S9000-S9999 and JDG* are reserved for judges).

Because the data is produced by a seeded script (scripts/generate_students.py) rather than free-text LLM output, the
"prompt" for the rows themselves is the script plus the edge-case table inside it. Regenerate with
`python scripts/generate_students.py`.

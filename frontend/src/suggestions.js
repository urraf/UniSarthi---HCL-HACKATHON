// Suggested questions shown as chips in the chat. Only the QUESTIONS live here:
// clicking a chip sends it to the API like a typed question, and the answer is generated live.
export const GENERAL_QUESTIONS = [
  "What is the minimum attendance required for end-semester exams?",
  "Is there a supplementary exam if I fail a course?",
  "What is the summer semester fee per paper?",
  "What is the hostel fee deadline?",
];

// {course} is filled with a course the student really has records for
export const ATTENDANCE_QUESTIONS = [
  "What is my attendance in {course}?",
  "Am I eligible for the end-semester exam in {course}?",
];
export const RESULT_QUESTIONS = ["If I clear {course}, can I register for placements?"];
export const OTHER_PERSONAL = ["Am I eligible for campus placements?"];

// me = GET /me (attendance_courses, result_courses)
export function buildSuggestions(me) {
  const att = (me.attendance_courses || []).map((c) => c.course_name);
  const res = (me.result_courses || []).map((c) => c.course_name);
  const fill = (questions, names) => (names.length ? questions.map((q, i) => q.replace("{course}", names[i % names.length])) : []);
  return [...fill(ATTENDANCE_QUESTIONS, att), ...fill(RESULT_QUESTIONS, res), ...OTHER_PERSONAL, ...GENERAL_QUESTIONS];
}

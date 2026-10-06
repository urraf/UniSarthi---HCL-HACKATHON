// Suggested questions shown as chips in the chat. Only the QUESTIONS live here:
// clicking a chip sends it to the API like a typed question, and the answer is generated live.
// {course} is replaced with one of the logged-in student's own courses.
export const GENERAL_QUESTIONS = [
  "What is the minimum attendance required for end-semester exams?",
  "How do I apply for the supplementary exam?",
  "What CGPA do I need to register for placements?",
];

export const PERSONAL_QUESTIONS = [
  "What is my attendance in {course}?",
  "Am I eligible for the end-semester exam in {course}?",
  "Am I eligible for campus placements?",
  "If I pass the supplementary in {course}, will I be eligible for placement?",
];

// Fill in the student's courses (first course for the first question, and so on)
export function buildSuggestions(courses) {
  const names = courses.map((c) => c.course_name);
  const personal = names.length
    ? PERSONAL_QUESTIONS.map((q, i) => q.replace("{course}", names[i % names.length]))
    : [];
  return [...personal, ...GENERAL_QUESTIONS];
}

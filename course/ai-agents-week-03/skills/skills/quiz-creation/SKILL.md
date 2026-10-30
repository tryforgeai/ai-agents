---
name: quiz-creation
description: >-
  Builds a quiz of at least ten questions on a topic the user names. Use when
  the user asks to create a quiz, generate a quiz, or write quiz questions.
  Do NOT use for encyclopedia articles, short study summaries, or grading an
  existing exam.
version: "0.1.5"
---

# Quiz Creation

## When to use

Reinforce the trigger and name explicit negatives (teach students: bound I):

- Use when: the user asks to create a quiz, generate a quiz, or write quiz questions.
- Do NOT use for: encyclopedia articles, short study summaries, or grading an existing exam. 

## Procedure

Checklist-carrier pattern — use `{placeholder}` for per-request inputs:

- [ ] Step 1: Extract `{topic}` and any requested question count or difficulty from the user message. Specify the programming language version when relevant.
- [ ] Step 2: Draft at least 10 questions on `{topic}` (or the requested count, if higher), mixing recall and reasoning.
- [ ] Step 3: Give each single-choice question exactly one correct answer and plausible distractors. For open-ended questions, provide a model answer. Clearly label any multiple-answer questions.
- [ ] Step 4: Prepare an answer key, numbered to match the questions, with a brief explanation for each answer.
- [ ] Step 5: Check every option independently. Confirm that each single-choice question has exactly one correct option and that the answer key and explanation agree with it.
- [ ] Step 6: For questions involving code, use an available execution tool to verify syntax and output. If execution is unavailable, review the code carefully and do not claim it was executed.
- [ ] Step 7: For questions asking for exact runtime output, ensure that exactly one option matches the actual output, including relevant whitespace and punctuation, and that every distractor is incorrect. Distinguish printed output from value representations and type labels; do not add quotation marks unless they are printed.
- [ ] Step 8: For loop-count questions, provide enough context to determine the iteration count: the iterable or relevant initial state, variable updates, and termination conditions. State assumptions about early exits when needed.
- [ ] Step 9: Distinguish values from types in all options. Fix ambiguous labels and duplicate or equivalent correct options.
- [ ] Step 10: Review factual accuracy, terminology, and wording. Fix any remaining errors, then recheck each revised question and its answer key before presenting it.
- [ ] Step 11: Present the checked quiz, followed by the matching answer key and explanations. Do not claim execution-based verification unless it occurred.

Do not bake one example instance (e.g. a specific theorem name) into the
procedure. Do not report "done" until every box is ticked.

## Done when

- The quiz contains at least 10 questions on the requested topic,
  or the requested count if higher.
- Every single-choice question has exactly one correct option.
- Multiple-answer questions are clearly labeled, and open-ended
  questions include model answers.
- The quiz ends with a complete numbered answer key and a brief
  explanation for each answer.
- Each answer and explanation agrees with its question and options.
- All questions have been checked for factual accuracy, clear wording,
  and precise terminology.
- Code examples have been checked for syntax and expected output.
  Do not claim code was executed unless it actually was.
- Every item in the Procedure checklist has been completed.
- For exact-output single-choice questions, exactly one option matches the
  actual runtime output; every distractor is incorrect.
- Loop-count questions provide enough context and assumptions to determine
  the number of iterations unambiguously.
- Options clearly distinguish values, types, and printed output; ambiguous
  labels and equivalent correct options have been corrected before delivery.

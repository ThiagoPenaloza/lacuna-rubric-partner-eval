# Provisional hypotheses for the micro1 eval

These options depend on Thiago's hands-on experience; they are evaluation hypotheses, not failures already observed. In all of them the set can use public or synthetic tasks, reviewed answer keys, and verifiable criteria.

1. **Software: find and fix real implementation bugs.** If Thiago has development experience, present small repositories with reproducible bugs and ask for a patch that fixes them without breaking specified behavior. Grading: run hidden tests focused on the bug and on regressions, and check that the diff changes the expected behavior. It matters because plausible patches may not fix the defect or may introduce regressions. Validity risk: tests may favor one implementation and miss correct alternative solutions; synthetic bugs may not represent real work.

2. **Grader/rubric: tell clear criteria from ambiguous ones.** If Thiago has created or evaluated rubrics, provide answers to professional cases and ask for an evaluation against a rubric, including structured justifications. Grading: compare labels and evidence with human-adjudicated decisions, also testing borderline answers and paraphrases. It matters because inconsistent evaluations make eval results unreliable. Validity risk: human adjudication may reflect disagreements or biases and not establish a single truth.

3. **A distinct option — spreadsheets: turn requirements into correct formulas.** If Thiago works with spreadsheets, present a small table and calculation/grouping requirements and ask for formulas or results. Grading: compare results and formulas with reference outputs in normal and edge cases, including empty cells and duplicates. It matters because quiet aggregation errors can distort decisions. Validity risk: synthetic examples may understate differences between real tools and spreadsheet conventions.

Before choosing, ask Thiago which of these areas matches his experience and which concrete errors he has already seen. Then compare relevance, automatic grading, cost of preparing tasks, and feasibility before the deadline. No option should be closed without that conversation and without experiments.

## Thiago's decision

Thiago chose option 2, evaluating LLMs around rubrics/graders. The first specification (`docs/EVAL_SPEC.md`) framed the model as a rubric-based answer grader. The final direction (`docs/EVAL_SPEC_V2.md`) frames it as a rubric-writing partner, with six synthetic tasks and a JSON contract. The answer keys still require human review before freezing.

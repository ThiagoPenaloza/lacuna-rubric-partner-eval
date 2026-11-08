# Short description

This eval tests LLMs used as partners for writing and reviewing rubrics. Across six synthetic tasks, the model must find omitted requirements, ask for context when there is none, turn ambiguous wording into an observable criterion, make generic feedback actionable, spell out code behaviors, and respect decisions already accepted in an iteration.

The output is JSON with the finding, literal evidence, impact, question, suggestion, and confidence. The metagrader separates protocol from content and includes negative mutations for denied gaps, fabricated evidence, inverted deadlines, code continuity, and paraphrases (24 tests). A free local run of `qwen2.5:7b` on the English tasks passed the protocol on 6/6 tasks and the strict content proxy on 2/6, with one attempt per task. The final semantic decision stays human.

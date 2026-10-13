---
name: discover
description: Open, run and close a sliceworks research round - fix the questions from SPARK.md or the feedback register, dispatch read-only researchers one question each, fill the claim register with sources and verification verdicts, run the register lint, freeze the round and hand its open questions to Decide. Use when the user says "research this", "open a round", "verify these assumptions", "what do we know about", "discover", or when a milestone enters discovering.
license: Apache-2.0
metadata:
  source: glotyuids/sliceworks
  version: 0.5.0
---

# Discover: run a research round

Method: `method/13-discover-and-decide.md`. Templates: `${CLAUDE_PLUGIN_ROOT}/templates/round/`.

1. **Open.** Next round number under `SW_ROUNDS_DIR`; copy the four templates; write `questions.md` from `SPARK.md`'s riskiest assumptions, the open `Q` entries that need evidence, or the feedback register. Each question names what it serves. Register each question as a `claim` or `experiment` row in `FEATURES.json` only once a claim exists; do not pre-create rows.
2. **Research.** One `researcher` subagent per question, read-only, with the question, the round directory and the rule: claims with sources, confidence and a verdict, nothing else. Record every source in `sources.md`. Prefer primary sources; mark secondary ones.
3. **Register.** Merge the researchers' claims into `register.md` (`C-<n>-<k>`); every claim has a source id and a verdict; refuted claims stay in the register with their refutation.
4. **Experiments.** For a riskiest assumption no source can settle, write an experiment row (measurable outcome, budget, deadline) instead of a claim.
5. **Synthesize.** `design.md`: answers by question, consequences for the design, the open questions handed to Decide with a recommended default each.
6. **Lint and close.** Run the register lint (every claim has source and verdict; no verdict older than its source). Create `.closed`. Add the round to `INDEX.md` as evidence. Hand the open questions to the `decide` skill.

Never edit a closed round; open a new one.

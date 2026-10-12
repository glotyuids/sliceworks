# Release <id> · <milestone> · <environment>

<!-- sliceworks 0.2.0. The release slice's checklist (method chapter 15). Each step is a FEATURES.json row of kind release; script steps carry a command, human steps carry human_act. -->

| step | check or act | row | result |
|---|---|---|---|
| version and changelog | tag exists; changelog names every merged slice since the last release | | |
| migrations and rollback | plan lists every numbered artifact; rollback rehearsed in isolated | | |
| flags and configuration | every flag has a default and an owner | | |
| runbook | covers the new surfaces; incident path named | | |
| T5 rehearsal | deploy to isolated; smoke and scenario subset green; log path | | |
| security review | threat models current; named-risk findings closed | | |
| approvals | D entries for money, legal, data | | |
| notice | on-call (or the owner, in the lite profile) notified of the window and the rollback trigger | | |
| push | the one push script | | |
| deploy | human act per environment; prepared command; verification by name; canary first where the environment offers one | | |
| post-release verification | probes green for <window> | | |
| announcement | human act | | |

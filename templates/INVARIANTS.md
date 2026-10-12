# Invariants

<!-- sliceworks 0.2.0. One line each. The code reviewer checks every finding against this list; the named-risk reviewer treats each as a question to answer with executed evidence. Add the binding documents (constitution, decision records, product contract) at the end. -->

- <tenant or user scoping rule: every read and write passes through the scope helper; the actor is the authenticated user id>
- <fail-closed rule for private data: no public URL, per-request rights check, revocation closes access before any sync>
- <no silent averaging or hidden ranking; unknown is never a failure>
- <generated claims carry provenance to their source>
- <tests never removed or weakened; a skipped check is NOT_RUN>

Binding documents: <paths>

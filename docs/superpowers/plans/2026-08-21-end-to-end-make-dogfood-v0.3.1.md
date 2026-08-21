# End-to-End Make Dogfood v0.3.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finalize the v0.3 dogfood with evidence from the actual Figma Make artifact and three completed correction passes.

**Architecture:** Add an evidence-only v0.3.1 directory while preserving v0.3 and all canonical product and Skill files. Separate historical source-readback evidence, fresh artifact existence readback, residual prototype limitations, and production non-claims.

**Tech Stack:** Markdown evidence, Python validators/unittest/py_compile, Git.

**Spec:** `C:/Users/tjdwo/.codex/attachments/3ecd815c-d0ee-45ef-a632-2ad1ccb0ca61/pasted-text.txt`

## Global Constraints

- Base dogfood commit is `dc3ee928d3ab38a8badd2a09e41e87a48eb2069a`.
- Canonical definition remains revision 44 and digest `2ffc3d304830327516f85e39df8c2be2800eda62568eaec45001f393379f07d1`.
- Do not modify Product Definition, Figma Design, Skill, validator, schema, taxonomy, state contract, or stable-ID semantics.
- Make is audited against the approved authority; it never becomes authority.

---

### Task 1: Preserve Make evidence

**Files:** Create the nine required files under `evals/end-to-end-v0.3.1/`.

- [x] Record exact inputs and authority order.
- [x] Preserve initial 5/7/1 drift counts and correction convergence.
- [x] Separate verified prototype observations, residual minor findings, and production non-claims.

### Task 2: Verify frozen contracts

**Files:** No source modifications.

- [x] Run unittest, both validators, and Python compile checks.
- [x] Compare frozen blobs against `0c5048f336ac9ba028d066a48c9ca60e4b85f5a8`.
- [x] Confirm v0.3 historical evidence and canonical product files are unchanged.

### Task 3: Publish evidence

**Files:** Stage only the plan and `evals/end-to-end-v0.3.1/`.

- [x] Inspect staged scope and commit with the prescribed message.
- [x] Push to remote `main` and read back required evidence paths.

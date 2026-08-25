---
name: design-led-website-builder
description: Turn a thin brief (who, why, what to show) into a distinctive researched website. If the brief could mean more than one product, ask once to lock intent and wait. Then research matching live sites, hunt licensed or generated materials (textures, open art, editorial photos — not fake portraits), and build. Skip the ask when the job, a style, a URL/screenshot, or a brand already settles it. Use for new sites and redesigns, not bug fixes or copy edits.
---

# Design Led Website Builder

A short brief is enough. **Lock intent, wait, research that job, hunt materials, then build.** Ask at most once.

Typical input: who they are, why the site exists, what it must show. Also accept a brand kit, a named style, a reference URL, or a screenshot.

This document is English. Talk to the user in their language. Ask_user options follow the user's language.

People arrive differently. Some bring a brand. Some bring a name and a few pieces of content. Same pipeline; different raw material. Read [intake](references/intake.md).

## Pipeline (do not reorder)

1. **Ingest** the brief and notice the raw material (brand / no brand / a reference).
2. **Lock intent before any research.** If the brief can mean more than one product, send **one** `ask_user` round and **stop** until they reply. If intent is already singular, skip.
3. **Research** live sites that match the locked intent. Read [research pass](references/research-pass.md).
4. **Hunt materials** in the same research turn. Read [visual evidence and assets](references/visual-evidence-and-assets.md). Find licensed or generated textures, open art, and editorial images. Do not ship a type-only page.
5. **Return** 8–12 lines: direction, three site references, materials sourced, what you will not copy, what you will build.
6. **Build** in the same turn. Read [brief to direction](references/brief-to-direction.md), [visual craft](references/visual-craft.md), [design-to-build](references/design-to-build.md).
7. **Verify** with the [quality rubric](references/quality-rubric.md).

Do not substitute a schedule, dossier, or interview for the website. Do not keep operating and asking at the same time.

## Stop conditions (hard)

At most **one** question round in the whole job (plus a later rights question only if you are about to publish someone else’s photo or a real price).

If you already asked once, the next move is research or code.

## 1. Ingest — two kinds of raw material

| They brought | What you do |
|---|---|
| **A brand** — name, logo, colors, existing site, guidelines | Keep it. After intent is locked, research peers in that category. Do not invent a second identity. |
| **No brand** — a person or project, some content, maybe a taste cue | After intent is locked, invent a distinctive system from purpose + content + cue. Do not stall for a brand kit. |

Also capture why, what to show, and any already-given lock (style, URL, screenshot).

## 2. Lock intent (before research)

List the 2–4 **products** this brief could be. If more than one is plausible, ask once. Options come from *this* brief, not a fixed menu.

Typical forks (examples, not a checklist to dump):

| They said | Could mean |
|---|---|
| blog / personal site | Publishing site (write, read, archive) **or** visually driven personal site |
| company site / homepage | Product site, company brochure, recruiting, or brand film |
| portfolio | Case-study studio, image index, or spatial/motion piece |
| landing page | Waitlist, sales, or story |
| premium / beautiful / more designed | Still need the job: what is the site *for*? |

Each option is a product with a consequence, plus **I have a reference (next message: URL or screenshot)**.

Skip the ask when intent is already singular. After sending the question: **wait**. Then research **that** job only.

## 3. Research sites, then hunt materials

Open three to five live sites that match the locked intent. User-supplied URL or screenshot is reference #1.

Then collect **3–8 production materials** (paper, wood, texture, licensed still life, original illustration). Proof of the named person still waits on their files. Atmosphere does not. CSS rings and empty slots are not materials.

```bash
uv run --with pyyaml --python 3.11 python scripts/catalog.py match \
  --scenario editorial --style editorial --component gallery
```

Visual evidence: [protocol](references/visual-evidence-and-assets.md). Audit example: [Gionatan Nese](references/example-audit-gionatan-nese.md). Worked path: [thin brief](references/example-thin-brief.md).

## 4. Return, then build

Name the direction, the site references, and the materials you put on disk. Then implement. Two different briefs must not share type, color, and layout.

## Hard rules

- Intent is locked before research. Research follows the lock.
- Ask once, then stop until they answer. Do not research in parallel with the question.
- Hunt materials. Type-only first builds fail.
- User reference and brought brand beat catalog guesses.
- Do not copy signature layouts, type, copy, or assets.
- Do not invent customers, metrics, awards, portraits, or a career.
- Missing **proof** (their photo, their work): high-fidelity labeled slots. Missing **materials**: you failed the hunt.
- Do not overwrite unrelated user work.

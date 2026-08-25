# Design-to-build playbook

Use this **after** the intent lock and the research return. It exists to stop a good direction from becoming arbitrary components.

Do not use this file as an excuse to skip research. Do not use it to write a schedule.

## Name the delivery level

- Concept prototype: art direction and representative states; some content may be pending.
- Functional prototype: primary flows and responsive behavior; some integrations mocked.
- Production implementation: real content and data, failure states, repo release requirements.

When the user says “build the site,” infer the highest level the repo and inputs support, disclose gaps, and implement. A thin brief plus researched placeholders is enough for a presentation-ready first site.

## Internal contract (do not dump on the user)

Hold these six decisions in working notes:

| Input | Decision |
|---|---|
| Purpose | audience, primary action, belief change, success signal |
| Taste | emotional position, visual language, anti-direction (from research) |
| Content | message order, proof, media, components, missing material |
| Constraints | framework, browsers, rights, maintenance, accessibility |
| Research | principles, evidence, non-copy boundary |
| Quality | acceptance criteria and release gates |

Save a durable dossier only when the user asked for one, or the work is a multi-handoff Level 2–3 build. Small sites keep this in the conversation. The [AI research dossier](example-dossier-ai-research.yaml) is an advanced fixture, not the default artifact.

## Content path

For each page or major section:

| Audience question | Message | Proof | Component | Desired action |
|---|---|---|---|---|
| What is this? | category and value | work, product, or plain explanation | hero | continue |
| Why believe it? | differentiated claim | case, metric, demo — only if real | proof | inspect |
| Is it for me? | audience / use | workflow or outcome | use-case or selected work | identify |
| What now? | clear next step | contact, book, buy, inquire | primary action | act |

Do not start from a fashionable section kit. Reorder or drop anything that does not answer a real question.

## System before components

Establish rules, then multiply:

- type roles, fluid scale, measure, line height;
- container widths, columns, gutters, responsive changes;
- spacing rhythm;
- surface, border, radius, shadow;
- color roles and contrast;
- media ratios and crops;
- interaction states;
- motion durations, easing, sequencing.

Prefer semantic tokens. Follow [visual craft](visual-craft.md).

For each consequential component: semantic role, content limits, desktop/mobile composition, states (including focus), input methods, motion and reduced-motion, fallback.

Separate reusable chrome from one-off art-directed sections. Premature abstraction erases identity.

## Experience ceiling

- Level 0 — static: hierarchy and responsive layout.
- Level 1 — feedback: hover, focus, disclosure, restrained reveals.
- Level 2 — narrative motion: coordinated sections, route continuity, product demonstration.
- Level 3 — immersive: WebGL, 3D, shaders, canvas, sound, cinematic media.

When research says the identity is Level 2 or 3, spike that effect early and compare a simpler alternative in the browser. Simplify only after evidence. Fallbacks preserve access; they do not cap the primary experience.

## Asset manifest

| Asset | Role | Status and replacement brief | Origin, provenance, rights | Format | Loading | Fallback |
|---|---|---|---|---|---|---|
| image, video, font, model | proof / explanation / atmosphere / identity | approved, placeholder, or pending | source, creator/tool, license | variants | eager / deferred / user | text, poster, still |

Route missing media through [visual evidence and assets](visual-evidence-and-assets.md). Generated media must never substitute for factual proof. Placeholders are presentation-template slots, not gray boxes.

## Vertical slice (first implementation)

Prove the system with one slice before cloning it across pages:

1. semantic content path and working navigation;
2. first viewport that passes the three-second test;
3. the signature visual or interaction at convincing fidelity;
4. one real content or proof section;
5. primary action;
6. tokens derived from the slice;
7. desktop, ~390px, keyboard, reduced-motion, loading, failure.

Then extend. Keep new dependencies justified:

- behavior they uniquely enable;
- why the current stack is insufficient;
- bundle, SSR/hydration, cleanup, reduced-motion, license.

Reuse installed libraries. Do not switch frameworks to imitate a reference.

## Durable dossier (optional, rare)

Only for complex handoffs or Level 2–3 work. Validate with:

```bash
uv run --with pyyaml --python 3.11 python scripts/validate_dossier.py \
  references/example-dossier-ai-research.yaml
```

The matching [reference pass](example-reference-pass-ai-research.md) and [vertical-slice fixture](../assets/e2e-fixture/index.html) are fixtures. Do not copy the fixture’s visual language onto a different brief.

Run fixture browser checks from the skill root (Playwright is ephemeral; the user’s project dependencies stay unchanged):

```bash
uv run --with pyyaml --with playwright --python 3.11 python \
  scripts/with_server.py \
  --server "python -m http.server 4173 --directory assets/e2e-fixture" \
  --port 4173 -- python scripts/test_vertical_slice.py
```

```bash
uv run --with pyyaml --with playwright --with axe-playwright-python --python 3.11 python \
  scripts/with_server.py \
  --server "python -m http.server 4173 --directory assets/e2e-fixture" \
  --port 4173 -- python scripts/audit_vertical_slice.py
```

```bash
uv run --with pyyaml --python 3.11 python \
  scripts/with_server.py \
  --server "python -m http.server 4173 --directory assets/e2e-fixture" \
  --port 4173 -- python scripts/check_lighthouse.py
```

Do not treat this fixture’s Lighthouse numbers as production budgets.

Before handing off changes to this skill package:

```bash
uv run --with pyyaml --python 3.11 python scripts/validate_skill.py
```

## Handoff

Make these traceable, briefly:

- chosen direction and anti-direction;
- references used and non-copy boundary;
- tokens and exceptional art-directed rules;
- asset provenance and unresolved rights;
- what was verified;
- production gaps and the next highest-value improvement.

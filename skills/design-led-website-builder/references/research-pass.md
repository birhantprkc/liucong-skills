# Research pass

Do not start this pass until intent is locked. If you sent `ask_user`, **do not browse, catalog, or keep asking** until the user answers. Researching in parallel with the question is how you end up in the wrong gallery.

## Why this step exists

Short briefs do not contain a visual language. Live craft does. Skipping research yields guesses. Researching the wrong job yields a mismatch (blog themes for a visual site, spectacle sites for a publishing site, product landings for a company intro). This pass changes the build, then stops.

## Match research to intent

| Locked intent | Look for | Do not lead with |
|---|---|---|
| Content / blog / notes / column | Strong publications: reading measure, index, typography, archival clarity | Portfolio spectacle, 3D heroes |
| Visual personal or brand site | High-craft first viewports: crop, type as image, distinctive material | Post-list blog themes |
| Company intro | Clear business lines, proof, contact | Product-SaaS landings, award spectacle |
| Product site | Demo, features, conversion path | Brochure about-pages |
| Case-study portfolio | Written cases with work | Pure image dumps, or 3D if they wanted cases |
| Image / spatial portfolio | Crop, index, or scene — as locked | Long case-study blogs |
| They pasted a URL or screenshot | That site first, then 1–2 peers in the same job | A fresh unrelated search |
| They brought a brand | Peers in that category; their existing site | A new identity |
| They brought no brand | Category craft for the locked job + cues in the brief | A biography search that delays the build |

If a name search finds no brand or studio, that is normal. Research the job, then build from what they gave.

## User-supplied reference (highest priority)

If they pasted a URL, a screenshot, or “like this site”:

1. That site (or frame) is reference #1.
2. Extract 3–5 principles: hierarchy, crop, type role, density, motion purpose, first-screen job.
3. Open one or two other high-craft sites in the same job so you do not clone the signature.
4. Adapt. Do not reproduce distinctive layout, type, illustration, or copy.

A screenshot is enough. You restyle by building, not by asking them to edit the screenshot.

## Quality bar (any job)

Open sites you would defend for *this* intent. If a first viewport is a theme demo, a template marketplace, or unrelated to the lock, discard it and pick another. Three strong matches beat fifteen weak ones.

## Depth

| Situation | Depth |
|---|---|
| Default | 3 live first-viewports you would defend for the locked intent |
| User named a site / sent a screenshot | Forensic-lite on that, plus 1–2 peers |
| Signature motion / 3D / canvas in the brief | [Audit protocol](site-audit-protocol.md); example [Gionatan Nese](example-audit-gionatan-nese.md) |

Never zero. Never ten tabs.

## Form the query

Map the **lock** onto [taxonomy](design-taxonomy.md) axes, then:

```bash
uv run --with pyyaml --python 3.11 python scripts/catalog.py match \
  --scenario editorial --style editorial --component gallery
```

Examples: publishing → `editorial` + long-form; visual portfolio → `portfolio` + the style they locked; cafe → `hospitality`. Pick at least two source types when possible, then leave the catalog. Open live sites.

## What to open

1. State the design question in terms of the lock (“how does a small publication keep reading first?” vs “how does a personal site hit hard in the first screen?”).
2. Load the public page. Record URL, date, viewport.
3. Capture the settled first viewport. Follow [visual evidence](visual-evidence-and-assets.md).
4. Keep it only if it matches the lock and is actually good.
5. Note implementation only when it changes the build.

## Evidence labels

observed / detected / source-claimed / inferred / unknown.

## Internal matrix (do not dump on the user)

| Reference | Relevant principle | Evidence | Adaptation | Do not copy |
|---|---|---|---|---|
| Site or frame | What solves this brief | observed / … | How the new site uses it | Signature layout, type, copy, assets |

## Return format

8–12 lines, then build in the same turn:

1. Locked intent + direction, and why it fits.
2. Three URLs (or “your screenshot + two peers”) and one principle each.
3. Will not copy.
4. Will build.
5. Materials on disk (3–8 files: what, license, role).
6. Need from you: **none**, unless a rights/fact blocker for *proof* (their face, their prices).

## Done enough

- intent is locked;
- three defensible first-viewports seen for that intent;
- direction and anti-direction stated;
- material pass done: 3–8 licensed or generated files on disk — see [visual evidence and assets](visual-evidence-and-assets.md);
- proof gaps labeled; atmosphere not waiting on the user;
- no further taste questions.

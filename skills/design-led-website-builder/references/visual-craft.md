# Visual craft

Read this before writing UI. Research chooses the direction; this file keeps the first build from looking like a template.

## First viewport

In three seconds the first screen must answer:

1. Who is this for / whose site is this?
2. What is the offer or body of work?
3. What should I do next?

If the hero could be swapped onto another company by changing three words, it is not done.

## Design system first

Define tokens, then compose. Do not sprinkle hex in components.

- **Color:** ≤5 total (field, ink, muted, one accent, one signal). Neutrals own most of the surface. Accent is for action and emphasis, not every card.
- **Type:** ≤2 families. Display has a job; body has a measure (~60–75ch). Fluid size with `clamp`. Line-height ~1.05–1.2 for display, 1.45–1.65 for body.
- **Space:** 4/8 scale. Section rhythm larger than card padding. Align to a real grid.
- **Radius / shadow:** one radius scale, concentric (outer ≈ inner + padding). One quiet shadow recipe or none.
- **Motion:** one easing family, short feedback (150–250ms), longer only for a signature sequence. Respect `prefers-reduced-motion`.

Name tokens by role (`--bg`, `--ink`, `--accent`), not by hue.

## Anti-slop (hard fail)

Do not ship these unless the researched direction *and* the user’s identity specifically demand them:

- purple / violet gradients, aurora blobs, glassmorphism soup;
- generic Inter + blue button on white as the whole identity;
- emoji as icons or headings;
- equal-radius card grids with random stock faces and lorem;
- fake 3D orbs, circuit boards, or “AI neural” decoration;
- gray boxes where an image-led section should be;
- type-only heroes with CSS rings/radars standing in for paper, wood, food, or work;
- “Welcome to our website” / “We are passionate about…” filler;
- copied Awwwards signature layouts.

The TRACE/WORK fixture in this skill is an **acceptance test**, not a look to clone. A cafe, a law firm, and an illustrator must not share its paper-and-evidence-rail language.

## This brief must not look like the last one

Two people must not get the same site with the name swapped.

Derive the system from *this* brief’s materials:

- a woodworker → wood grain, tool steel, paper labels, not a writer’s serif magazine;
- a writer → measure, ink, one display face, not a photographer’s full-bleed grid;
- wood / restraint / paper → warm field, quiet type, visible fiber, almost no chrome;
- a 3D artist → spatial layer + readable list, not the woodworker’s craft site.

If you cannot say in one sentence how this site’s type, color, and first crop differ from a generic personal blog *and* from the previous build, change them before writing more UI.

## Match the locked intent

If they wanted a **publishing site**, the first screen should read: a piece, an index, a reason to stay. Do not dress a blog as a cinematic portfolio.

If they wanted **visual impact**, the first screen should hit as an object or a statement. Do not park “Latest posts” on it.

Either way, quality is required — a weak theme demo is not “matching intent.”

## Make it specific to this brief

Pull identity from the content you were given:

- **Work** (art, photos, dishes, buildings) should be large. UI gets out of the way.
- **Product** should be shown doing the job, not illustrated as a metaphor.
- **Place** should use interiors, maps, hours — atmosphere is evidence.
- **Expertise** should use readable claims and real credentials, not gradients of trust.
- **Event** should put date, venue, and entry on the first screen.

If the user gave six works, the site is an edited exhibition, not a feature-card layout with those works stuffed in.

## Type recipes (pick one)

| Direction | Display | Body | Notes |
|---|---|---|---|
| Editorial craft | Serif with real italics | Grotesk or the same serif at small size | Captions and indexes matter |
| Quiet authority | Restrained serif | Grotesk | Avoid theatrical weights |
| Warm hospitality | Human serif | Plain sans | Menu and hours stay san-serif-clear |
| Editorial product | Grotesk, tight tracking on claims | Grotesk | Optional serif only for long proof |
| Identity-first event | One loud face | One boring face for facts | Facts must outrun the loud face |
| Spatial / cinematic | Compact UI grotesk | Same | Type is interface, not decoration |

Load only the weights you use. Check language coverage (Chinese, Latin, numerals) before committing.

## Color recipes (pick one)

Build from the work or the place when they exist. Otherwise:

- paper + ink + one mineral accent (editorial);
- warm white + terracotta + dark wood (hospitality);
- near-black + bone + one metal line (luxury / wine);
- cool gray field + one analytic blue (product, not neon);
- high-contrast ink on newsprint (brutalist / event);
- accessible warm field + strong action color (nonprofit).

Never default to purple, teal-on-dark glass, or pure `#000` on `#fff` for large body text. Soft ink on soft paper reads more expensive.

## Composition

Match content relationships, not fashion:

- one primary column with a rail for proof or booking;
- large image / small caption (portfolios, hospitality);
- split: statement | object;
- index of cases, not a bento of unrelated tiles;
- long-form reading when the product *is* text.

Bento is for heterogeneous summaries. It is not a default design system.

Mobile (~390px): single column, no horizontal overflow, tap targets ≥44px, same information — not a chopped desktop.

## Imagery

Follow [visual evidence and assets](visual-evidence-and-assets.md). Craft rules:

- the first viewport uses a real material (texture, licensed still, generated atmosphere, or the user’s work);
- real work, product, place, or people whenever you have them;
- generated or licensed media for illustrative materials; never as a fake portrait or fake client;
- proof gaps are labeled high-fidelity slots at the final crop — not a reason to skip materials;
- CSS/SVG ornament is not a substitute for paper, wood, or photography;
- one crop language per site (e.g. always 4:5 work, 16:10 interiors);
- descriptive `alt`; no “image1”.

## Interaction

Every control has hover / focus / active / disabled as relevant. Primary action is visible without hunting. Forms: labels, errors next to fields, success you can read. Do not hijack scroll unless the researched signature requires it, and then provide a usable reduced-motion path.

## Implementation notes

- Inspect the repo first. Reuse existing tokens, components, and stack.
- Prefer CSS, then the already-installed motion library, then a new dependency with a recorded reason.
- Semantic HTML: one `h1`, landmarks, skip link, visible focus.
- If the environment is React + Tailwind, encode tokens in `@theme` and avoid ad-hoc hex in JSX.

## Done when

- First viewport passes the three-second test.
- The site could not be mistaken for a different category’s template.
- The user’s listed content is all on the page, at presentation fidelity.
- Mobile does not overflow; keyboard can complete the primary path.
- No gray boxes, no fake proof, no unresearched purple gradient.

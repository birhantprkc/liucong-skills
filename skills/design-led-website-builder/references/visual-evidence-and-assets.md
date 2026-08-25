# Visual evidence and image asset protocol

Use this protocol when reference analysis depends on page appearance or when the planned website needs screenshots, photography, illustration, diagrams, textures, or other image assets.

**Hunt is not optional.** A type-only site with CSS ornament is a failed hunt, not a careful rights decision. Missing user photography blocks **proof**, not **materials**.

## Material pass (required)

Lock intent, then hunt materials before you write the page. Do not wait for the user to upload atmosphere. Do not ask whether to look.

| Job | What it is | Source |
|---|---|---|
| **Proof** | This person, their work, their cafe, their product UI, a real price | User files, or a labeled high-fidelity slot waiting on them |
| **Materials** | Paper, wood, grain, ink, landscape, still life, abstract art, texture, licensed editorial photo that is *not* claiming to be the subject | You go get these. Now. |

Collect **3–8 files on disk**, matched to the direction:

- wood / paper / restraint → washi, grain, a cut log, ink on paper
- food / hospitality → dishes, interiors, linen — licensed, not “this is their restaurant”
- technical writer → desks, hardware, paper notes, diagrams you author — not a fake portrait
- illustrator without files → generated or licensed analog-print studies at the final crop, labeled as stand-ins

Download locally. Record URL, creator, license, attribution. Do not hotlink.

Starting points (verify the **asset page**, not the search thumbnail): [Openverse](https://openverse.org/), [Wikimedia Commons](https://commons.wikimedia.org/), [Unsplash License](https://unsplash.com/license), [Pexels License](https://www.pexels.com/legal-pages/license/). Generation is fine for original texture and atmosphere — never for a fake photo of the named person.

Hard fails: type-only hero; CSS/SVG rings or radars standing in for photography; gray boxes; stock faces as the user; “we’ll add images later” as the first delivery. A diagram may be the signature only if the rest of the page still has material.

Do not put “find stock vs wait for uploads” on `ask_user`.

## Keep two jobs separate

### Reference evidence

A screenshot of a reference site is evidence for understanding composition, hierarchy, state, crop, interaction, and art direction. It is not automatically a production asset and should not be shipped in the new website.

### Production assets

An image used in the delivered website needs a defined role, provenance, rights status, crop and format plan, accessible alternative, loading behavior, and fallback. “Visible on the web” and “free to download” do not establish permission to reuse it.

## Capture screenshots for visual analysis

Text, DOM, and bundle inspection cannot replace looking at the rendered result. When a browser or Playwright surface is available:

1. State the design question the capture should answer.
2. Record URL, access date, viewport, route, authentication state, input mode, and relevant UI state.
3. Capture the settled initial viewport and the relevant full-page structure.
4. Capture consequential states separately: open menus, hover or focus treatment, product-demo steps, scroll transitions, loading, errors, media failure, reduced motion, and mobile composition as relevant.
5. Give the visual model both the screenshot and the matching semantic or technical evidence. Ask it to identify relationships such as hierarchy, alignment, rhythm, crop, type contrast, color roles, interaction feedback, and visual changes between states.
6. Distinguish direct observations from interpretation. A screenshot may show that an element moved; it does not by itself prove which library caused the movement.

Prefer a small evidence set that answers the question over an indiscriminate screenshot dump. Crop a detail only after preserving enough page context to understand it.

If a screenshot tool fails, try another available browser surface or an in-repository Playwright workflow. Record the failed probe and continue with DOM, computed style, assets, or video evidence; failure to capture is not evidence that a visual feature is absent.

Do not capture credentials, personal data, private dashboards, customer information, or authenticated pages without specific authorization. Keep analysis captures temporary unless the project has an approved research location, and never treat them as redistributable assets.

## Route every image need

| Need | Preferred source | Key boundary |
|---|---|---|
| Product interface or workflow proof | Capture the real approved product state | Do not generate a fictional UI and present it as product evidence. |
| Customer, team, facility, event, certification, or outcome proof | User-owned, commissioned, or specifically licensed media | Do not synthesize or substitute people and claims as if they were factual. |
| Original explanatory diagram or data graphic | Authored SVG, canvas, code, or generated draft rebuilt from verified data | Preserve semantics and never invent the underlying facts. |
| Atmospheric hero, editorial illustration, texture, or conceptual scene | Original generation or a suitable licensed asset | Keep it clearly illustrative and coherent with the art direction. |
| Commodity editorial photo or video | Openly licensed, public-domain, or stock media with asset-level verification | Verify commercial use, derivatives, attribution, releases, and depicted rights. |
| Icon system | One coherent owned or permissively licensed set | Record the set license; do not mix unrelated styles casually. |
| Temporary gap | Art-directed generated or licensed placeholder at the final dimensions, original CSS/SVG composition, or polished sample-state media | Label and track the gap; do not let a placeholder become unverified production media. |

The asset role decides the route. Availability of an image generator does not make generation the correct choice for *proof*. For *materials*, generation or a licensed hunt is expected; skipping both is not.

Do not put “find stock vs wait for uploads” on `ask_user`. Hunt materials. Wait only on proof the user must own.

## Build high-fidelity placeholders

Missing final content should not force the design back to wireframe fidelity. Treat a placeholder like a polished presentation-template slot: it should demonstrate the intended composition, crop, color balance, density, contrast, and responsive behavior well enough that the user can understand the finished design.

A high-fidelity placeholder should:

- use the final component dimensions, aspect ratio, border treatment, caption behavior, and loading state;
- contain visually credible sample material that matches the selected art direction;
- survive desktop, tablet, and narrow-mobile crops without hiding the intended focal area;
- use realistic content length and density so the layout is not tuned to empty boxes;
- remain replaceable through a component prop, content record, CMS field, or documented file slot rather than hard-coded page markup;
- carry a development-only status in the asset manifest or preview controls without covering the composition with intrusive labels;
- include a replacement brief: subject, ratio, minimum resolution, focal point, safe zones, palette range, allowed content, alt-text intent, and owner;
- block production release when its rights or factual accuracy are unresolved.

Use the highest-fidelity safe route available:

1. Generate an original illustrative placeholder from the image contract.
2. Select a beautiful openly licensed or stock asset whose terms are verified.
3. Author a polished fictional interface, diagram, crop study, or abstract composition with clearly identified sample data.
4. If none is possible, use a designed fallback that preserves visual mass and rhythm—not a generic gray rectangle.

Pinterest, award galleries, and moodboards are useful for finding a visual direction, subject, lighting, crop, or texture. They are not asset libraries. Pinterest's own [copyright guidance](https://help.pinterest.com/en/article/copyright) directs users to obtain permission from the copyright holder where necessary. Extract the qualities, trace the original creator and license when possible, then generate or source a permitted replacement. Do not scrape, hotlink, or ship an unknown-rights Pin merely because it makes the prototype look finished.

For concept and functional prototypes, make placeholder status obvious in the handoff and asset manifest while keeping the viewed page polished. For production delivery, replace or approve every release-blocking placeholder. High fidelity is a presentation standard; it is not permission to blur factual or rights status.

## Generate original images when appropriate

When image generation is available and the approved asset plan calls for original illustrative media, follow the generation capability's own instructions. Use it for art direction, atmosphere, conceptual illustration, textures, or other non-factual roles—not to manufacture proof.

Define an image contract before generating:

- role in the page and message it must support;
- subject and factual boundaries;
- composition, viewpoint, crop, aspect ratio, and responsive safe zones;
- visual language, palette, material, lighting, and desired consistency across a series;
- foreground/background separation and text-overlay requirements;
- exclusions such as embedded text, recognizable logos, signature reference compositions, unsafe stereotypes, or misleading realism;
- required resolution, formats, loading budget, alt-text intent, and fallback.

Generate a small art-direction set first. Select by purpose and page composition rather than by standalone spectacle, then refine the chosen direction. Ask before a paid run, a large batch, or a direction involving identifiable real people, sensitive subjects, or material external cost.

Before shipping, inspect the actual crops at desktop and narrow mobile. Check anatomy and geometry, text-like artifacts, unintended marks or logos, edge quality, series consistency, contrast behind interface text, file weight, and whether the image could be mistaken for a real product, person, place, event, or result. Keep the prompt, tool or model when available, generation date, selection notes, and material edits in provenance.

## Find reusable images when generation is unavailable or wrong

Use image search to discover candidates, then open the individual asset page and verify its current terms. Search results, thumbnails, gallery pages, and “free image” labels are not license evidence.

Useful starting points, checked 2026-08-25:

- [Openverse](https://openverse.org/) searches Creative Commons and public-domain media. Its own documentation warns that license metadata may be inaccurate, so verify the original asset and license before use.
- [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia) hosts media under varying free licenses or public-domain claims. Follow the license and attribution on each file page and check non-copyright restrictions.
- [Unsplash](https://unsplash.com/license) uses its own broad stock license, not an open-source software license. Review the current restrictions and separately consider recognizable people, brands, artworks, and property.
- [Pexels](https://www.pexels.com/legal-pages/license/) also uses its own stock-media license. Review the current prohibited uses, including endorsement implications and standalone redistribution.

Prefer “openly licensed,” “public domain,” or “stock under a named license” over the vague phrase “open-source image.” License terms can change; re-check them when selecting the final asset.

For each selected asset record:

- original asset-page URL and creator;
- acquisition date and original filename or identifier;
- exact license name and license URL;
- required attribution and where it will appear;
- allowed commercial use, modification, and redistribution;
- share-alike or other derivative obligations;
- model, property, trademark, artwork, privacy, or jurisdictional concerns;
- local modifications and final crop;
- fallback if approval or rights fail.

Do not hotlink unless the source explicitly permits it and the runtime dependency is intentional. Download, optimize, and serve a local derivative only when the license and project rules allow it.

## Fallback ladder

If a production image cannot be generated or licensed safely:

1. Use approved user-owned media.
2. Author an original diagram, SVG, CSS composition, or data visualization.
3. Redesign the section so typography, layout, and real content carry it.
4. Use a high-fidelity, explicitly temporary placeholder with a replacement brief and release-blocking status.

Do not lower the evidence standard merely to fill a visual slot.

## Acceptance checks

- Consequential reference decisions are supported by labeled screenshots or an explicit capture limitation.
- Reference screenshots are not shipped as production media.
- Factual proof uses real approved evidence, not generated substitutes.
- Missing final media is represented by high-fidelity, replacement-ready placeholders rather than low-fidelity gray boxes.
- Generated media has an image contract, responsive crop review, artifact review, and provenance.
- Third-party media has asset-level license, attribution, depicted-rights, and modification records.
- Every placeholder has a status, replacement brief, owner or next action, and explicit production-release disposition.
- Every image has suitable dimensions, formats, loading behavior, alt treatment, and a failure fallback.

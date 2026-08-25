# Design taxonomy and scenario fit

Use several axes together. A site is not simply “minimal” or “3D.”

For a thin brief, pick a starting direction from [brief to direction](brief-to-direction.md) **after** the research pass, then use the axes below to stay consistent and to form catalog queries.

## Scenario axis

Stable scenario tags used by the catalog:

- saas-product: explain value, prove usability, and convert.
- startup-launch: establish a category, create momentum, and capture intent.
- ai-product: make capability and trust legible without generic sci-fi decoration.
- portfolio: make authorship, range, and case quality memorable.
- agency: demonstrate positioning, work, and fit.
- ecommerce: support product discovery, desire, comparison, and purchase.
- corporate: create clarity, legitimacy, and stakeholder confidence.
- editorial: sustain reading, browsing, and content relationships.
- event-campaign: create urgency, identity, schedule comprehension, and registration.
- hospitality: sell atmosphere while keeping booking information accessible.
- architecture: balance spatial imagery, project detail, and practice credibility.
- fashion-luxury: create desire and distinction without hiding commerce tasks.
- nonprofit: communicate mission, evidence impact, and enable action.
- mobile-app: demonstrate flows and provide platform conversion.
- experimental: reward exploration where novelty is itself part of the value.
- content-platform: support search, discovery, hierarchy, and repeat use.

## Visual language axis

- quiet-minimal: low visual noise, strong proportion, precise detail.
- editorial: publication-like hierarchy, rhythm, captions, and long-form control.
- swiss-grid: explicit grid, typographic discipline, systematic alignment.
- expressive-type: type behaves as image, navigation, or motion material.
- monochrome: limited palette makes hierarchy, material, and motion carry more weight.
- colorful: broad palette used as an information or emotional system.
- brutalist: raw defaults, exposed structure, deliberate friction, or anti-polish.
- luxury: controlled scarcity, refined imagery, tactile pacing, exact typography.
- playful: surprise, illustration, elastic behavior, and friendly imperfection.
- cinematic: scene-led pacing, sound or video, scale, and dramatic transition.
- spatial-3d: depth, camera, lighting, and object manipulation are part of meaning.
- futuristic: unfamiliar materials or systems; avoid default neon-on-black clichés.
- interface-dense: product-like controls, data, compact hierarchy, and high information value.
- organic-craft: natural material, irregular rhythm, warmth, and visible making.

## Composition axis

- strict grid;
- asymmetric editorial;
- modular cards or bento;
- full-screen chapters;
- split narrative;
- long-form article;
- gallery or index;
- horizontal sequence;
- layered canvas;
- app shell.

Composition should follow content relationships. Bento is useful for heterogeneous summaries, not as a universal design system.

## Motion axis

- none or state-only;
- microinteractions;
- entrance and reveal;
- layout and shared-element transition;
- scroll choreography;
- page transitions;
- pointer-reactive behavior;
- kinetic typography or SVG;
- video or image sequence;
- physics;
- spatial 3D;
- sound-reactive or sound-accompanied.

Define motion purpose for each system: orient, explain, focus, acknowledge, create continuity, or create atmosphere.

## Scenario-to-direction starting points

| Scenario | Strong starting directions | Common failure |
|---|---|---|
| SaaS or AI product | editorial clarity, product UI, restrained motion, proof-rich sections | generic gradients, empty glass cards, capability claims without evidence |
| Portfolio or agency | expressive type, case-led gallery, transition continuity, authored media | style overwhelms authorship or case detail |
| E-commerce | product-first imagery, tactile details, fast comparison, clear purchase states | cinematic entry blocks shopping tasks |
| Corporate or nonprofit | systematic grid, editorial hierarchy, restrained brand moments | sterile template or vague purpose language |
| Fashion or luxury | art direction, whitespace, precise type, controlled cinematic media | slow pages, inaccessible navigation, copied campaign language |
| Editorial | readable measure, strong type scale, metadata, related-content system | visual novelty breaks reading and discovery |
| Event or campaign | bold identity, temporal information, focused conversion | date, venue, price, or registration becomes hard to find |
| Experimental | spatial, brutalist, playful, or kinetic systems with a semantic fallback | novelty has no concept and no usable fallback |

## Technology selection

Choose after defining behavior, and after you have seen how references actually do it:

| Need | Likely fit | Check before adopting |
|---|---|---|
| Hover, focus, disclosure, simple reveal | CSS or Web Animations API | reduced motion and interruption behavior |
| React/Vue presence, gesture, layout transition | Motion | existing framework and bundle cost |
| Coordinated timelines, ScrollTrigger, text or SVG choreography | GSAP | scroll ownership, cleanup, licensing, fallback |
| Custom compositing, particles, image treatment, simulation | Canvas 2D or GPU canvas | input, resolution scaling, lifecycle, fallback |
| Real-time scene, model, shader, particles | Three.js/WebGL | mobile GPU, input, cleanup, fallback, semantic content |
| Compute-heavy simulation or advanced GPU rendering | WebGPU | capability detection, shader pipeline, target browsers, WebGL or static fallback |
| Authored vector state machine | Rive or Lottie | authoring source, runtime weight, accessibility |
| Cinematic product story | compressed video or image sequence | art direction, bandwidth, poster, captions, reduced data |
| Icon or diagram motion | SVG/CSS/WAAPI | DOM complexity and stroke scalability |

The presence of a library in a reference site does not mean the new site needs it. Conversely, uncertainty about cost is not proof that a simpler technique will look as good. When a technique could define the concept, build and inspect a representative spike before accepting or rejecting it.

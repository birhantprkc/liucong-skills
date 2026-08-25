# Example audit: Gionatan Nese

This is a worked evidence record, not a reusable asset pack.

## Scope

- Target: https://www.gionatannese.com/
- Accessed: 2026-08-25
- Discovery source: https://gsap.com/showcase/
- Question: how does a portfolio combine semantic case-study content with an immersive, media-heavy spatial layer?
- Tested state: initial desktop visit in the Codex in-app browser.

## Observed experience

- Observed: the rendered viewport is a sparse white spatial composition with small floating project imagery, compact navigation, and an optional sound control.
- Observed: the semantic DOM exposes a conventional portfolio structure even when the visual canvas is highly composed: a descriptive H1, Selected Work, project articles, and an Explorations list.
- Observed: project summaries explain the work in text, including the intended use of WebGL, subtle 3D, typography, motion, and interaction.
- Observed: sound is opt-in through a Turn on sound control.

This separation matters: the art-directed visual layer does not replace the content outline.

## Asset evidence

The browser page-asset inventory reported 84 observed resources in this state:

- 21 scripts and 1 stylesheet;
- 3 fonts: Lay Grotesk Medium, Teodor Regular, and Teodor Light;
- 12 images, many delivered from Sanity CDN;
- 9 videos;
- a GLB model and MatCap texture;
- several MP3 files for ambient, enter, hit, click, menu-hover, image-hover, and scrubble behaviors;
- one small inline SVG.

Detected asset examples:

- /Model/model.glb
- /Model/MatCap.jpg
- /Preloader.mp4
- /audio/AMBIENT.mp3
- cdn.sanity.io image assets

The inventory proves requests were observed, not that every resource was visible or active at the same time.

## Technical evidence

### High confidence

- Detected: Next.js-style _next/static/chunks paths and React Server Component _rsc requests.
- Detected: Turbopack-named runtime chunk and TURBOPACK strings across chunks.
- Detected: Sanity-backed imagery and a bundle containing sanity identifiers.
- Detected: bundles containing GSAP and ScrollTrigger identifiers; the site is also listed in the official GSAP Showcase.
- Detected: bundles containing Three.js, WebGL, and GLSL identifiers, supported by the observed GLB model and MatCap texture requests.

### Unknown

- Exact framework and library versions.
- Exact division of labor among CSS, GSAP, and Three.js for every transition.
- Shader source and scene graph.
- Mobile GPU behavior, reduced-motion implementation, and complete keyboard behavior.
- Total transferred weight and Core Web Vitals.

## Probe limitation discovered

The browser's safe evaluation surface did not expose document.getAnimations or performance.getEntriesByType. The initial all-in-one probe failed. The audit therefore fell back to:

- DOM snapshot;
- screenshots;
- Playwright locators;
- page-asset inventory;
- public script URL and bundle-keyword inspection.

This is why the main protocol capability-checks optional APIs and keeps probes independent.

## Reusable principles

1. Keep a semantic content layer underneath an experimental visual layer.
2. Make sound optional and explicit.
3. Use a restrained base palette so type, motion, and 3D assets carry the identity.
4. Let project descriptions explain the creative intent instead of relying only on spectacle.
5. Load specialized media in formats appropriate to their role: GLB and texture for real-time material, WebM for loops, and custom fonts for hierarchy.

## Do not copy

- The floating-image composition;
- the site's exact typography;
- project imagery, GLB model, textures, video, audio, or copy;
- signature navigation labels and spatial behavior.

For a new portfolio, adapt the principles to the creator's own work, assets, authorship, and accessibility requirements.

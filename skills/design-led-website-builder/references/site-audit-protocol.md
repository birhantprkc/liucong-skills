# Forensic site audit protocol

Use this after a [research pass](research-pass.md) when a target interaction, animation, 3D scene, asset system, or implementation technique must be understood before building. Do not start here for an ordinary thin brief — run the reference pass first.

## Set the question first

Write the exact decision the audit must support. Examples:

- Is this effect a video, image sequence, DOM transform, canvas, or WebGL scene?
- How does the site transition between case studies?
- Which assets make the art direction work?
- Can a similar narrative remain usable on mobile and reduced motion?

Avoid collecting everything when only one behavior matters.

## Evidence record

For each consequential finding record:

- URL and access date;
- page and UI state;
- viewport and input mode;
- observation or claim;
- evidence type: observed, detected, source-claimed, inferred, or unknown;
- confidence and alternative explanations;
- screenshot, DOM, asset, request, bundle, or documentation reference when available.

Do not claim exact library versions unless version evidence is direct.

When appearance is consequential, follow the screenshot and visual-model workflow in [visual evidence and image assets](visual-evidence-and-assets.md). A text-only audit is incomplete for claims about composition, typography, imagery, spatial hierarchy, or state transitions.

## Pass 1: experience and structure

1. Let the page settle; note preloader, consent, sound, and permission states.
2. Capture the settled initial viewport and full content structure; preserve separate captures for consequential UI, scroll, loading, failure, reduced-motion, and responsive states.
3. Identify semantic headings, navigation, primary action, and content order.
4. Traverse the primary path as a user.
5. Note desktop, mobile, keyboard, and reduced-motion behavior when relevant.

Visual canvas content and accessible DOM may be different layers. Audit both.

Do not capture private or authenticated states without specific authorization, and do not retain credentials or personal data in screenshots.

## Pass 2: interaction and motion

Build an interaction map:

| Trigger | Target | Behavior | Duration/easing | Purpose | Fallback |
|---|---|---|---|---|---|
| scroll, hover, click, route, time, audio | element or scene | transform, reveal, morph, camera, state | measured or unknown | orient, explain, focus, atmosphere | reduced or static state |

Use Playwright locators and screenshots to reproduce states. Sample intermediate states when timing matters. Capability-check optional APIs before calling them:

    const animations =
      typeof document.getAnimations === "function"
        ? document.getAnimations()
        : document.body && typeof document.body.getAnimations === "function"
          ? document.body.getAnimations({ subtree: true })
          : [];

A missing browser API does not prove that the page has no animation. Fall back to computed styles, screenshots over time, runtime globals, asset inventory, and bundle evidence.

Inspect:

- CSS transitions, keyframes, scroll-driven animation;
- Web Animations API;
- transform and opacity layers;
- sticky and pinned regions;
- page transitions and shared elements;
- pointer and gesture response;
- GSAP timelines and plugins;
- canvas/WebGL render surfaces, camera behavior, shaders, and model loading;
- video, image sequence, Lottie, Rive, SVG, and audio.

## Pass 3: assets and art direction

Inventory without copying:

- raster and responsive image variants;
- SVG and inline vector markup;
- fonts, weights, and licensing clues;
- video, poster, captions, codecs, and autoplay behavior;
- audio and sound opt-in;
- GLB/GLTF models, textures, environment maps, and compressed geometry;
- icons, illustrations, data, and CMS/CDN origins.

Record dimensions, formats, roles, loading strategy, and provenance. Do not bundle or reuse third-party assets unless the user has rights and specifically needs them.

## Pass 4: technical evidence

Inspect several independent signals:

- HTML markers, response headers, route behavior, and metadata;
- script and stylesheet URLs;
- network initiator type and asset requests;
- runtime globals or registered plugins;
- source maps or unminified module names when publicly available;
- bundle strings, with false-positive caution;
- framework paths such as _next, _nuxt, or Webflow attributes;
- CMS/CDN domains and request shapes.

Confidence guidance:

- High: direct runtime object plus matching request or authored source.
- Medium: multiple independent bundle, path, asset, or gallery signals.
- Low: one minified keyword, class naming, or visual resemblance.

When inspecting public bundles, search only to identify implementation evidence. Do not reconstruct proprietary source code.

## Pass 5: cost and quality

Check:

- resource counts and approximate weight where observable;
- long loading, layout shift, blocked interaction, and console errors;
- mobile GPU and memory risk;
- semantic structure, focus order, contrast, labels, captions, and reduced motion;
- content availability without canvas or animation;
- failure behavior when media, JavaScript, or WebGL is unavailable.

## Synthesis

End with:

1. What the experience is doing.
2. Why it works for that site's purpose.
3. Directly supported implementation evidence.
4. Unknowns and limitations.
5. Reusable principles.
6. What must not be copied.
7. The highest-fidelity justified implementation option, the spike needed to prove it, and a robust capability fallback.

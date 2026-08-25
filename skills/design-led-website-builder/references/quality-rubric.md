# Website quality rubric

Use this after implementation and before handoff. Score only what was actually inspected.

For a thin-brief first site, also apply the first-pass gates at the bottom. Research must have happened; a pretty template with no references is a fail.

## Weighted review

### Art direction and visual fidelity: 25

- Typography, composition, imagery, color, depth, and material behavior form a distinctive system.
- The rendered result communicates the intended emotional position immediately.
- Signature sections reach presentation fidelity rather than stopping at competent layout.
- Missing final imagery is represented at presentation fidelity, so the intended direction remains understandable.

### Originality and identity: 15

- The site has a recognizable point of view without borrowing a reference's signature.
- Novelty reinforces this specific product, person, place, or event.
- The result does not collapse into the easiest available template or the example fixture's visual language.

### Interaction, motion, and spatial execution: 20

- The primary interaction or motion idea is implemented and inspected, not merely described.
- Advanced techniques are judged through working spikes and rendered comparison rather than rejected abstractly.
- Motion, spatial behavior, sound, and state changes feel authored and coherent.
- Every interaction has feedback and clean interruption.

### Composition and responsiveness: 15

- Layout relationships hold across wide desktop, laptop, and narrow mobile.
- Content extremes do not break rhythm or hierarchy.
- Touch targets, overflow, and media cropping are deliberate.

### Strategy and content: 15

- The primary audience and action are obvious.
- Message hierarchy matches the user's purpose.
- Proof appears where skepticism arises.
- Real content is used; missing content is explicit.

### Accessibility, performance, and robustness: 10

- Semantic structure and keyboard order match the visible experience.
- Focus is visible; controls have names and states.
- Contrast, media alternatives, captions, and error messages are adequate.
- Canvas, 3D, sound, and gesture features have usable alternatives.
- The primary content is not hostage to decorative media.
- Images, fonts, video, and 3D assets load proportionately.
- Generated and third-party images have coherent responsive crops, artifact review, provenance, and rights records.
- No relevant console errors, broken links, layout shifts, or stuck states remain.
- Slow network, failed media, and unsupported WebGL have reasonable outcomes.

Do not award a visually weaker primary experience merely because its implementation is simpler. Accessibility and fallback quality are release requirements, not reasons to pre-emptively flatten the main design.

## Release gates

Do not call the site finished when any in-scope gate fails:

- research was skipped, or no live references informed the direction;
- research targeted the wrong job (blog themes for a visual site, or spectacle sites for a publishing site);
- the agent kept asking after one intent lock, or researched while the question was still open;
- a no-brand brief was stalled for lack of a kit, or padded with a fake career;
- the first build is type-only, or CSS/SVG ornament stands in for hunted materials;
- proof (their face, their work) is faked with stock or generation;
- primary path is broken;
- important content is absent or fabricated;
- mobile layout has blocking overflow or unreadable text;
- keyboard users cannot reach or identify primary controls;
- essential motion ignores reduced-motion preference;
- autoplay sound has no prior opt-in;
- 3D or video failure removes essential meaning;
- third-party assets lack known permission;
- a reference screenshot is shipped as an asset without permission;
- generated media is presented as factual product, customer, team, place, event, or outcome evidence;
- a production build still contains an unapproved or unknown-rights placeholder marked as release-blocking;
- the implementation overwrites unrelated user work.

## Thin-brief first pass

When the user only gave who / why / what, the first site still has to:

- pass a three-second identity test (whose site, what it is, what to do);
- include every content item they listed, at presentation fidelity;
- match the locked intent (a publishing site reads; a visual site hits);
- use hunted materials on the first viewport, not type-plus-CSS-ornament;
- look unlike a generic template *and* unlike this skill’s TRACE/WORK fixture;
- look unlike “the same site with a different name”;
- use high-fidelity placeholders where media is missing, with a replacement brief;
- be usable at ~390px.

## Evidence

Report:

- references opened and principles taken;
- `ask_user` questions asked, or why none were needed;
- commands and automated checks run;
- viewport and scenario checks;
- screenshots or browser states compared;
- working alternatives compared for consequential visual or technical choices;
- accessibility and performance tools used;
- areas not tested and why.

Automated scores are signals, not substitutes for the primary user journey or visual review.

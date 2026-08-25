# Intake, questions, and ask_user

Extract who / why / what, and which raw material they brought. If the brief can mean more than one product, **ask once to lock intent, wait, then research.** Never research the wrong job because a word was taken literally.

This file is English. User-facing questions use the user's language.

## Raw material

People operate differently. Notice which of these you were handed.

### They brought a brand

Logo, colors, type, existing site, guidelines, “our brand is…”.

- Open *their* site if they pointed at it.
- Keep the brand. Still lock *what the new site is for* if that is unclear (brochure vs product vs recruiting).
- Do not ask them to name a style already encoded in the brand.

### They did not

A name, a goal, some content (notes, a few projects, two photos), maybe a taste cue.

- That is enough to start — after intent is locked.
- Invent the visual system from purpose + content + cue.
- Do not stall for a brand kit or a biography.

### They brought a reference

URL, screenshot, “like this site”, a style sentence that already implies the product.

- That is the lock. Do not ask. Research that, then build.

## Who / why / what

- **Who** from the message and uploads.
- **Why:** audience, primary action. Infer when stated.
- **What to show:** keep listed sections. Do not ask “which pages do you want?” when about / work / contact are already named.

If identity is totally absent (“make me a website”), the one question is “whose site is this, and who is it for?” — still one round.

## When intent is already singular — skip the ask

Go straight to research:

- “I am Lin Ke, an independent illustrator. I want brands to commission me. About, work, process, contact.”
- “Personal site for Jia — restrained, wood and paper. Work and writing.”
- “Here is a reference [URL]. Make my portfolio from these three images.”
- “This is our brand kit. Rebuild the product site: demo, features, pricing.”
- “Neighborhood wine bar. Menu, wines, reservation, two photos.”

## When it could be more than one product — ask once, then wait, then research

Do this **before opening any reference**. Derive 2–4 options from *this* brief. Each option is a product, with what you will research if they pick it. Then **stop until they answer**.

Examples of how the options change with the brief:

**“Make a personal blog. He writes notes and also wants to show projects.”**

- Publishing site: notes should be readable and archivable — research publications
- Visually driven site: projects and presence first — research high-craft personal sites
- I have a reference: next message is a URL or screenshot

**“Build a company website.”**

- Product site: demo, features, conversion
- Company intro: business lines, trust, contact
- Recruiting: team and roles
- I have a reference

**“Make a portfolio. Make it look good.”**

- Case-study studio: written cases
- Image index: work on the first screen
- Spatial / motion piece: a strong first viewport
- I have a reference

Use `ask_user` / `AskUserQuestion` / host equivalent. If missing, ask in chat with the same shape and wait **once**.

Mark a recommended default only when the rest of the brief implies one.

That is the whole interview. After the answer you may not ask about color, dark mode, font, blogroll, or “anything else to add?”

## Never ask these

- What style do you like? / Modern or minimal?
- Light or dark?
- Confirm audience / tone / brand keywords again
- Should we add a blog, timeline, blogroll, guestbook?
- Education, employer, social accounts (unless they offered them as content)
- Which tech stack
- Please send a full brief pack

## After the one answer

Research **that** product only. Fold later messages into the build without a new questionnaire.

A later question is allowed **only** for rights or factual publication when you are about to ship it as fact. Not for taste.

---
name: spendly-ui-designer
description: Generates modern, production-ready UI pages and components for Spendly (aka Kharche), a Flask-based personal expense tracker (templates/ + static/ CSS/JS, no frontend framework). Use this skill any time the user asks to design, build, create, redesign, or improve a page or UI component for Spendly/Kharche — phrases like "design the ___ page", "create UI for ___", "build a component for ___", "redesign/improve ___", or any request touching the app's look and feel, even if they don't say "UI" explicitly. Also trigger for icon choices, layout/spacing decisions, or matching the app's existing visual style. Produces a brief UI structure, Jinja2/HTML markup, vanilla CSS, and Lucide icons, written directly into the project's templates/ and static/ folders.
---

# Spendly (Kharche) Frontend UI Designer

Generates clean, modern, fintech-style UI for Spendly — a personal expense tracker built with **Flask + Jinja2 templates + vanilla CSS/JS** (no React, no Tailwind, no build step). Every page/component produced by this skill must look like it was designed by the same person who built the rest of the app.

Repo reference: https://github.com/PrakhrS/Kharche (`app.py`, `templates/`, `static/`, `database/`).

## Golden rule: inspect before you design

Never generate UI from a generic template. Before writing anything:

1. **Find the project.** Look for `templates/`, `static/css/`, `static/js/` relative to the working directory (or ask the user for the path if not found).
2. **Read the existing design system directly from the code**, not from memory or assumption:
   - Open `templates/base.html` (or equivalent layout/shared template) to see the page shell, nav, and included stylesheets/scripts.
   - Read the main CSS file(s) in `static/css/` — extract the actual color palette (hex values), font-family, border-radius values, shadow styles, and spacing scale in use.
   - Skim 1-2 existing page templates to see how cards, buttons, forms, and tables are currently structured and classed.
   - Check whether an icon library is already wired in (e.g. a Lucide `<script>` tag in the base template, inline SVGs, or something else).
3. **If the existing design is inconsistent, missing, or you genuinely can't tell what the visual language should be**, stop and ask the user for reference screenshots of the current app before generating anything. Do not guess a fintech aesthetic out of thin air when a real one already exists in the repo.
4. Only after this inspection, treat the design rules below as the target aesthetic for anything new — filling gaps, not overriding what's already established.

## Gathering the request

At minimum you need the **page or component name** (e.g. "monthly budget page", "expense card component", "add-transaction modal"). If the user gives it, proceed — don't stall on a full interview for a simple, well-scoped ask.

Politely ask a follow-up only when something genuinely blocks a good result:
- The page needs real data shape (e.g. what fields an expense/category/budget object has) and it isn't obvious from `database/` or existing templates — check those first before asking.
- The user references a page/section that doesn't exist yet and the placement/navigation entry point is unclear.
- Step 3 above triggered (no inferable design system).

Otherwise, proceed with sensible defaults and state the assumptions you made.

## Design rules (the Spendly look)

Apply these on top of whatever real tokens you extracted from the existing CSS — reuse those tokens (exact hex codes, existing CSS variables, existing font stack) rather than inventing parallel ones:

- **Aesthetic**: minimal, clean fintech UI. Confident whitespace, no visual clutter, no random one-off styles.
- **Shape language**: rounded corners (cards/buttons/inputs), soft/subtle shadows for elevation — never harsh drop shadows.
- **Spacing**: consistent 8px grid (8, 16, 24, 32, 40...) for padding, gaps, and margins.
- **Layout**: card-based sections for grouped content (e.g. an expense card, a summary stat card); clear visual hierarchy (size/weight/color establish what matters most first).
- **Color**: subtle, restrained palette — reuse the project's existing primary/neutral/accent colors; use color purposefully (e.g. red/green for expense vs. income, not decoratively).
- **Icons**: use Lucide icons wherever an icon adds clarity (nav items, action buttons, empty states, category markers). If the base template doesn't already include Lucide, add the Lucide CDN script (`https://unpkg.com/lucide@latest`) once to the shared layout and use `<i data-lucide="icon-name"></i>` + `lucide.createIcons()`, matching however icons are already invoked if a pattern exists.
- **Avoid**: generic dated UI (default browser form styling, unstyled tables), unstructured code dumps, inline `style=` attributes, styles that don't reuse the existing design tokens.

## Code conventions

- **Templates**: Jinja2, consistent with existing templates — extend `base.html` (`{% extends "base.html" %}`) and use existing block names rather than restructuring the page shell.
- **CSS**: plain vanilla CSS. Add a new stylesheet under `static/css/` named for the page/component (e.g. `budget.css`) unless the existing project keeps everything in one shared file — match whatever pattern is already there. Use CSS custom properties if the project already defines them; otherwise keep values consistent with what you extracted from the existing styles.
- **JS**: vanilla JS only, no framework. Keep it in `static/js/` following the existing file-per-page or shared-file pattern, whichever the project already uses.
- **Modularity**: break markup into logical, reusable chunks (e.g. a `_expense_card.html` Jinja include/macro) when the same UI piece will repeat, instead of copy-pasting blocks.
- **Minimal boilerplate**: no unused classes, no commented-out scaffolding, no placeholder lorem ipsum beyond what's needed to demonstrate the layout.

## Output

Deliver, in this order:

1. **UI structure (brief)** — a short summary: the layout and key sections, and any notable UX decisions (e.g. "empty state shown when no expenses this month", "category color-coding reused from the existing badge styles"). A few sentences to a short list — not a full spec document.
2. **The code** — write the actual files (template, CSS, and JS if needed) directly into the project's `templates/` and `static/` folders, following the conventions above. Don't just print code in chat; save it to the real paths.
3. **Design quality note** — one or two lines on how it fits the fintech look (spacing/hierarchy/cards) and where you reused existing tokens vs. introduced new ones (and why).
4. **Icons used** — list which Lucide icons you used and where.

After writing the files, briefly tell the user which files were created/modified with their paths. If a file-presentation tool is available in this environment, use it so the user can open what changed.

## Common pitfalls to avoid

- Don't reach for Tailwind, CSS-in-JS, or any component framework — this project has no build step.
- Don't restyle the whole app to fit one new page; scope changes to what was asked.
- Don't invent a color palette or font when the project already has one — go find it first.
- Don't skip the "read the existing code" step even for a "quick" component — a mismatched card style is the single most common way this skill fails.
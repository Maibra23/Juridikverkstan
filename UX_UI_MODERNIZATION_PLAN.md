# UX/UI Modernization Plan: Juridikverkstan

Status: proposal, awaiting approval. No source file has been changed.
Base branch audited: `sakerhet/kostnadsskydd` (commit `fd5c833`), which is the latest
version of the product. It is two commits ahead of `main` and contains every other
branch (`main`, `feat/ux-omdesign`, `feat/kunskapsutmaning-och-lagrumsrobusthet`).
Audit date: 2026-11-17. Streamlit installed: 1.67.0. Baseline test run: 1647 passed,
130 skipped.

## How to read this document

The brief was written for a financial product. The repository is not one. Juridikverkstan
is a Swedish legal training app: students practise legal method (RNTS: Rättsfrågan, Norm,
Tillämpning, Slutsats) on cases, quizzes and statute hunts, with an optional LLM tutor
whose every citation is checked against a register of 21 statutes. Every recommendation
below is therefore translated from "financial trust and precision" into its legal
equivalent: citation trust, source transparency, and clear separation between curated,
generated and verified content. Section A8 maps each financial requirement of the brief
onto the legal domain explicitly.

The product has also already been through one design pass (`feat/ux-omdesign`, "etapp 1"),
documented in `design_system.md`. That pass made deliberate decisions that this plan
respects instead of reopening: no icons or emoji anywhere (enforced by
`tests/test_sprak.py`), no collapsible navigation, no centred content column (tried and
reverted on 2026-08-07, commit `bf268ae`), and gold reserved exclusively for statute
references. This plan is a second pass: it finishes what etapp 1 started, fixes the
defects it left, and uses Streamlit 1.67 theming that did not exist when the design
system was written.

---

# PART A: UX/UI MODERNIZATION PROPOSAL

## A1. Executive summary

**Current assessment.** The product is pedagogically strong and technically disciplined:
one shared module view for twelve modules, deterministic grading before any LLM call,
a verified citation system, 1647 tests including language and design guards. The design
language (parchment, ink, authority blue, statute gold, serif headings) suits a legal
publication and should be kept.

The weaknesses are in execution, not direction:

1. **Typography contradicts the design system.** `design_system.md` section 2 says body
   text and UI use sans serif with serif headings. `.streamlit/config.toml` sets
   `font = "serif"`, so every button, label, input, tab and table renders in Source Serif
   (verified in the running app). Controls look like body text and the hierarchy flattens.
2. **Visible rendering defects.** Literal `**asterisks**` appear in two notices because
   `render_info` and `render_varning` escape markdown (`utils/ui.py:153`, `:285`; seen on
   Kunskapsutmaning and in the tutor fallback text). Colons have been used as a generic
   separator after the middle dot was banned, which produces strings such as
   "Svårighetsgrad: Grund: ca 10 min" and "3 moduler påbörjade: 2 rättsfall genomförda: 5/7 rätt
   på quiz". One sentence starts in lower case (`sidor/0_Hem.py:121`).
3. **Action hierarchy is inverted on the main workflow.** In the Rättsfall tab the
   difficulty selector and a full-width primary "Generera nytt rättsfall" button (an
   optional LLM feature) sit above the curated case, which is the default content. At
   1440 by 900 the case text starts at the fold. Up to three primary buttons are visible
   in one flow, and every answered quiz question adds another primary tutor button.
4. **Dead ends and inert controls.** Kunskapstest lists modules as plain text (not
   links, alphabetical rather than in the app's order). "Visa appens rättsfall" is always
   shown, usually disabled. The helper `pipeline_steps` is unused.
5. **Accessibility gaps.** Statute gold used as text measures 3.25:1 on white, and the
   "(kommer)" rows 3.05:1. Both fail WCAG AA for 13 px text. The RNTS stepper exposes
   state by colour and shape only, with nothing for screen readers. External links open
   new tabs without `rel="noopener"` or any notice.
6. **Mobile.** `initial_sidebar_state="expanded"` makes the 300 px sidebar cover the
   content on every page load on a phone. Streamlit's developer "Deploy" button shows in
   the header.

**Objectives.** Make the interface read as a mature, trustworthy legal training tool:
clear typographic hierarchy, one primary action per view, the case before the controls,
consistent feedback, honest labelling of AI-generated versus curated material, and
WCAG AA throughout.

**Expected improvements.** Correct rendering everywhere; the default case is visible
above the fold; consistent success, warning and error styling; actionable progress
pages; accessible contrast and state; a usable phone layout. All with no new
dependencies, no change to business logic and no change to session-state keys.

## A2. Existing application assessment

### Architecture

| Layer | Files | Notes |
|---|---|---|
| Entry and router | `streamlit_app.py` | `st.set_page_config`, `st.navigation(position="hidden")`, CSS injection, sidebar, visit registration |
| Pages | `sidor/*.py` (17) | 12 module pages are three-line shells calling `utils.modulvy.rendera_modulsida`. Five tool pages: Hem, Rättskartan, Kunskapstest, Kunskapskarta, Kunskapsutmaning |
| Shared UI | `utils/ui.py`, `utils/css.py` | HTML components rendered with `st.html`, one CSS template with palette, type and spacing tokens |
| Module view | `utils/modulvy.py` | Three tabs: Rättsfall (RNTS form, tutor, facit), Quiz, Lagrumsjakt |
| Navigation data | `utils/navigation.py` | `NAV_TRAD` tree mirrors Swedish legal systematics; CTA logic |
| Graphs | `utils/taxonomi_ui.py`, `utils/kraftgraf_ui.py`, `utils/graf_ui.py`, `utils/static/*.js` | vis-network 9.1.9 from unpkg inside `components.html` iframes |
| Domain logic | `utils/lagrum.py`, `quiz.py`, `scenarier.py`, `generator.py`, `fallkontroll.py`, `granskning.py`, `prompts.py`, `tutor.py`, `llm.py`, `llm_budget.py` | Untouched by this plan |
| Export | `utils/export.py`, `utils/obsidian.py` | Markdown, Excel (openpyxl), Obsidian zip |
| Data | `data/` | `lagrum.json`, 12 scenario files, `rattssystem.json`, `nyckelbegrepp.json`, verbatim statute text |
| Quality gate | `tests/` (41 files), `ruff.toml`, `.github/workflows/ci.yml` | pytest, ruff, mypy, node tests; language guard; CSS token guard |

No database, no authentication. State lives in `st.session_state` and is lost when the
tab closes, which the UI states plainly.

### Navigation

A single always-expanded sidebar tree (`render_sidopanel`) with four visual levels:
category (mono caps, blue), subcategory (ink), sub-branch (grey, indented), module
(`st.page_link`). Planned modules collapse into one grey "(kommer)" row per group.
Ancestors of the open page get full ink weight. Home has one CTA that computes the next
unstarted module in the app's order.

### Visual identity

Parchment `#FAF7F2` background, ink `#1A2332` text, authority blue `#2C5F8A` accent,
statute gold `#B8860B` reserved for citations, warm green and red for states. Serif
headings, mono eyebrows in letter-spaced capitals, 46 rem reading width for the app's own
blocks. Calm, bookish and appropriate for law. It should stay.

### Component patterns

Custom HTML components (`hero`, `section_heading`, `render_case`, `render_lagrum_chip`,
`render_rnts_steg`, `render_tutortext`, `render_lagkort`, `render_begreppskort`,
`render_varning`, `render_info`, `render_tranar`, `footer_note`) mixed with native
Streamlit widgets. Feedback uses two parallel systems: native `st.success`, `st.error`,
`st.warning`, `st.info` in the module view and Kunskapstest, and custom `.jok-varning`
and `.jok-info` cards elsewhere. The native ones still use Streamlit's default green, red
and blue, not the app palette.

### Interaction patterns

Strong and deliberate: tutor runs only on click, answers are cached by input hash and
marked stale when the student edits; facit is behind a per-task "Jag har försökt, visa
facit" gate; norm citations are validated live while typing; statute hunt re-grades live
after the first click. These patterns are preserved without change.

### Main usability problems

Listed with evidence in A6 per page. In short: inverted action hierarchy on the core
workflow, rendering defects, inert or non-clickable elements that look actionable,
contrast failures, colour-only state, and a mobile layout that hides content behind the
sidebar.

## A3. Feature and functionality inventory

Importance: H high, M medium, L low. "Modify" means the UI around the feature changes in
this plan; the behaviour never does unless marked as a decision in A10.

### Core functionality

| ID | Feature | Location | Interaction | Dependencies | Imp. | Current UX/UI issues | Modify |
|---|---|---|---|---|---|---|---|
| F01 | Curated case exercise (19 cases) | `modulvy._rendera_rattsfall`, `rendera_case_ovning` | Select case, read scenario | `scenarier`, `render_case` | H | Case pushed below controls; metadata uses double colon | Yes |
| F02 | RNTS form (4 text areas, 2000 chars each) | `modulvy._rnts_formular` | Type analysis | `prompts.MAX_TECKEN_PER_FALT` | H | Form width differs from case card width | Layout only |
| F03 | Live norm validation chips | `modulvy._norm_feedback` | Automatic on rerun | `lagrum.extrahera_lagrum`, `validera_lagrum` | H | None significant | No |
| F04 | RNTS stepper | `ui.render_rnts_steg` | Read only | `rnts.RNTS_STEG` | M | State is colour and shape only | Yes (a11y) |
| F05 | Tutor review with grounding, retry, stale detection | `tutor.tutorknapp`, `generera_tutorsvar` | Click button | `llm`, `granskning`, `llm_budget` | H | Always primary; fallback text shows literal asterisks | Yes |
| F06 | Facit gate and deterministic facit | `modulvy._rendera_facitgrind`, `_rendera_facit` | Click to unlock per task | session keys `facit_upplast_*` | H | None | No |
| F07 | Generated case with difficulty and fallback | `modulvy._rendera_rattsfall`, `generator.generera_case` | Choose level, click generate | LLM, `fallkontroll` | M | Dominates the tab; no source label on the case card | Yes |
| F08 | Multiple choice quiz (86 questions) | `modulvy._rendera_quiz` | Pick, click "Svara" | `quiz.ratta_flervalsfraga` | H | "Resultat: 0 rätt av 0" before any answer; "Rätt!" breaks tone rule; a primary button per answered question | Yes |
| F09 | Statute hunt (43 tasks) | `modulvy._rendera_lagrumsjakt` | Type citation, click "Rätta" | `quiz.ratta_lagrumsjakt` | H | Long undifferentiated list | Layout only |
| F10 | Completion registration | `export.registrera_case_genomford`, `obsidian.registrera_case_analys` | Automatic when 4 fields filled | session state | H | None | No |

### Supporting functionality

| ID | Feature | Location | Interaction | Dependencies | Imp. | Current UX/UI issues | Modify |
|---|---|---|---|---|---|---|---|
| F11 | Next-step CTA and resume link | `sidor/0_Hem.py`, `navigation.cta_mal` | Click | `framsteg` | H | Good | No |
| F12 | Progress summary | `sidor/0_Hem.py:_render_framsteg` | Read | `quiz`, `export` | M | Colon-chained sentence; lower-case sentence start | Yes |
| F13 | Exports: Obsidian zip, Markdown, Excel | `sidor/0_Hem.py:_render_export` | Download | `obsidian`, `export`, `openpyxl` | H | Fine; Excel sheet name mixes English "case" | Copy only |
| F14 | Hierarchical sidebar navigation | `ui.render_sidopanel`, `navigation.NAV_TRAD` | Click | `st.page_link` | H | Tall brand block; covers content on phones; "(kommer)" contrast fails | Yes |
| F15 | LLM status line and cap cards | `ui.render_statuspanel`, `render_*_cap_card` | Read | `llm`, `llm_budget` | M | Fine | No |
| F16 | TRÄNAR labels | `ui.render_tranar`, `rnts.tranar_etikett` | Read | | M | Fine | No |
| F17 | Page help expander | `ui.render_sidhjalp` (Rättskartan only) | Expand | | L | Design system says every page; only one uses it | Optional (P3) |
| F18 | Disclaimer and footer | `ui.footer_note`, Home caption | Read | | M | "Version 0.1.0: uppdaterad 2026-07-08" (colon, stale date) | Copy |

### Advanced functionality

| ID | Feature | Location | Interaction | Dependencies | Imp. | Current UX/UI issues | Modify |
|---|---|---|---|---|---|---|---|
| F19 | Taxonomy tree graph (Trädvy) | `taxonomi_ui.render_taxonomigraf`, `static/taxonomigraf*.js` | Click branch to focus, click law to open lagen.nu, reset view | vis-network CDN | H | Graph starts low on the page; legend copy says "Kurslag", uses "&" | Copy, placement |
| F20 | Force graph (Kraftvy) with search, branch filter, info panel | `kraftgraf_ui.render_kraftgraf`, `static/kraftgraf.js` | Search, filter, click, double click | vis-network CDN | M | "Kurslagar" label | Copy |
| F21 | Reference-law toggle | `sidor/16_Rattskartan.py:111` | Checkbox | `rattssystem_graf` | M | Help text says "kurskarta" | Copy, placement |
| F22 | Area tree with law cards and sections | `sidor/16_Rattskartan.py:141`, `ui.render_lagkort` | Expand | `lagkort_avsnitt`, `lagrum` | H | Expander labels colon chained; gold text fails contrast | Yes |
| F23 | Case type guide (Falltypsguide) | `sidor/16_Rattskartan.py:199` | Search, clear | `rattskarta.falltypsguide` | M | Clear button on its own row | Layout |
| F24 | Key concepts bank (58) with search, area filter, clear, module link, LLM deepening popover, "Se även" | `sidor/16_Rattskartan.py:255` | Search, filter, expand, popover | `nyckelbegrepp`, `tutor` | H | Expander label "X: 5 begrepp" | Copy |
| F25 | Personal knowledge graph (Kunskapskarta) | `sidor/10_Kunskapskarta.py`, `graf_ui` | Drag, zoom | vis-network CDN | M | Legend written as prose, which `design_system.md` 4.2 forbids | Yes |
| F26 | Knowledge challenge (Kunskapsutmaning) | `sidor/11_Kunskapsutmaning.py` | Area, "Överraska mig", difficulty, generate | `generator`, shared exercise flow | M | Literal asterisks in empty state | Yes |
| F27 | Results overview (Kunskapstest) | `sidor/9_Kunskapstest.py` | Read | `quiz.alla_resultat` | M | Module list not clickable, alphabetical, no progress | Yes |

### Administrative and operational functionality

| ID | Feature | Location | Imp. | Modify |
|---|---|---|---|---|
| F28 | LLM budget: session cap 40, shared daily cap 300, hourly cap, `/no_think`, token limits, prompt injection fencing | `utils/llm.py`, `utils/llm_budget.py`, `utils/prompts.py` | H | No |
| F29 | Data maintenance scripts | `scripts/hamta_lagstruktur.py`, `hamta_lagtext.py`, `verifiera_lagavsnitt.py` | M | No |
| F30 | Quality gate and language guard | `tests/`, `.github/workflows/ci.yml` | H | Tests extended, never weakened |
| F31 | Error detail suppression | `.streamlit/config.toml` `showErrorDetails = "none"` | H | No |

### Experimental or optional functionality

| ID | Feature | Location | Notes |
|---|---|---|---|
| F32 | "Överraska mig" random module | `sidor/11_Kunskapsutmaning.py:62` | Keep |
| F33 | Planned modules shown as "(kommer)" | `ui._rendera_barn` | Keep, fix contrast |

**Session-state keys that must not change** (they carry student work across reruns):
`rnts_{case_id}_{falt}`, `facit_upplast_*`, `quiz_val_*`, `quiz_klart_*`, `quiz_svara_*`,
`quiz_resultat`, `jakt_svar_*`, `jakt_rattad_*`, `jakt_ratta_*`, `gen_case_*`,
`gen_notis_*`, `gen_kalla_*`, `gen_raknare_*`, `gen_niva_*`, `case_val_*`,
`utmaning_*`, `tutor_cache`, `_jok_aktiv_sida`, `_jok_senast_besokt`, `falltyp_sok`,
`begrepp_sok`, `begrepp_omrade`, `begrepp_las_*`, plus every widget `key=` in
`utils/modulvy.py` and `sidor/`.

## A4. Proposed design direction

**Visual identity: "a well-edited law review, with a precise instrument panel."** Keep the
parchment, ink, authority blue and statute gold. Sharpen it with a clear split between
reading type and interface type, quieter controls, and stricter emphasis rules.

**Design principles**

1. **The case comes first.** The default content of every exercise is visible before any
   optional control.
2. **One primary action per view.** In an exercise the primary action is the tutor
   review. Generation, answers and unlocking are secondary.
3. **Every citation is a trust object.** Gold means a statute reference, and a reference
   always shows whether it is verified. Generated material says that it is generated.
4. **State is never colour alone.** Every coloured state carries text, a shape or both.
5. **Proximity carries structure.** Use the existing 4 px spacing scale and bordered
   groups instead of dividers and extra headings.
6. **Nothing that looks clickable is inert, and nothing inert is shown as a control.**

**Industry suitability.** Legal readers expect long-form typography, exact citation
format and visible sourcing. Reference products for quality, not appearance:
lagen.nu and Karnov (citation density, statute as primary object), Linear and Stripe
docs (quiet controls, one accent, consistent feedback), Mercury and Wise (plain-language
states, tabular numbers, honest empty states). The brief's fintech references apply in
their discipline, not in their look: no dashboard tiles, gradients or icon rows.

**Rationale.** The current look already signals a legal publication. Modernizing it
means removing amateur signals (wrong fonts on controls, broken markup, competing
primary buttons, dead lists), not replacing the identity.

## A5. Proposed information architecture

The sidebar tree stays as is, by documented decision (`design_system.md` 4.1: the whole
legal system visible at once, no collapsible sections). Changes:

1. **Shorter sidebar header.** Brand title at `--t-h3`, tagline kept, one divider removed.
   Saves about 90 px so the CIVILRÄTT block starts higher.
2. **Phones start with the sidebar closed** (`initial_sidebar_state="auto"`). Desktop is
   unchanged.
3. **Module page headers show where the module sits.** The eyebrow becomes the legal
   chain from `navigation.rubrikkedja`, for example
   "CIVILRÄTT / FÖRMÖGENHETSRÄTT / KONTRAKTSRÄTT" above "Avtalsrätt", instead of
   repeating "AVTALSRÄTT" above "Avtalsrätt".
4. **Kunskapstest becomes a working hub**: every module is a link, in the app's order,
   with progress.
5. **Optional, for review (D5):** move the TRÄNING group directly under START OCH METOD,
   so the cross-module tools are reachable without scrolling past twelve modules. Not in
   the default scope, because it changes a documented ordering.

User journey after the change: Home (next step, progress, exports) to module (case
visible, write, tutor review, facit) to quiz and statute hunt (clear progress) to
Kunskapstest (where to go next) and Rättskartan (orientation).

## A6. Page-by-page redesign specification

### Shell (all pages): `streamlit_app.py`, `utils/ui.py:render_sidebar`, `.streamlit/config.toml`

* **Current.** Serif everywhere, Deploy button in the header, sidebar expanded on phones,
  tall brand block.
* **Problems.** Controls indistinguishable from prose; phone content hidden on load.
* **Proposed.** Theme: `font = "sans-serif"`, `headingFont = "serif"`,
  `codeFont = "monospace"` (all three are fonts bundled with Streamlit, so the "no CDN, no
  font files" rule holds), `borderColor`, `baseRadius`, palette-matched semantic colours
  so `st.success`, `st.error`, `st.warning` and `st.info` use the app's green, red,
  warning and blue. `client.toolbarMode = "minimal"` hides developer chrome.
  `initial_sidebar_state = "auto"`. Compact sidebar header.
* **Responsive.** Sidebar auto-collapses below Streamlit's mobile breakpoint.
* **Unchanged.** Page registry, routing, `registrera_besok`, navigation tree, status line.

### Hem: `sidor/0_Hem.py`

* **Current.** Hero, disclaimer caption, "NÄSTA STEG" with one primary CTA, progress as one
  colon-chained sentence, export section.
* **Problems.** Progress sentence reads as broken; caption at line 121 starts a sentence in
  lower case; the page explains the method in one line only.
* **Proposed.** Keep the hero and CTA exactly. Under the hero, a quiet four-step RNTS strip
  using the existing unused `pipeline_steps` component (text only, not clickable, so it is
  not mistaken for navigation). Progress becomes a row of three stat blocks
  ("Moduler påbörjade", "Rättsfall genomförda", "Rätt på quiz" shown as "5 av 7")
  rendered by a new `stat_rad` component with tabular numerals. Fix the caption sentence.
  Exports unchanged in content, order and emphasis.
* **Responsive.** Stat row wraps to one column under 640 px.
* **Unchanged.** Empty state shows exactly one button and zero downloads
  (`tests/test_hem.py`). CTA logic. Download file names and MIME types.

### Module pages (12): `utils/modulvy.py` via `sidor/1_..15_*.py`

**Header.** Breadcrumb eyebrow (A5 item 3), title, module ingress. Unchanged otherwise.

**Rättsfall tab.**

* **Current order.** TRÄNAR label; difficulty control; two buttons (primary full-width
  "Generera nytt rättsfall", usually disabled "Visa appens rättsfall"); case select; case
  card (46 rem); stepper column (1/4) and form column (3/4) under the card; caption;
  primary tutor button; facit gate.
* **Problems.** The optional LLM generator dominates the default curated content; a
  disabled button is shown in normal use; the case card and the form have different
  widths; the student scrolls away from the facts while writing.
* **Proposed order.**
  1. TRÄNAR label.
  2. "Välj rättsfall" select (full width of the content column).
  3. A secondary group in a bordered container titled "Nytt fiktivt rättsfall": the
     difficulty control and a *secondary* "Generera nytt rättsfall" button in one row,
     with the existing help text as caption. When a generated case is active, the same
     row also shows "Visa appens rättsfall" (secondary). It is no longer rendered disabled
     when there is nothing to go back to.
  4. Case card, with a source line in the metadata: "Appens rättsfall" or "Genererat
     rättsfall, lagrum kontrollerade mot registret". The success notice after generation
     stays.
  5. On wide screens, two columns: left the case card, right the stepper (horizontal,
     above the fields) and the four fields. Below 900 px the columns stack in the same
     order as today.
  6. Caption, then the tutor button as the only primary button in the tab.
  7. Facit gate and facit, unchanged.
* **Unchanged.** Generation only on click, unique case ids per generation, clearing of
  generated state, all widget keys, the facit gate, completion registration, tutor
  caching and stale detection.

**Quiz tab.**

* **Problems.** "Resultat: 0 rätt av 0 besvarade." before anything is answered; dividers
  between 6 to 8 questions; "Rätt!" violates the tone rule in `design_system.md` section 6
  ("Inga utropstecken i bedömningar"); every answered question adds a primary button.
* **Proposed.** Progress line only when something is answered, in the form
  "3 av 8 besvarade, 2 rätt". Each question in `st.container(border=True)`. Correct
  feedback reads "Rätt svar. {förklaring}". The "Förklara med tutorn" button becomes
  secondary (new `primar` parameter on `tutorknapp`, default `True` so other call sites
  are unchanged).
* **Unchanged.** Grading, `registrera_mc_svar`, keys, explanation and chips, tutor prompt
  and underlag.

**Lagrumsjakt tab.**

* **Proposed.** Each task in a bordered container; the hint caption stays under the input.
  The long instruction caption is split into two short sentences.
* **Unchanged.** Live re-grading after first "Rätta", hint, facit gate, keys.

### Rättskartan: `sidor/16_Rattskartan.py`

* **Problems.** Graph starts around 740 px down; legend label "Kurslag (klicka för
  lagen.nu)" and "Internationell rätt & EU-rätt" (the app otherwise avoids course wording
  and ampersands); checkbox help says "kurskarta"; expander labels such as
  "Civilrätt: Förmögenhetsrätt: Kontraktsrätt" read as a broken sentence; Falltypsguide
  clear button sits alone on a row.
* **Proposed.** Put the reference-law checkbox and the view radio on one horizontal row
  (`st.container(horizontal=True)`); turn the intro paragraph into a two-sentence lead.
  Breadcrumb expander labels with " / ". Copy: "Lag i appens register (klicka för
  lagen.nu)", "Internationell rätt och EU-rätt", "Lagar i registret", "en karta med bara de
  lagar appen rättar mot". Search field and clear button on one row in both filter tabs.
  Concept area labels "Avtalsrätt (5 begrepp)".
* **Unchanged.** Three tabs and their order; Trädvy default and first; one clear button per
  filter tab, no page-wide reset (`tests/test_rattskartan_sida.py`); popover for LLM
  deepening; graph JavaScript.

### Kunskapstest: `sidor/9_Kunskapstest.py`

* **Problems.** Results and module list are separate plain-text lists; modules are not
  links and are sorted alphabetically; no progress or percentage; stale docstring
  promising a mixed test "i Dag 3".
* **Proposed.** One list in the app's order (`navigation.övningsmoduler`), each row a
  bordered container: `st.page_link` to the module, "x av y besvarade",
  "z rätt (nn %)" when answered, and `st.progress` for answered share. Empty state via
  `render_info`. Correct the docstring. No mixed test is built (new feature, out of scope).
* **Unchanged.** Data source `alla_resultat`, deterministic counts.

### Kunskapskarta: `sidor/10_Kunskapskarta.py`

* **Proposed.** Replace the prose legend "Guld = lagrum, blå = rättsfall, mörkblå = modul"
  with the existing `.jok-legend` swatch pattern, as `design_system.md` 4.2 requires. The
  count line becomes "3 genomförda rättsfall och 7 lagrum".
* **Unchanged.** Graph, data, empty state.

### Kunskapsutmaning: `sidor/11_Kunskapsutmaning.py`

* **Proposed.** Empty-state notice renders bold correctly (fixed centrally in
  `render_info`). Difficulty control and "Generera nytt rättsfall" on one row under the
  area row. Case card shows the same source line as in modules.
* **Unchanged.** "Överraska mig" picks module only, never level; ids `utmaning-{n}`; shared
  exercise flow.

### Juridisk metod and the other 11 modules

Covered by the module view above; no page-specific changes.

## A7. Component and design system changes

### Colour

Keep every existing palette value. Add tokens for colours that are hard-coded today and
fix two contrast failures:

| Token | Value | Use | Contrast |
|---|---|---|---|
| `--bl` | `#1A2332` | Text, headings | 14.8:1 on parchment |
| `--perg` | `#FAF7F2` | App background | |
| `--panel` | `#FFFFFF` | Cards | |
| `--ram` | `#E5E0D8` | Borders | |
| `--bla` | `#2C5F8A` | Accent, links, primary button | 6.3:1 |
| `--guld` | `#B8860B` | Statute borders, graph law nodes (non-text) | 3.2:1, valid for non-text only |
| `--guld-text` (new) | `#8A6608` | Gold used as **text** (section spans) | 5.3:1 on white, 4.9:1 on parchment |
| `--gra` (new) | `#6B6459` | Metadata, muted labels (replaces 8 hard-coded uses) | 5.5:1 |
| `--gra-dampad` (new) | `#736C5E` | "(kommer)" rows (replaces `#9A9384`, 3.05:1) | 5.2:1 on white, 4.9:1 on parchment |
| `--gron`, `--fel`, `--varn-*` | unchanged | States | as documented |

Theme semantic colours in `config.toml` are set to the same values so native alerts and
widgets follow the palette.

### Typography

| Role | Font | Size token |
|---|---|---|
| Headings, case titles | Serif (theme `headingFont`) | `--t-hero`, `--t-h2`, `--t-h3` |
| Long reading text: scenario, tutor text, concept fields | Serif (explicit on `.jok-case p`, `.jok-tutortext`, `.jok-begrepp .falt p`) | `--t-brod` |
| UI: buttons, labels, inputs, tabs, tables, captions | Sans (theme `font`) | Streamlit default, `--t-ui` in custom blocks |
| Eyebrows, citations, SFS numbers | Mono (theme `codeFont`, `--font-mono`) | `--t-etikett` |
| Numbers in stats and progress | Sans with `font-variant-numeric: tabular-nums` | `--t-h2` value, `--t-etikett` label |

Font stacks move into three tokens (`--font-serif`, `--font-mono`, `--font-sans`) instead of
being repeated 11 times in `utils/css.py`.

### Spacing, radius, elevation

Keep `--s1` to `--s7`. Add `--r1: 6px`, `--r2: 10px`, `--r3: 12px` replacing literal radii,
and one shadow token `--skugga` for cards (today repeated literally). No new shadows.

### Buttons

| Type | When | Example |
|---|---|---|
| Primary | Exactly one per view: the main next step | Home CTA, "Be tutorn granska min analys", "Generera nytt rättsfall" on Kunskapsutmaning (its only action) |
| Secondary | Optional or repeated actions | Generate in module tab, quiz tutor, "Svara", "Rätta", facit gate, clear filters |
| Link (`st.page_link`) | Navigation | Kunskapstest rows, "Öva i modulen" |

### Cards and containers

`render_case`, `render_lagkort`, `render_begreppskort` stay the content cards. Repeated
exercise items (quiz question, statute hunt task, Kunskapstest row) use native
`st.container(border=True)`, which inherits `borderColor` and `baseRadius`.

### Feedback and notices

| Need | Component |
|---|---|
| Immediate grading result | `st.success` or `st.error` (now palette-themed), always with words, never colour alone |
| Missing input | `st.warning` |
| Explanatory or persistent notice, empty states | `render_info` |
| Risk, unverified citations, caps | `render_varning` |

`render_info` and `render_varning` accept `**bold**` safely: text is escaped first, then
only bold and italics are converted, reusing `ui._md_till_html`.

### Reusable components added

| Component | File | Purpose |
|---|---|---|
| `stat_rad(poster)` | `utils/ui.py` | Row of number plus label blocks for Home |
| `kedja_etikett(delar)` | `utils/texter.py` | Join a hierarchy with " / " for eyebrows and expander labels |
| `uppraknad(delar)` | `utils/texter.py` | Swedish list join: "a, b och c" |
| `andel_text(ratt, besvarade)` | `utils/texter.py` | "2 av 3 rätt (67 %)" with non-breaking space before % |
| `.sr-only` CSS class | `utils/css.py` | Visually hidden text for screen readers |

### Charts and graphs

No new chart library. The three vis-network graphs are relational, not quantitative, and
already follow the palette. Only copy and legend changes.

### Libraries evaluated and rejected

| Suggested in brief | Decision | Reason |
|---|---|---|
| Lucide or any icon set | Rejected | Icons are banned app-wide by `design_system.md` 4.1 and `tests/test_sprak.py` |
| Plotly, Altair | Rejected | No quantitative visualisation exists; progress needs only `st.progress` |
| AgGrid | Rejected | One table of about 40 rows; `st.dataframe` already sorts and searches; extra JS dependency and licence tiers for no gain |
| Custom web fonts | Rejected | Streamlit bundles Source Sans, Source Serif and Source Code; project forbids CDN fonts |
| `st.navigation` sections | Rejected | Flat two-level sections cannot express the four-level legal tree the sidebar exists to show |

## A8. Industry-specific improvements (financial brief mapped to the legal domain)

| Brief requirement | Legal equivalent in this app | Change |
|---|---|---|
| Consistent currency and number formatting | Citation format ("36 § AvtL", "3 kap. 1 § ÄB") and score format | Citations already normalised; scores get one helper `andel_text` and tabular numerals |
| Clear distinction between actual, forecast and estimated values | Curated versus generated cases; verified versus unverified citations | Source line on every case card; unverified chips keep "Ej verifierad:" prefix |
| Do not use colour alone for status | Stepper, chips, quiz feedback | Stepper gets hidden text state; chips already have text prefix; quiz feedback is worded |
| Where data comes from | lagen.nu and Riksdagen data | Chips announce "öppnas på lagen.nu i ny flik"; footer keeps disclaimer |
| Which assumptions are used | What a green chip means | `VERIFIERINGSNOT` kept verbatim |
| Tables: alignment, totals, sorting | Falltypsguide, Kunskapstest | Kunskapstest becomes a structured list with progress; Falltypsguide unchanged except layout |
| Trust and credibility | Disclaimer, no legal advice | Kept on Home and every footer |

## A9. Performance and technical improvements

* Reruns: unchanged model. No `st.fragment` in scope: pages render in well under a second
  locally and fragments would change when Home progress refreshes. Listed as deferred.
* Styling: font stacks, greys and radii become tokens; `tests/test_ui.py` gains a guard
  against new literal font stacks in `CSS_MALL`.
* Theme config replaces CSS overrides that would otherwise be needed for native widgets.
* Dead code: `pipeline_steps` is reused on Home rather than deleted.
* `APP_UPDATED` in `utils/ui.py` is stale (2026-07-08); update it as part of the release.

## A10. Feature preservation matrix

| Existing feature | Current implementation | Proposed change | Preserved? | Risk |
|---|---|---|---|---|
| F01 Curated case | Select after generator controls | Select first | Yes | Low |
| F02 RNTS form | Under card, 3/4 column | Right column on wide screens | Yes, same keys | Medium (layout) |
| F03 Norm chips | `_norm_feedback` | None | Yes | None |
| F04 Stepper | Vertical, colour only | Hidden status text | Yes | Low |
| F05 Tutor | Always primary | `primar` parameter, default unchanged | Yes | Low |
| F06 Facit gate | Per task | None | Yes | None |
| F07 Generated case | Primary, top | Secondary group under select, source line | Yes, **D3** | Medium |
| F08 Quiz | Dividers, "Rätt!" | Bordered items, worded feedback, progress line | Yes, **D4** copy | Low |
| F09 Statute hunt | Dividers | Bordered items | Yes | Low |
| F10 Completion | Automatic | None | Yes | None |
| F11 CTA | One primary | None | Yes | None |
| F12 Progress | One sentence | Stat row | Yes | Low |
| F13 Exports | Three downloads | None | Yes | None |
| F14 Sidebar | Tree | Compact header, auto-collapse on phones | Yes | Low |
| F15 Status line | Caption | None | Yes | None |
| F19 to F24 Rättskartan | As listed | Copy, control row, labels | Yes | Low |
| F25 Kunskapskarta | Prose legend | Swatch legend | Yes | Low |
| F26 Kunskapsutmaning | As listed | Layout, fixed notice | Yes | Low |
| F27 Kunskapstest | Text lists | Linked rows with progress | Yes, plus links | Low |
| "Visa appens rättsfall" | Always shown, often disabled | Shown only when a generated case is active | Behaviour preserved, **D7** | Low |

**Decisions for explicit review**

* **D1 Typography.** Sans for UI, serif for headings and long reading text. This restores
  what `design_system.md` section 2 already specifies. Alternative: keep everything serif
  and only fix hierarchy with weight and size.
* **D2 Branch base.** Branch the work from `sakerhet/kostnadsskydd` (recommended, it is the
  latest), or merge it into `main` first and branch from `main`.
* **D3 Rättsfall order.** Curated case first, generation as a secondary group.
* **D4 Copy.** "Rätt!" becomes "Rätt svar." per the tone rule.
* **D5 Sidebar order.** Move TRÄNAR tools up. Not in default scope.
* **D6 Two-column case view.** Case left, form right on wide screens. Sticky case column is
  deferred because it needs CSS on Streamlit's internal `stColumn` element.
* **D7 Hide the disabled "Visa appens rättsfall"** instead of showing an inert button.

No feature is removed. No business logic, data file, prompt, budget rule or session key
changes.

## A11. Expected outcomes

| Improvement | Usability | Consistency | Accessibility | Productivity | Maintainability |
|---|---|---|---|---|---|
| Theme fonts and colours | Controls recognisable as controls | Native and custom widgets match | | | Fewer overrides |
| Rendering fixes | No broken text | | | | Central fix in two functions |
| Case first, one primary | Default task visible, clear next step | Same rule on every page | | Less scrolling while writing | |
| Breadcrumb eyebrows | Student knows where a module sits in the law | | | | Derived from `NAV_TRAD`, no new data |
| Kunskapstest hub | Results lead somewhere | | | One click to the next module | |
| Contrast and semantics | | | AA for all text, state readable without colour | | Guarded by tests |
| Tokens | | One source per colour and font | | | Smaller, guarded CSS |
| Phone sidebar | Content visible on load | | | | Config only |

---

# PART B: STEP-BY-STEP IMPLEMENTATION ROADMAP

## B1. Implementation principles

1. Preserve every feature in A3 and every session key in the A3 key list.
2. One task per commit, conventional prefix in Swedish as the repo already does
   (`feat:`, `fix:`, `refactor:`, `docs:`).
3. Never edit `utils/lagrum.py`, `quiz.py`, `scenarier.py`, `generator.py`,
   `fallkontroll.py`, `granskning.py`, `prompts.py`, `llm.py`, `llm_budget.py` or anything
   in `data/`.
4. Write or extend the test first where behaviour is observable (house rule in README).
5. Run the full gate after every task: `python -m pytest -q`, `python -m ruff check .`,
   `python -m mypy --ignore-missing-imports utils`, `node --test tests/js/`.
6. All user-facing text is Swedish and must pass `tests/test_sprak.py` (no emoji, no
   dashes as punctuation, no middle dot, no course or exam words).
7. No new dependencies.
8. Update `design_system.md` in the same commit as the rule it documents.

## B2. Prioritized task breakdown

| ID | Pri | Task | Files | Depends on | Est. | Risk |
|---|---|---|---|---|---|---|
| T00 | P0 | Branch, baseline gate, baseline screenshots | none in repo | D2 | 0.5 h | Low |
| T01 | P0 | Theme configuration and phone sidebar | `.streamlit/config.toml`, `streamlit_app.py`, `utils/css.py`, `design_system.md` | T00 | 1.5 h | Medium |
| T02 | P0 | CSS tokens and contrast fixes | `utils/css.py`, `utils/ui.py`, `tests/test_ui.py`, `design_system.md` | T01 | 1.5 h | Low |
| T03 | P0 | Safe bold in notices | `utils/ui.py`, `tests/test_ui.py` | T00 | 1 h | Low |
| T04 | P0 | Text helpers and colon-chain copy fixes | `utils/texter.py`, `utils/modulvy.py`, `sidor/0_Hem.py`, `sidor/10_Kunskapskarta.py`, `sidor/16_Rattskartan.py`, `utils/ui.py`, tests | T00 | 1.5 h | Low |
| T05 | P1 | Compact sidebar header | `utils/ui.py`, `utils/css.py` | T01 | 0.75 h | Low |
| T06 | P1 | Breadcrumb eyebrow on module pages | `utils/modulvy.py`, `utils/texter.py`, tests | T04 | 1.25 h | Low |
| T07 | P1 | Accessibility semantics (stepper, chips, links) | `utils/ui.py`, `utils/css.py`, tests | T02 | 1.5 h | Low |
| T08 | P1 | Unify empty states and feedback wording | `utils/modulvy.py`, `sidor/9_Kunskapstest.py` | T03 | 0.75 h | Low |
| T09 | P0 | Rättsfall tab: case first, one primary, source line, two columns | `utils/modulvy.py`, `utils/ui.py`, `utils/tutor.py`, `utils/css.py`, tests | T03, T04 | 3.5 h | Medium |
| T10 | P1 | Quiz tab | `utils/modulvy.py`, `utils/tutor.py`, `utils/texter.py`, tests | T09 | 1.5 h | Low |
| T11 | P1 | Lagrumsjakt tab | `utils/modulvy.py` | T10 | 0.75 h | Low |
| T12 | P1 | Home: stat row and RNTS strip | `sidor/0_Hem.py`, `utils/ui.py`, `utils/css.py`, tests | T04 | 1.5 h | Low |
| T13 | P1 | Kunskapstest hub | `sidor/9_Kunskapstest.py`, `utils/texter.py`, tests | T04, T08 | 1.75 h | Low |
| T14 | P2 | Rättskartan layout and copy | `sidor/16_Rattskartan.py`, `utils/taxonomi_ui.py`, `utils/kraftgraf_ui.py`, tests | T04 | 1.5 h | Low |
| T15 | P2 | Kunskapskarta legend, Kunskapsutmaning layout | `sidor/10_Kunskapskarta.py`, `sidor/11_Kunskapsutmaning.py` | T09 | 1 h | Low |
| T16 | P1 | Responsive pass | `utils/css.py` | T09 to T15 | 1.25 h | Low |
| T17 | P0 | Full regression and visual QA | none or fixes | all | 3 h | n/a |
| T18 | P0 | Documentation and release metadata | `design_system.md`, `README.md`, `APPGUIDE.md`, `utils/ui.py` | T17 | 1.25 h | Low |
| T19 | P3 | Deferred backlog (not scheduled) | | | | |

Total scheduled: about 27 hours, which fits 4.5 working days with buffer for review and
fixes. P2 tasks (T14, T15) are the first to drop if time runs short.

## B3. Five-day schedule

| Day | Tasks | Hours | Exit check |
|---|---|---|---|
| 1 Foundation | T00, T01, T02, T03, T04 | 6 | Gate green; every page renders sans UI with serif headings; no literal asterisks; no colon chains |
| 2 Shell and core semantics | T05, T06, T07, T08, start T09 (layout skeleton) | 6 | Sidebar compact; breadcrumbs on all 12 modules; stepper announces state |
| 3 Core workflow | finish T09, T10, T11 | 5.5 | One primary button per exercise view; case above the fold at 1440 by 900; all keys unchanged |
| 4 Remaining pages and responsive | T12, T13, T14, T15, T16 | 7 | Kunskapstest rows link; Rättskartan graph higher; 390 px layout checked |
| 5 QA and docs | T17, T18 | 4.25 | Regression checklist B5 complete; docs updated |

## B4. Implementation prompts

Every prompt assumes the repository root `juridik_oversiktskurs` and the work branch
created in T00. Each prompt is self-contained.

### T00: Branch and baseline

```
Task T00. Objective: create a safe work branch and record a baseline before any change.

Context: Juridikverkstan is a Streamlit 1.67 app (entry streamlit_app.py, pages in
sidor/, shared UI in utils/ui.py and utils/css.py). The latest code is on branch
sakerhet/kostnadsskydd, two commits ahead of main.

Steps:
1. git status must be clean apart from the untracked folder
   PRIME-A520M-A-II-ASUS-3645/ (not part of the project; do not add or delete it).
2. Create branch feat/ux-modernisering from sakerhet/kostnadsskydd (decision D2; if the
   owner chose to merge to main first, branch from main after that merge).
3. Run and record the counts: python -m pytest -q ; python -m ruff check . ;
   python -m mypy --ignore-missing-imports utils ; node --test tests/js/
   Expected baseline: 1647 passed, 130 skipped.
4. Start the app on a free port (8501 may be busy): python -m streamlit run
   streamlit_app.py --server.port 8617 --server.headless true
5. Take baseline screenshots at 1440x900 and 390x844 of: /, /Juridisk_metod,
   /Avtalsratt (all three tabs), /Rattskartan (all three tabs), /Kunskapstest,
   /Kunskapskarta, /Kunskapsutmaning. Save them OUTSIDE the repo.

Must stay intact: everything. No source edits in this task.
Acceptance: branch exists, baseline numbers written in the task log, screenshots saved.
Done when: all four gate commands pass on the new branch with no edits.
```

### T01: Theme configuration and phone sidebar

```
Task T01. Objective: make Streamlit's own theme carry the design system so native
widgets match the app, and stop the sidebar covering content on phones.

Context: .streamlit/config.toml sets font = "serif", so every control renders in serif,
contradicting design_system.md section 2 (UI in sans, headings in serif). Streamlit 1.67
supports headingFont, codeFont, borderColor, baseRadius, linkColor and per-colour
semantic keys (greenColor, redColor, yellowColor, blueColor and their Background and
Text variants). The fonts "sans-serif", "serif" and "monospace" are bundled with
Streamlit, so no CDN or font file is introduced.

Files: .streamlit/config.toml, streamlit_app.py, utils/css.py, design_system.md.

Requirements:
1. config.toml [theme]: font = "sans-serif"; headingFont = "serif";
   codeFont = "monospace"; keep primaryColor, backgroundColor,
   secondaryBackgroundColor, textColor; add borderColor = "#E5E0D8";
   baseRadius = "0.5rem"; linkColor = "#2C5F8A"; greenColor = "#2E7D4F";
   redColor = "#B3402A"; yellowColor = "#8A6914"; blueColor = "#2C5F8A";
   greenBackgroundColor = "#EAF4EE"; redBackgroundColor = "#FBEDEA";
   yellowBackgroundColor = "#FFF8E1"; blueBackgroundColor = "#EAF1F7".
   Keep the existing explanatory comment style (Swedish, purpose of each block).
2. config.toml [client]: add toolbarMode = "minimal". Keep showErrorDetails = "none".
3. streamlit_app.py: initial_sidebar_state="auto" (desktop stays expanded, phones start
   collapsed).
4. utils/css.py: long reading text keeps serif explicitly. Add
   font-family: Georgia, "Iowan Old Style", "Times New Roman", serif to .jok-case p,
   .jok-tutortext and .jok-begrepp .falt p (T02 will turn the stack into a token).
5. design_system.md section 1 and 2: document the theme keys and the rule
   "UI sans, headings and long reading text serif, citations mono".

Must stay intact: all colours, all CSS classes, all tests.
Constraints: no new dependency, no font files, no CDN.
Visual expectation: buttons, tabs, labels, inputs and tables in sans; h1 to h3 and
scenario text in serif; st.success, st.error, st.warning, st.info in palette colours.
Tests: full gate. Add a test in tests/test_ui.py that parses .streamlit/config.toml with
tomllib and asserts font, headingFont and codeFont values, so the regression that
caused this task cannot return silently.
Acceptance: screenshots at 1440 and 390 px show sans controls and serif headings; on 390
px the sidebar is closed on first load of every page.
Done when: gate green and design_system.md updated in the same commit.
```

### T02: CSS tokens and contrast

```
Task T02. Objective: replace repeated literals in utils/css.py with tokens and fix two
WCAG AA failures.

Context: CSS_MALL in utils/css.py repeats the serif stack and mono stack about 11 times,
the grey #6B6459 eight times, and literal radii and one card shadow. Measured contrast:
.jok-lagkort .avsnittsrad .spann uses gold #B8860B as text, 3.25:1 on white (fails AA
for 13 px). .jok-nav-kommer uses #9A9384, 3.05:1 on white (fails).
tests/test_ui.py already guards that font-size uses tokens.

Files: utils/css.py, utils/ui.py (palette constants and inject_css format call),
tests/test_ui.py, design_system.md.

Requirements:
1. In :root add --font-serif, --font-mono, --font-sans (system-ui stack),
   --gra: #6B6459, --gra-dampad: #736C5E, --guld-text: #8A6608, --r1: 6px, --r2: 10px,
   --r3: 12px, --skugga: 0 1px 3px rgba(26,35,50,.06).
2. Replace every literal serif or mono stack, every #6B6459, every border-radius of 6,
   8 to 10 and 12 px, and both card shadows with the tokens. Keep 999px pills literal.
3. .jok-lagkort .avsnittsrad .spann: color var(--guld-text).
   .jok-nav-kommer: color var(--gra-dampad).
4. Verify both new pairs reach at least 4.5:1 against #FFFFFF and #FAF7F2 with a small
   contrast helper in the test (relative luminance formula), and assert it.
5. Add a test: CSS_MALL contains no literal "Georgia" or "ui-monospace" outside the
   :root block.
6. design_system.md: list the new tokens in section 1 and 2.2.

Must stay intact: every class name and visual role; gold still means statute.
Constraints: tokens only inside utils/css.py; components.html iframes (graph files) are
out of scope by the documented exception.
Acceptance: visual diff against baseline shows no change except the two contrast fixes.
Done when: gate green, including the new tests.
```

### T03: Safe bold in notices

```
Task T03. Objective: stop literal ** from appearing in notices.

Context: utils/ui.py render_varning and render_info html.escape the text and render it
with st.html, so markdown is shown raw. Callers pass bold markup:
sidor/11_Kunskapsutmaning.py (empty-state notice) and utils/modulvy.py
(reservhanvisning "Tryck på **Jag har försökt, visa facit** nedan så länge.", rendered
through utils/tutor.py render_varning). utils/ui.py already has _md_till_html, which
converts bold and italics in escaped text.

Files: utils/ui.py, tests/test_ui.py.

Requirements:
1. Add a pure function _notis_html(text) that escapes, then converts only **bold** and
   *italic* using the same regexes as _md_till_html (do not apply RNTS heading styling).
2. render_varning and render_info use it. Signatures unchanged.
3. Tests: bold becomes <strong>, no asterisks remain, HTML in the input is still escaped
   (<script> stays inert), plain text is unchanged.

Must stay intact: every call site, escaping of untrusted text.
Acceptance: Kunskapsutmaning empty state shows bold button names; tutor fallback
notice shows bold "Jag har försökt, visa facit".
Done when: gate green.
```

### T04: Text helpers and colon chains

```
Task T04. Objective: replace colon-as-separator strings with correct Swedish and add
small text helpers used by later tasks.

Context: after the middle dot was banned, several strings use ": " as a separator:
- utils/modulvy.py rendera_case_ovning metadata:
  "Svårighetsgrad: {nivå}: ca {n} min"
- sidor/0_Hem.py _render_framsteg: ": ".join(delar)
- utils/ui.py footer_note: "Version {v}: uppdaterad {d}."
- sidor/16_Rattskartan.py area expanders ": ".join((*vag, lov.namn)) and concept
  expanders "{namn}: {n} begrepp"
- sidor/10_Kunskapskarta.py count caption
Also sidor/0_Hem.py caption: "Stänger du fliken är de borta. ladda ner dem nedan..."
(lower-case sentence start).

Files: utils/texter.py, the files above, tests/test_texter.py (create if missing) and
existing tests that assert the old strings (search tests/ for each string first).

Requirements:
1. utils/texter.py: uppraknad(delar) -> "a", "a och b", "a, b och c";
   kedja_etikett(delar, avdelare=" / ") ; andel_text(ratt, besvarade) ->
   "2 av 3 rätt (67 %)" with a non-breaking space U+00A0 before % and integer rounding;
   besvarade == 0 raises ValueError.
2. Metadata: "Svårighetsgrad {nivå}, cirka {n} minuter".
3. Home: "3 moduler påbörjade, 2 rättsfall genomförda och 5 av 7 rätt på quiz" via
   uppraknad (T12 later replaces this with a stat row; keep the helper).
4. Footer: "Version 0.1.0, uppdaterad 2026-07-08."
5. Rättskartan: kedja_etikett for area expanders; concept expanders "Avtalsrätt (5 begrepp)".
6. Kunskapskarta: "3 genomförda rättsfall och 7 lagrum."
7. Fix the lower-case sentence: "... är de borta. Ladda ner dem nedan för att behålla dem."

Must stay intact: meaning of every string, Swedish agreement via antal_med_enhet.
Constraints: tests/test_sprak.py rules.
Tests: unit tests for the three helpers; update any test asserting old strings.
Acceptance: grep for '": ".join' in sidor/ and utils/ returns nothing user-facing.
Done when: gate green.
```

### T05: Compact sidebar header

```
Task T05. Objective: shorten the sidebar header so more of the tree is visible.

Context: utils/ui.py render_sidebar renders an h2 brand inside .jok-section, a caption,
st.divider(), the tree, st.divider(), the status line. At 900 px height the CIVILRÄTT
group starts around y=630.

Files: utils/ui.py, utils/css.py, tests/test_ui.py if they assert structure.

Requirements:
1. Replace the brand markup with <div class="jok-varumarke"><div class="namn">
   Juridikverkstan</div><div class="tagline">Fallbaserad träning med RNTS-metoden.
   </div></div>. .namn uses --font-serif at --t-h3, weight 700; .tagline --t-etikett,
   color var(--gra).
2. Remove the first st.divider(); keep the one above the status line.
3. Reduce top margin of the first .jok-nav-kategori to var(--s3) via
   .jok-varumarke + div .jok-nav-kategori or an equivalent first-child rule, without
   changing the spacing scale between groups.

Must stay intact: tree content, active chain, "(kommer)" rows, status line.
Acceptance: at 1440x900 the CIVILRÄTT heading is at least 80 px higher than baseline.
Done when: gate green.
```

### T06: Breadcrumb eyebrow on module pages

```
Task T06. Objective: module headers show where the module sits in the legal system.

Context: every module page calls rendera_modulsida(filnamn, titel, undertitel) where
undertitel repeats the title in capitals ("AVTALSRÄTT" above "Avtalsrätt").
utils.navigation.rubrikkedja(titel) returns the ancestor chain, e.g.
("CIVILRÄTT", "Förmögenhetsrätt", "Kontraktsrätt").

Files: utils/modulvy.py, tests (tests/test_ui.py or a new tests/test_modulrubrik.py).

Requirements:
1. In rendera_modulsida compute kedja = rubrikkedja(titel). If non-empty, eyebrow =
   kedja_etikett([d.upper() for d in kedja]); otherwise fall back to undertitel or
   "MODUL" as today.
2. Keep the undertitel parameter and all 12 page shells unchanged.
3. Test: Avtalsrätt gives "CIVILRÄTT / FÖRMÖGENHETSRÄTT / KONTRAKTSRÄTT"; Juridisk metod
   gives "START OCH METOD"; an unknown title falls back to undertitel.

Must stay intact: the failure path that still renders the hero when scenario loading
fails (tests/test_ui.py test_modulsida_ritar_hero_aven_om_inlasningen_misslyckas).
Done when: gate green; all 12 module pages checked visually.
```

### T07: Accessibility semantics

```
Task T07. Objective: state and links are understandable without colour or sight.

Context: render_rnts_steg in utils/ui.py renders an empty span per step with a class for
state. Chips and law-card links are <a target="_blank"> without rel or notice.

Files: utils/ui.py, utils/css.py, tests/test_ui.py.

Requirements:
1. Add .sr-only (standard visually-hidden pattern) to CSS_MALL.
2. render_rnts_steg: after the label add <span class="sr-only">, {status text}</span>
   with texts: ej påbörjad, pågår, godkänd, behöver mer. Wrap the list in
   <div class="jok-rnts" role="list" aria-label="RNTS-steg"> and each step role="listitem".
3. Every <a ... target="_blank"> produced in utils/ui.py (lagrum chip, tutor chips,
   law card link, section spans) gets rel="noopener noreferrer" and the visible text
   unchanged plus <span class="sr-only"> (öppnas på lagen.nu i ny flik)</span>.
4. Add :focus-visible outline 2px solid var(--bla) with 2px offset for .jok-chip and
   .jok-lagkort a.
5. Tests: each state's text is present; rel present on every anchor from
   render_lagrum_chip, _tutortext_html, render_lagkort; existing tests that compare exact
   HTML are updated, not deleted.

Must stay intact: chip replacement logic in _tutortext_html (longest match first),
escaping, VERIFIERINGSNOT.
Done when: gate green; keyboard Tab reaches chips with a visible ring.
```

### T08: Empty states and feedback

```
Task T08. Objective: one visual language for empty states.

Context: utils/modulvy.py uses st.info for "Inga rättsfall/quizfrågor/Ingen lagrumsjakt
i den här modulen ännu." and sidor/9_Kunskapstest.py uses st.info for its empty state,
while other pages use render_info.

Files: utils/modulvy.py, sidor/9_Kunskapstest.py, related tests.

Requirements: replace those four st.info calls with render_info, same text. Keep
st.success, st.error and st.warning for grading feedback (they are palette-themed after
T01). Document the rule table from plan section A7 "Feedback and notices" in
design_system.md section 3.
Done when: gate green.
```

### T09: Rättsfall tab

```
Task T09. Objective: the case is the first content, generation is secondary, the tutor
is the only primary action, and generated cases are labelled.

Context (utils/modulvy.py _rendera_rattsfall and rendera_case_ovning): order today is
TRÄNAR label, svarighetsvaljare, two columns with primary "Generera nytt rättsfall"
(key gen_knapp_{filnamn}) and "Visa appens rättsfall" (key kur_knapp_{filnamn},
disabled when no generated case), selectbox "Välj rättsfall" (key case_val_{modul}),
then rendera_case_ovning: render_case card, columns [1,3] stepper and form, caption,
tutorknapp (primary), facit gate. rendera_case_ovning is shared with
sidor/11_Kunskapsutmaning.py. Generation must happen only on click (a rerun happens on
every keystroke in the form).

Files: utils/modulvy.py, utils/ui.py (render_case), utils/tutor.py, utils/css.py,
tests/test_ui.py and module view tests.

Requirements:
1. New order in _rendera_rattsfall when no generated case is active:
   TRÄNAR label; selectbox "Välj rättsfall"; bordered container with caption
   "Nytt fiktivt rättsfall" containing svarighetsvaljare and a SECONDARY
   "Generera nytt rättsfall" button in one horizontal row
   (st.container(horizontal=True, vertical_alignment="bottom")); then the case.
2. When a generated case is active: same container, plus secondary
   "Visa appens rättsfall"; the curated selectbox is not shown (as today).
   Do not render "Visa appens rättsfall" when no generated case exists (decision D7).
3. Keep every key, label, help text, spinner text and the click-only generation logic
   byte-for-byte except button type.
4. render_case gets an optional kalla: str = "" argument; when given it is appended to
   the meta line. rendera_case_ovning passes "Appens rättsfall" for curated cases and
   "Genererat rättsfall, lagrum kontrollerade mot registret" when the case id contains
   "-gen-" or starts with "utmaning-" AND the stored source is "genererad". Read the
   source from the existing session keys gen_kalla_{filnamn} / utmaning_kalla; pass it
   in as a new optional parameter kalla to rendera_case_ovning (default ""), so
   Kunskapsutmaning can pass its value too.
5. Layout in rendera_case_ovning: st.columns([5, 6], gap="large"). Left: case card.
   Right: stepper rendered horizontally (add .jok-rnts.vagrat modifier: flex row, wrap,
   gap var(--s4)) above the four fields. Streamlit stacks columns on narrow screens.
   Remove max-width from .jok-case inside a column only if it overflows; verify.
6. tutorknapp gets primar: bool = True; button type "primary" if primar else
   "secondary". Case view keeps True.
7. Tests: generation is not called on rerun without click (existing tests must still
   pass); "Visa appens rättsfall" absent without a generated case and present with one;
   render_case shows kalla; tutorknapp(primar=False) renders a secondary button (AppTest).

Must stay intact: facit gate, completion registration when all four fields are filled,
tutor caching and stale notice, keys rnts_{case.id}_{falt}, case ids
"{filnamn}-gen-{n}" and "utmaning-{n}", success and warning notices after generation.
Visual: at 1440x900 the case title is above the fold on /Avtalsratt; exactly one primary
button in the tab.
Done when: gate green; manual run through: write all four fields, ask tutor (or see the
unavailable notice offline), unlock facit, generate a case, go back to curated.
```

### T10: Quiz tab

```
Task T10. Objective: quieter, clearer quiz with progress and correct tone.

Context: utils/modulvy.py _rendera_quiz and _rendera_quizfraga. Today: "Resultat: X rätt
av Y besvarade." always shown, st.divider between questions, st.success("Rätt! ...")
and a primary tutor button after each answer.

Files: utils/modulvy.py, utils/texter.py (andel_text from T04), tests.

Requirements:
1. Show progress only when besvarade > 0: "{besvarade} av {antal} besvarade, {ratt} rätt".
2. Wrap each question in st.container(border=True); remove the dividers.
3. Correct feedback: st.success(f"Rätt svar. {res.forklaring}"). Wrong feedback text
   unchanged.
4. tutorknapp(..., primar=False) for "Förklara med tutorn".
5. Tests: no progress line with zero answers; line present after one answer (AppTest);
   no "!" in correct feedback.

Must stay intact: keys quiz_val_*, quiz_svara_*, quiz_klart_*, quiz_forklara_*,
registrera_mc_svar, chips, underlag, warning when no option is chosen.
Done when: gate green.
```

### T11: Lagrumsjakt tab

```
Task T11. Objective: each statute-hunt task reads as one unit.

Context: utils/modulvy.py _rendera_lagrumsjakt and _rendera_jaktfraga, separated by
st.divider. The instruction caption is one long paragraph.

Requirements:
1. Each task in st.container(border=True); remove dividers.
2. Split the caption into: "Skriv vilket lagrum situationen handlar om. Rättningen kräver
   ingen tutor." and a second caption: "Paragraftecknet behövs inte: \"3 paragrafen
   skuldebrevslagen\" fungerar lika bra som \"3 § SkbrL\"."
Must stay intact: live re-grading after first click (see the comment in
_rendera_jaktfraga), hint, facit gate, keys jakt_svar_*, jakt_ratta_*, jakt_rattad_*.
Done when: gate green.
```

### T12: Home

```
Task T12. Objective: Home explains the method at a glance and shows progress as numbers.

Context: sidor/0_Hem.py. utils/ui.py has an unused pipeline_steps(steps) component and
the .jok-pipeline class. tests/test_hem.py asserts the empty state has exactly one
button and zero downloads.

Requirements:
1. Under the disclaimer caption, render pipeline_steps(list(RNTS_STEG)) (text only).
2. Add stat_rad(poster: tuple[tuple[str, str], ...]) -> str in utils/ui.py rendering
   <div class="jok-stat-rad"> with one <div class="jok-stat"><div class="tal">..</div>
   <div class="etikett">..</div></div> per item. CSS: flex, wrap, gap var(--s5); .tal
   --font-serif, --t-h2, tabular-nums; .etikett --t-etikett, color var(--gra).
3. Progress section: stat_rad((str(moduler), "moduler påbörjade"),
   (str(fall), "rättsfall genomförda"), and when besvarade > 0
   (f"{ratt} av {besvarade}", "rätt på quiz")). Use antal_med_enhet for singular forms.
4. Keep the session-honesty caption and the export section exactly.
Tests: stat_rad escapes input; empty state still one button and zero downloads.
Done when: gate green.
```

### T13: Kunskapstest hub

```
Task T13. Objective: results lead to the next action.

Context: sidor/9_Kunskapstest.py prints results sorted alphabetically and a separate
non-clickable module list. utils.navigation.övningsmoduler() gives modules in app order
with their page paths; utils.quiz.alla_resultat() gives name -> (rätt, besvarade);
utils.scenarier.ladda_modul(stem).flervalsfragor gives question counts; module display
names equal navigation names (guarded by tests/test_navigation.py).

Requirements:
1. Build a dict name -> question count from lista_moduler()/ladda_modul (skip broken
   files as today).
2. For each module in övningsmoduler() with at least one question: a bordered container
   with st.page_link(modul.sida, label=modul.namn), a caption
   "{besvarade} av {antal} besvarade" plus ", " + andel_text(...) when answered, and
   st.progress(besvarade / antal).
3. Empty state (no answers anywhere) shown above the list via render_info, list still
   shown so the page is never a dead end.
4. Update the module docstring: remove the "Dag 3" promise.
Tests (AppTest): every row has a page link; order equals övningsmoduler order.
Done when: gate green.
```

### T14: Rättskartan

```
Task T14. Objective: graph higher on the page, consistent copy.

Files: sidor/16_Rattskartan.py, utils/taxonomi_ui.py, utils/kraftgraf_ui.py, tests.

Requirements:
1. Put the referenslagar checkbox and the "Kartans vy" radio in one
   st.container(horizontal=True, vertical_alignment="bottom").
2. Shorten the overview paragraph to two sentences, same facts.
3. Copy: "Kurslag (klicka för lagen.nu)" -> "Lag i appens register (klicka för
   lagen.nu)"; "Internationell rätt & EU-rätt" -> "Internationell rätt och EU-rätt";
   "Kurslagar" -> "Lagar i registret"; checkbox help "en ren kurskarta" -> "en karta med
   bara de lagar appen rättar mot". Search tests/ and utils/static/*.js for these
   strings and update consistently.
4. Falltypsguide and Nyckelbegrepp: search input and clear button on one horizontal row.
Must stay intact: tab order, Trädvy default and first option, one clear button per filter
tab, no page-wide reset, popover deepening, tests/test_rattskartan_sida.py.
Done when: gate green, including node tests.
```

### T15: Kunskapskarta and Kunskapsutmaning

```
Task T15. Objective: legend as swatches; compact challenge controls.

Requirements:
1. sidor/10_Kunskapskarta.py: replace the prose legend with a .jok-legend block of three
   .jok-swatch entries using the colours in utils/graf_ui.py _FARGER (lagrum, rättsfall,
   modul). Keep the count caption from T04.
2. sidor/11_Kunskapsutmaning.py: put svarighetsvaljare and the primary
   "Generera nytt rättsfall" button in one horizontal container; pass kalla from
   st.session_state["utmaning_kalla"] to rendera_case_ovning (T09 parameter).
Must stay intact: "Överraska mig" picks module only; ids utmaning-{n}; notices.
Done when: gate green.
```

### T16: Responsive pass

```
Task T16. Objective: verified layout at 390 px and 768 px.

Requirements:
1. Add @media (max-width: 640px) rules in CSS_MALL: .jok-hero h1 uses --t-h2;
   .jok-case and .jok-lagkort padding var(--s4); .jok-stat-rad gap var(--s4);
   .jok-lagkort .avsnittsrad .spann flex-basis 5rem.
2. Check every page at 390x844 and 768x1024: no horizontal scroll
   (document.documentElement.scrollWidth <= innerWidth), sidebar closed on load, case,
   form and buttons usable. Graph iframes keep fixed height (documented limitation).
Done when: screenshots saved outside the repo and gate green.
```

### T17: Regression and visual QA

```
Task T17. Objective: prove nothing broke.

Steps: run the full gate; run every item in plan section B5; compare screenshots with
the T00 baseline page by page; fix defects in the task that caused them (separate fix
commit referencing the task id). Offline mode (no HF_TOKEN) must show the tutor
unavailable notice and everything deterministic must work.
Done when: every B5 box is ticked or a defect is logged with a reason.
```

### T18: Documentation and release metadata

```
Task T18. Objective: docs match the shipped UI.

Requirements: design_system.md sections 1 to 4 reflect tokens, theme keys, button rule,
feedback table, module page order, Kunskapstest hub. README.md test count updated to the
actual number. APPGUIDE.md: search for descriptions of the Rättsfall tab order, Home
progress text and Kunskapstest and update them. utils/ui.py APP_UPDATED set to the
release date. Remove UX_UI_MODERNIZATION_PLAN.md or move it under docs/ only if the
owner asks.
Done when: gate green (tests/test_sprak.py scans all .md files).
```

### T19: Deferred backlog (P3, not scheduled)

* Sticky case column on wide screens (needs CSS on `[data-testid="stColumn"]`).
* Dark theme via `[theme.dark]` (all `.jok-*` colours would need dark tokens).
* `render_sidhjalp` on every page, as `design_system.md` 4.3 promises.
* Graph label legibility at fit zoom in Trädvy.
* `st.fragment` for quiz items.
* Mixed quiz across modules (a new feature, not modernization).
* D5 sidebar regrouping.

## B5. Testing and regression checklist

### Automated

- [ ] `python -m pytest -q` passes, count at least baseline plus new tests
- [ ] `python -m ruff check .` clean
- [ ] `python -m mypy --ignore-missing-imports utils` clean
- [ ] `node --test tests/js/` passes
- [ ] `tests/test_sprak.py` passes on all changed files, including this plan

### Startup and navigation

- [ ] App starts with and without `HF_TOKEN`
- [ ] All 17 pages open from the sidebar; active chain highlighted
- [ ] Home CTA goes to the next unstarted module; resume link appears after visiting one
- [ ] "Öva i modulen" links in Nyckelbegrepp open the right module
- [ ] Kunskapstest rows open the right module
- [ ] Direct URLs (`/Avtalsratt`, `/Rattskartan`) render with sidebar and CSS

### Feature by feature (from A3)

- [ ] F01 Every curated case selectable in all 12 modules
- [ ] F02 Text persists across tab switches and reruns; 2000 character limit
- [ ] F03 "36 § AvtL" gives a gold chip; a fake paragraph gives "Ej verifierad:" and warning
- [ ] F04 Stepper changes state per field; screen reader text present
- [ ] F05 Tutor: unavailable notice offline; with token, review renders chips; edit makes it stale; "Uppdatera förklaringen" works; cap cards render
- [ ] F06 Facit hidden until "Jag har försökt, visa facit"; per task, survives reruns
- [ ] F07 Generate in each difficulty; fallback notice when grounding fails; "Visa appens rättsfall" returns; source line correct
- [ ] F08 Quiz answer, warning without choice, explanation, chips, tutor button secondary
- [ ] F09 Statute hunt: correct, wrong, unknown law, empty, hint, live re-grade, facit
- [ ] F10 Completing four fields increments Home count and Kunskapskarta
- [ ] F11 to F13 Home progress, exports download and open (zip in Obsidian, md, xlsx)
- [ ] F14 Sidebar tree complete, "(kommer)" rows, phone collapse
- [ ] F15 Status line normal and low-budget states
- [ ] F19 Trädvy: focus branch, open law, reset view
- [ ] F20 Kraftvy: search, filter, info panel, double click opens law
- [ ] F21 Reference-law toggle changes graph and area list
- [ ] F22 Area expanders, law cards, section spans link to lagen.nu
- [ ] F23 Falltypsguide search, count line, clear button
- [ ] F24 Concepts: search, area filter, clear, popover both modes, "Se även"
- [ ] F25 Kunskapskarta empty state and populated graph with swatch legend
- [ ] F26 Kunskapsutmaning: area, "Överraska mig", difficulty, generate, full exercise
- [ ] F27 Kunskapstest rows, progress, percentages

### Data, calculation and state

- [ ] Quiz totals on module tab, Home and Kunskapstest agree
- [ ] Percentages rounded consistently, "%" preceded by a non-breaking space
- [ ] No session key renamed (grep diff for `key=`)

### Accessibility

- [ ] All text pairs at least 4.5:1 (re-run contrast test)
- [ ] Keyboard: Tab reaches sidebar links, tabs, inputs, buttons, chips with visible focus
- [ ] No state conveyed by colour alone
- [ ] External links announce new tab

### Responsive and browser

- [ ] 1440x900, 768x1024, 390x844: no horizontal scroll, sidebar behaviour correct
- [ ] Chromium (Edge or Chrome) and Firefox

## B6. Rollback strategy

1. **Preserve the original.** `sakerhet/kostnadsskydd` and `main` are never committed to
   during this work. Optionally tag the base: `git tag pre-ux-modernisering fd5c833`.
2. **Separate branch.** All work on `feat/ux-modernisering`.
3. **Traceability.** One commit per task, message prefixed with the task id, for example
   `fix: T03 visa fetstil i notiser utan asterisker`. `git log --oneline --grep T09` lists
   a task's commits.
4. **Revert one change.** `git revert <sha>` for a single task. Tasks are ordered so later
   tasks depend on earlier ones only through the helpers in T03 and T04 and the
   `tutorknapp(primar=...)` and `rendera_case_ovning(kalla=...)` parameters; reverting
   T09 also requires reverting T10 and T15 or keeping those parameters.
5. **Config-only rollback.** T01 is isolated in `.streamlit/config.toml` and one argument
   in `streamlit_app.py`; reverting it restores the old look instantly.
6. **Failed implementation.** If a task breaks the gate and cannot be fixed within its
   estimate, `git reset --hard` to the previous task's commit on the work branch (never on
   a shared branch), log the task as deferred, continue with the next independent task.
7. **Release.** Merge with a pull request into `main` only after T17. Keep the branch until
   the deployed app has been checked on Streamlit Community Cloud.

---

## Stage 4: Internal review of this plan

* **Coverage.** All 17 registered pages are covered: the 12 module pages through the
  shared view, and Hem, Rättskartan, Kunskapstest, Kunskapskarta and Kunskapsutmaning
  individually. The stray untracked `pages/` folder (only `__pycache__`) and the BIOS
  folder in the repo root are outside the app and untouched.
* **Overlooked features checked.** Exports, budget caps, reference-law toggle, Kraftvy
  search and filter, concept popover modes, "Överraska mig", completion registration,
  stale tutor detection: all present in A3 and B5.
* **Conflicts with existing rules.** The brief's icon, chart-library and table-library
  suggestions conflict with project rules or add nothing; rejected with reasons in A7.
  Centred column and collapsible navigation were already tried or ruled out; not
  reproposed. Gold remains statute-only.
* **Technical compatibility.** Every API used exists in the installed Streamlit 1.67:
  `headingFont`, `codeFont`, semantic colour keys, `toolbarMode`,
  `st.container(horizontal=True, border=True)`, `st.page_link`, `st.progress`. Checked
  against `streamlit config show` and the installed package. `requirements.txt` only
  requires `streamlit>=1.50`. CI and Streamlit Cloud install the latest release, so this
  works in practice, but T01 must check the release notes for the first version that
  supports each theme key and `st.container(horizontal=True)`, and raise the floor in
  `requirements.txt` if any of them is newer than 1.50.
* **Estimates.** About 27 hours over 4.5 days, the riskiest task (T09) scheduled across
  two days. P2 tasks can be dropped without affecting P0 and P1.
* **Risk to functionality.** Highest in T09 (layout and button order in the shared
  exercise view). Mitigated by keeping every key and label, adding AppTest coverage and a
  scripted manual run.

## Stop for approval

Implementation starts only after the owner approves this plan and answers decisions
D1 to D7 (defaults: D1 yes, D2 branch from `sakerhet/kostnadsskydd`, D3 yes, D4 yes,
D5 no, D6 yes, D7 yes).

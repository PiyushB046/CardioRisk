# Warm Minimal UI: Design System Spec

> **For Claude (or any developer) reading this:** this file fully specifies a UI style. Your job is to
> reproduce it *exactly* in the current project. Use the tokens, CSS, and JS in this file verbatim
> wherever possible, then adapt only the **content** (brand name, copy, data, pages) to this project.
> Do not invent new colours, fonts, radii, shadows, or easing curves. If something isn't covered here,
> derive it from the tokens and principles in §1–§3.

---

## 0. How to apply this to a project (checklist)

1. Read the project's existing frontend to see the stack (plain HTML, React, Next.js, Vue, Svelte, etc.).
2. **Pick a colour theme** (§2.1): **Theme A, Terracotta** (default; warm, editorial, general-purpose)
   or **Theme B, Rose** (healthcare, wellness, care, anything with a heart/people focus). If the user
   doesn't say, choose by domain. Then add the **fonts** (§2.2) and that theme's **tokens** globally.
   Only the token values differ between themes; every other rule in this file applies to both.
3. Add the **pre-paint theme script** (§6.1) in `<head>` before any CSS paints.
4. Paste the **base + component CSS** (§4). In a Tailwind project, still keep the CSS variables and map
   Tailwind colours to them (§9).
5. Build the **nav** (§5.1), then pages using the **page anatomy** (§5).
6. Wire up the **JS behaviours** (§6): theme toggle, router or active-link state, scroll reveal,
   count-up, toasts, loading buttons.
7. If there are charts, apply the **chart theming** (§7).
8. Verify with the **QA checklist** (§10): light and dark mode, 375px mobile with no horizontal
   scroll, reduced motion, keyboard focus.

---

## 1. Design philosophy

- **Warm minimal.** Off-white "paper" canvas, near-black warm ink, one accent colour (terracotta in
  Theme A, rose in Theme B). No pure
  white backgrounds (cards are white; the page is not). No pure black.
- **Quiet, confident, editorial.** Big tight headlines, generous whitespace, muted secondary text, and
  hairline (1px) borders instead of heavy shadows.
- **One accent, used sparingly:** primary buttons, eyebrow labels, active nav underline, key numbers,
  icons, and the second line of headlines. Everything else is ink, muted, or subtle.
- **Numbers are monospace** (Geist Mono with tabular figures). Text is Geist.
- **Two-line headlines.** Line 1 in ink, line 2 in accent (hero) or subtle grey (section headings).
  Example: "Two sides. / *One quiet handshake.*"
- **Motion is short and eased:** 150–260ms for UI state, 600ms for scroll reveals, about 1s for number
  count-ups and gauges. Always one easing curve: `cubic-bezier(0.2, 0.7, 0.2, 1)`.
- **Decoration is minimal:** a subtle dot-grid background on hero and CTA blocks, a pulsing "live"
  dot, and an orbiting dot on the logomark. Nothing else.
- **Copy tone:** short, calm, declarative. "Three quiet steps." "Honest scores." "No hidden X."

---

## 2. Foundations

### 2.1 Colour tokens: Theme A, Terracotta (default; exact values, define on `:root` and `.dark`)

```css
:root {
  --canvas:   #FAFAF7;  /* page background (warm off-white) */
  --surface:  #FFFFFF;  /* cards, inputs on focus, ghost buttons */
  --surface2: #F5F4EF;  /* inputs, table-row hover, tracks, subtle fills */
  --ink:      #1A1A18;  /* primary text */
  --muted:    #6B6B66;  /* secondary text, nav links, body copy in cards */
  --subtle:   #9E9C95;  /* tertiary: table headers, hints, units, headline line-2 grey */
  --hair:     #E8E6E0;  /* 1px borders, grid lines, dot-grid dots */
  --hairS:    #D6D3CA;  /* stronger hairline: hover borders */
  --accent:        #B85C38;               /* terracotta */
  --accent-hover:  #A24F30;
  --accent-soft:   rgba(184,92,56,0.10);  /* tinted backgrounds, focus glow, selection */
  --on-accent:     #FFFFFF;               /* text/icons on accent-filled buttons */
  --ok:     #4A8A5C;  /* success / low risk / positive */
  --warn:   #B07A2D;  /* warning / medium */
  --danger: #B0413E;  /* error / high risk / negative */
  --ease: cubic-bezier(0.2,0.7,0.2,1);
  --shadow: 0 1px 2px rgba(20,20,18,.04), 0 8px 24px -12px rgba(20,20,18,.10);
}
.dark {
  --canvas:   #141412;
  --surface:  #1A1A17;
  --surface2: #211F1C;
  --ink:      #EDEAE2;
  --muted:    #9A968B;
  --subtle:   #6D6A62;
  --hair:     #2A2823;
  --hairS:    #3A3833;
  --accent:        #C26A45;
  --accent-hover:  #D77952;
  --accent-soft:   rgba(194,106,69,0.14);
  --on-accent:     #FFFFFF;
  --ok:     #5BA371;
  --warn:   #C99248;
  --danger: #C75A56;
  --shadow: 0 1px 2px rgba(0,0,0,.3), 0 8px 24px -12px rgba(0,0,0,.5);
}
```

**Usage rules**
| Token | Use for | Never use for |
|---|---|---|
| `--canvas` | `body` background, sticky nav (at 82% opacity + blur) | cards |
| `--surface` | cards, ghost buttons, pills, focused inputs | page background |
| `--surface2` | input fill, hover rows, progress-bar tracks, segmented control track | text |
| `--ink` | headings, primary text, active nav | large fills |
| `--muted` | paragraphs, nav links, labels | headings |
| `--subtle` | table headers, hints, units, fine print, headline line 2 | body copy |
| `--accent` | primary CTA, eyebrow, active underline, icons, key data line | backgrounds of large areas |
| `--accent-soft` | tag backgrounds, focus glow, step number chips, selection | text |
| `--ok/--warn/--danger` | status tags, risk colours, confusion-matrix cells (at 11–14% alpha) | decoration |

Tinted status background: `color-mix(in srgb, var(--ok) 14%, transparent)` with text `var(--ok)`.

### 2.1b Colour tokens: Theme B, Rose (healthcare)

A pink/rose variant for health and care products. It uses the **same token names**, so it drops in
by replacing the `:root` and `.dark` blocks; nothing else changes. Every value below was checked for
WCAG contrast.

```css
:root {
  --canvas:   #FCF8F9;  /* off-white with a faint rose tint */
  --surface:  #FFFFFF;
  --surface2: #F8F0F3;
  --ink:      #221A1D;  /* 16:1 on canvas */
  --muted:    #6B5F64;  /* 5.8:1 */
  --subtle:   #8F8288;  /* 3.5:1: hints/fine print only */
  --hair:     #F0E6EA;
  --hairS:    #E2D3D9;
  --accent:        #BE185D;               /* rose-magenta, hue 335°, 5.7:1 */
  --accent-hover:  #9D174D;
  --accent-soft:   rgba(190,24,93,0.09);
  --on-accent:     #FFFFFF;               /* 6.0:1 on accent */
  --ok:     #0F766E;  /* teal, 5.2:1 */
  --warn:   #A16207;  /* amber, 4.7:1 */
  --danger: #B91C1C;  /* true red, 6.1:1 */
  --ease: cubic-bezier(0.2,0.7,0.2,1);
  --shadow: 0 1px 2px rgba(34,26,29,.04), 0 8px 24px -12px rgba(120,20,60,.12);
}
.dark {
  --canvas:   #161113;
  --surface:  #1D171A;
  --surface2: #251D21;
  --ink:      #F3EAEE;  /* 15.9:1 */
  --muted:    #A99BA1;  /* 7.0:1 */
  --subtle:   #85777D;  /* 4.4:1 */
  --hair:     #30262B;
  --hairS:    #42363C;
  --accent:        #F472B6;               /* light pink, 7.1:1 on canvas */
  --accent-hover:  #F9A8D4;
  --accent-soft:   rgba(244,114,182,0.14);
  --on-accent:     #3B0A22;               /* deep plum text on pink buttons, 6.3:1 (white would fail) */
  --ok:     #2DD4BF;  /* 10.0:1 */
  --warn:   #FBBF24;  /* 11.2:1 */
  --danger: #F87171;  /* 6.8:1 */
  --shadow: 0 1px 2px rgba(0,0,0,.3), 0 8px 24px -12px rgba(0,0,0,.5);
}
```

**Why these values (keep them if you adjust anything):**
- **Accent and danger must not look alike.** A plain pink sits right next to red, so a "high risk"
  status would read as brand decoration. The accent is pushed toward magenta (hue about 335°) and
  danger is a true red (0°).
- **Teal replaces green for `--ok`.** Pink and teal are a classic healthcare pairing, and teal
  (about 175°) is maximally distinct from the rose accent.
- **Neutrals carry a faint rose tint** (canvas, hairlines, greys) so the page feels cohesive; don't
  mix in the beige neutrals from Theme A.
- **Dark mode needs `--on-accent`:** light pink with white text fails contrast, so buttons use deep
  plum text. Always style accent-filled elements with `color: var(--on-accent)`, never `#fff`.
- Chart and matplotlib equivalents: ok `#0F766E`, danger `#B91C1C`, grey text `#6B5F64`,
  sequential colormap `RdPu`.

| Pair (light / dark) | Contrast |
|---|---|
| ink on canvas | 16.2 / 15.9 |
| muted on canvas | 5.8 / 7.0 |
| accent on canvas | 5.7 / 7.1 |
| on-accent on accent | 6.0 / 6.3 |
| ok / warn / danger on canvas | 5.2, 4.7, 6.1 / 10.0, 11.2, 6.8 |

### 2.2 Typography

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
```

- Body: `'Geist', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif`
- Body letter-spacing: `-0.011em`; `-webkit-font-smoothing: antialiased`;
  `font-feature-settings: 'cv11','ss01','ss03'`
- Numbers: `.mono` = `'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace`,
  `font-feature-settings: 'tnum','zero'`, `letter-spacing: -0.02em`

| Role | Size | Weight | Line-height | Letter-spacing |
|---|---|---|---|---|
| Hero H1 | `clamp(40px, 6.4vw, 68px)` | 600 | 1.02 | -0.035em |
| Section H2 | `clamp(30px, 4vw, 42px)` | 600 | 1.08 | -0.03em |
| Page title (`.h-page`) | `clamp(30px, 4vw, 40px)` | 600 | 1.08 | -0.03em |
| H3 / card title | 15px | 600 | normal | -0.01em |
| Lede (hero paragraph) | 18px | 400 | 1.55 | (body) |
| Sub (section paragraph) | 16px, `--muted`, max-width 620px | 400 | 1.55 | |
| Body in cards | 14px, `--muted` | 400 | 1.55 | |
| Eyebrow | 12px, UPPERCASE, `--accent` | 500 | | 0.08em |
| Table header / legend | 12px, UPPERCASE, `--subtle` | 500 | | 0.05–0.07em |
| Nav link | 14px `--muted` | 400 | | |
| Big stat number | 30px mono | 500 | | |
| KPI number | 26px mono | 500 | | |
| Hint / fine print | 12px `--subtle` | 400 | | |

### 2.3 Spacing, radius, layout

- Container: `max-width: 1120px; margin: 0 auto; padding: 0 20px` (16px under 720px).
- Section rhythm: `padding-top: 88px` between landing sections (64px on mobile). Footer `margin-top: 88px`.
- App pages: `padding: 48px 20px 40px`; page header `margin-bottom: 28px`.
- Grid gaps: 16px (cards), 20px (main two-column), 12px (KPI tiles), 14px (form fields).
- Radius: **12px** cards · **8px** buttons, inputs, icon buttons · **6px** inner elements
  (segmented thumb, nav hover, number chips) · **999px** pills and tags · **3px** progress bars.
- Borders: always `1px solid var(--hair)`; hover `var(--hairS)`.
- Shadow: only `var(--shadow)` on cards and the segmented thumb. Nothing heavier.

### 2.4 Motion tokens

| What | Duration | Easing |
|---|---|---|
| Hover colour/border/bg | 150ms | `--ease` |
| Theme switch (bg/colour) | 200ms | `--ease` |
| Card lift on hover | 200ms, `translateY(-3px)` | `--ease` |
| Page enter | 260ms, opacity 0 → 1, `translateY(6px)` → 0 | `--ease` |
| Scroll reveal | 600ms, `translateY(12px)` → 0, stagger 70ms (max 3 steps) | `--ease` |
| Segmented control thumb | 250ms | `--ease` |
| Progress bars fill | 900ms (width 0 → value) | `--ease` |
| Count-up numbers | 1100–1200ms, ease-out cubic | JS |
| Gauge arc sweep | 1100ms | `--ease` |
| Chart.js draw | 900ms `easeOutQuart` | |
| Skeleton shimmer | 1.4s linear infinite | |
| Live dot pulse | 2s infinite | `--ease` |
| Logomark orbit | 6s linear infinite | |
| Toast in/out | 250ms, rises 20px | `--ease` |

Always honour `prefers-reduced-motion` (§4, last block).

---

## 3. Iconography

- Inline SVG, `viewBox="0 0 24 24"`, **stroke icons only**: `fill:none; stroke:currentColor;
  stroke-width:1.6; stroke-linecap:round; stroke-linejoin:round`.
- Sizes: 15px inline with text, 16px in icon buttons, 22px on feature cards (coloured `--accent`).
- Useful paths:
  - Shield: `M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z`
  - Pulse/activity: `M3 12h4l3 8 4-16 3 8h4`
  - Database: `<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>`
  - Lock: `<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>`
  - Clock: `<path d="M12 8v4l3 2"/><circle cx="12" cy="12" r="9"/>`
  - Moon: `M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z`
  - Sun: `<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>`
  - Menu: `M4 7h16M4 12h16M4 17h16`
- **Logomark:** a 24px SVG with a thin ring (`stroke: var(--hairS)`), a filled accent glyph in the
  centre (swap the glyph per project), and a small accent dot at the top that orbits the centre:

```html
<span class="mark" aria-hidden="true">
  <svg viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" class="ring"/>
    <!-- centre glyph: replace this path per project -->
    <path d="M12 18s-5-3.1-5-6.6A2.8 2.8 0 0 1 12 9.9a2.8 2.8 0 0 1 5 1.5C17 14.9 12 18 12 18z" class="glyph"/>
    <circle cx="12" cy="2" r="1.6" class="orbit-dot"/>
  </svg>
</span>
```

---

## 4. Complete CSS (copy verbatim, then add project-specific bits)

```css
/* ===== tokens: paste §2.1 here ===== */

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; min-height: 100vh; display: flex; flex-direction: column;
  font-family: 'Geist', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: var(--canvas); color: var(--ink); letter-spacing: -0.011em;
  -webkit-font-smoothing: antialiased; font-feature-settings: 'cv11','ss01','ss03';
  transition: background-color 200ms var(--ease), color 200ms var(--ease);
}
main { flex: 1; }
.mono { font-family: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace; font-feature-settings: 'tnum','zero'; letter-spacing: -0.02em; }
::selection { background: var(--accent-soft); color: var(--ink); }
*::-webkit-scrollbar { width: 10px; height: 10px; }
*::-webkit-scrollbar-thumb { background: var(--hair); border-radius: 6px; border: 2px solid var(--canvas); }
*::-webkit-scrollbar-thumb:hover { background: var(--hairS); }
.focus-ring:focus-visible, input:focus-visible, select:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
a { color: inherit; text-decoration: none; }
svg { fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
.wrap { max-width: 1120px; margin: 0 auto; padding: 0 20px; }

/* ===== NAV ===== */
.nav { position: sticky; top: 0; z-index: 20;
  background: color-mix(in srgb, var(--canvas) 82%, transparent);
  backdrop-filter: saturate(1.4) blur(12px); -webkit-backdrop-filter: saturate(1.4) blur(12px);
  border-bottom: 1px solid var(--hair);
  transition: background-color 200ms var(--ease), border-color 200ms var(--ease); }
.nav-inner { max-width: 1120px; margin: 0 auto; padding: 12px 20px; display: flex; align-items: center; gap: 28px; }
.brand { display: flex; align-items: center; gap: 9px; font-weight: 600; font-size: 15px; }
.mark svg { width: 24px; height: 24px; display: block; }
.mark .ring { stroke: var(--hairS); }
.mark .glyph { fill: var(--accent); stroke: none; }
.mark .orbit-dot { fill: var(--accent); stroke: none; transform-origin: 12px 12px; animation: orbit 6s linear infinite; }
@keyframes orbit { to { transform: rotate(360deg); } }
.links { display: flex; gap: 4px; flex: 1; }
.links a { position: relative; padding: 6px 10px; font-size: 14px; color: var(--muted); border-radius: 6px;
  transition: color 150ms var(--ease), background-color 150ms var(--ease); }
.links a:hover { color: var(--ink); background: var(--surface2); }
.links a.active { color: var(--ink); }
.links a.active::after { content: ""; position: absolute; left: 10px; right: 10px; bottom: -13px; height: 2px;
  background: var(--accent); border-radius: 2px; animation: grow 250ms var(--ease); }
@keyframes grow { from { transform: scaleX(0); } }
.nav-actions { display: flex; align-items: center; gap: 8px; }
.icon-btn { width: 34px; height: 34px; display: grid; place-items: center; background: none; border: 1px solid var(--hair);
  border-radius: 8px; color: var(--muted); cursor: pointer; transition: all 150ms var(--ease); }
.icon-btn:hover { color: var(--ink); border-color: var(--hairS); background: var(--surface2); }
.icon-btn svg { width: 16px; height: 16px; transition: transform 400ms var(--ease); }
.icon-btn:active svg { transform: rotate(-30deg) scale(.9); }
.sun { display: none; } .dark .sun { display: block; } .dark .moon { display: none; }
.menu-btn { display: none; }

/* ===== BUTTONS ===== */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; height: 42px; padding: 0 18px;
  border-radius: 8px; font: inherit; font-size: 14px; font-weight: 500; cursor: pointer; border: 1px solid transparent;
  transition: background-color 150ms var(--ease), border-color 150ms var(--ease), transform 150ms var(--ease), box-shadow 150ms var(--ease); }
.btn-sm { height: 34px; padding: 0 12px; font-size: 13px; }
.btn-primary { background: var(--accent); color: var(--on-accent); box-shadow: 0 1px 0 rgba(255,255,255,.15) inset, 0 4px 12px -4px var(--accent-soft); }
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); box-shadow: 0 6px 18px -6px var(--accent); }
.btn-primary:active { transform: translateY(0); }
.btn-ghost { background: var(--surface); color: var(--ink); border-color: var(--hair); }
.btn-ghost:hover { border-color: var(--hairS); background: var(--surface2); }
.arrow { display: inline-block; transition: transform 200ms var(--ease); }
.btn:hover .arrow { transform: translateX(3px); }
.btn:disabled { opacity: .7; cursor: progress; transform: none; }
.spinner { display: none; width: 14px; height: 14px; border: 2px solid color-mix(in srgb, var(--on-accent) 40%, transparent); border-top-color: var(--on-accent);
  border-radius: 50%; animation: spin 700ms linear infinite; }
.loading .spinner { display: inline-block; } .loading .btn-label { opacity: .8; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== VIEWS & REVEAL ===== */
.view { display: none; }
.view.active { display: block; animation: pageEnter 260ms var(--ease) both; }
@keyframes pageEnter { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.reveal { opacity: 0; transform: translateY(12px); transition: opacity 600ms var(--ease), transform 600ms var(--ease); transition-delay: var(--d, 0ms); }
.reveal.in { opacity: 1; transform: none; }

/* ===== HERO ===== */
.dot-grid { background-image: radial-gradient(circle, var(--hair) 1px, transparent 1px); background-size: 22px 22px; }
.hero { padding: 88px 0 72px; border-bottom: 1px solid var(--hair); position: relative;
  -webkit-mask-image: linear-gradient(to bottom, #000 80%, transparent); mask-image: linear-gradient(to bottom, #000 80%, transparent); }
.pill { display: inline-flex; align-items: center; gap: 8px; padding: 5px 12px 5px 10px; border: 1px solid var(--hair);
  border-radius: 999px; background: var(--surface); font-size: 12.5px; color: var(--muted); }
.live { width: 7px; height: 7px; border-radius: 50%; background: var(--ok); animation: live 2s var(--ease) infinite; }
@keyframes live { 0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--ok) 60%, transparent); } 70%,100% { box-shadow: 0 0 0 7px transparent; } }
h1 { font-size: clamp(40px, 6.4vw, 68px); line-height: 1.02; letter-spacing: -0.035em; font-weight: 600; margin: 22px 0 18px; }
.accent-ink { color: var(--accent); }
.muted-ink { color: var(--subtle); }
.lede { font-size: 18px; line-height: 1.55; color: var(--muted); max-width: 620px; margin: 0 0 28px; }
.cta-row { display: flex; flex-wrap: wrap; gap: 10px; }
.checks { display: flex; flex-wrap: wrap; gap: 8px 22px; margin-top: 26px; font-size: 13px; color: var(--muted); }
.checks span { display: inline-flex; align-items: center; gap: 7px; }
.checks svg { width: 15px; height: 15px; color: var(--accent); }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); margin-top: 56px; border-top: 1px solid var(--hair); }
.stat { padding: 20px 20px 0 0; }
.stat + .stat { padding-left: 20px; border-left: 1px solid var(--hair); }
.stat b { display: block; font-size: 30px; font-weight: 500; min-height: 36px; }
.stat span { font-size: 13px; color: var(--muted); }

/* ===== SECTIONS & CARDS ===== */
.section { padding: 88px 20px 0; }
.eyebrow { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: var(--accent); font-weight: 500; margin: 0 0 12px; }
h2 { font-size: clamp(30px, 4vw, 42px); line-height: 1.08; letter-spacing: -0.03em; font-weight: 600; margin: 0 0 14px; }
h3 { font-size: 15px; font-weight: 600; margin: 0 0 8px; letter-spacing: -0.01em; }
.sub { color: var(--muted); font-size: 16px; line-height: 1.55; max-width: 620px; margin: 0 0 32px; }
.card { background: var(--surface); border: 1px solid var(--hair); border-radius: 12px; padding: 22px; box-shadow: var(--shadow);
  transition: border-color 200ms var(--ease), transform 200ms var(--ease), box-shadow 200ms var(--ease), background-color 200ms var(--ease); }
.card p { color: var(--muted); font-size: 14px; line-height: 1.55; margin: 0; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.step:hover, .feature-grid .card:hover { border-color: var(--hairS); transform: translateY(-3px); }
.num { display: inline-block; color: var(--accent); font-size: 13px; margin-bottom: 26px; padding: 3px 8px; background: var(--accent-soft); border-radius: 6px; }
.feature-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.feature-grid svg { width: 22px; height: 22px; color: var(--accent); margin-bottom: 18px; }
.badges { margin-top: 28px; font-size: 12.5px; color: var(--subtle); text-align: center; }
.cta { text-align: center; padding: 64px 24px; background-color: var(--surface); }
.cta .cta-row { justify-content: center; margin-top: 26px; }

/* ===== TABLES ===== */
.table-card { padding: 6px 22px 10px; overflow-x: auto; }
.table-card h3 { margin: 16px 0 6px; }
.tbl { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl th { text-align: left; font-weight: 500; font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: var(--subtle); padding: 14px 10px; border-bottom: 1px solid var(--hair); }
.tbl td { padding: 14px 10px; border-bottom: 1px solid var(--hair); transition: background-color 150ms var(--ease); }
.tbl tbody tr:last-child td { border-bottom: 0; }
.tbl tbody tr:hover td { background: var(--surface2); }
.tbl .sd { color: var(--subtle); font-size: 12px; margin-left: 4px; }
.tbl tr.best td:first-child { font-weight: 600; }
.tag { display: inline-flex; align-items: center; gap: 5px; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 500; background: var(--accent-soft); color: var(--accent); }
.tag.ok { background: color-mix(in srgb, var(--ok) 14%, transparent); color: var(--ok); }
.tag.bad { background: color-mix(in srgb, var(--danger) 14%, transparent); color: var(--danger); }
.bar { height: 6px; background: var(--surface2); border-radius: 3px; overflow: hidden; min-width: 80px; }
.bar i { display: block; height: 100%; background: var(--accent); border-radius: 3px; width: 0; transition: width 900ms var(--ease); }

/* ===== APP PAGES ===== */
.page { padding: 48px 20px 40px; }
.page-head { margin-bottom: 28px; }
.h-page { font-size: clamp(30px, 4vw, 40px); margin: 0 0 10px; }
.grid-main { display: grid; grid-template-columns: 1.25fr 1fr; gap: 20px; align-items: start; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }

/* ===== FORMS ===== */
fieldset { border: 0; padding: 0; margin: 0 0 22px; }
legend { font-size: 12px; text-transform: uppercase; letter-spacing: .07em; color: var(--subtle); margin-bottom: 12px; padding: 0; }
.fields { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 14px; }
label { display: flex; flex-direction: column; gap: 6px; font-size: 13px; font-weight: 500; color: var(--muted); position: relative; }
.unit { position: absolute; right: 0; top: 0; font-size: 11px; color: var(--subtle); font-weight: 400; }
input, select, textarea { font: inherit; font-size: 14px; color: var(--ink); background: var(--surface2); border: 1px solid var(--hair);
  border-radius: 8px; height: 40px; padding: 0 12px; width: 100%;
  transition: border-color 150ms var(--ease), background-color 150ms var(--ease), box-shadow 150ms var(--ease); }
textarea { height: auto; min-height: 96px; padding: 10px 12px; }
input:hover, select:hover, textarea:hover { border-color: var(--hairS); }
input:focus, select:focus, textarea:focus { outline: none; border-color: var(--accent); background: var(--surface); box-shadow: 0 0 0 3px var(--accent-soft); }
select { appearance: none;
  background-image: linear-gradient(45deg, transparent 50%, var(--subtle) 50%), linear-gradient(135deg, var(--subtle) 50%, transparent 50%);
  background-position: calc(100% - 17px) 17px, calc(100% - 12px) 17px; background-size: 5px 5px; background-repeat: no-repeat; padding-right: 30px; }
/* Segmented control (2 options) */
.seg { display: grid; grid-template-columns: 1fr 1fr; background: var(--surface2); border: 1px solid var(--hair); border-radius: 8px; padding: 3px; height: 40px; position: relative; }
.seg button { border: 0; background: none; font: inherit; font-size: 13.5px; color: var(--muted); border-radius: 6px; cursor: pointer; position: relative; z-index: 1; transition: color 200ms var(--ease); }
.seg button.on { color: var(--ink); }
.seg::before { content: ""; position: absolute; top: 3px; bottom: 3px; left: 3px; width: calc(50% - 3px); background: var(--surface); border-radius: 6px; box-shadow: var(--shadow); transition: transform 250ms var(--ease); }
.seg.right::before { transform: translateX(100%); }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 18px; border-top: 1px solid var(--hair); }
.err { color: var(--danger); font-size: 13px; margin: 10px 0 0; min-height: 1em; }
.shake { animation: shake 400ms var(--ease); }
@keyframes shake { 20%,60% { transform: translateX(-4px); } 40%,80% { transform: translateX(4px); } }

/* ===== RESULT PANEL / EMPTY STATE / GAUGE ===== */
.result { position: sticky; top: 84px; }
.empty { text-align: center; padding: 70px 10px; color: var(--muted); font-size: 14px; }
.empty-icon { width: 64px; height: 64px; margin: 0 auto 16px; display: grid; place-items: center; border-radius: 50%; background: var(--accent-soft); color: var(--accent); }
.empty-icon svg { width: 28px; height: 28px; animation: beat 1.4s var(--ease) infinite; }
@keyframes beat { 0%,100% { transform: scale(1); } 15% { transform: scale(1.15); } 30% { transform: scale(1); } 45% { transform: scale(1.1); } }
.gauge { position: relative; max-width: 280px; margin: 6px auto 0; }
.gauge svg { width: 100%; display: block; }
.track, .fill { fill: none; stroke-width: 12; stroke-linecap: round; }
.track { stroke: var(--surface2); }
.fill { stroke: var(--accent); transition: stroke-dashoffset 1100ms var(--ease), stroke 400ms var(--ease); }
.gauge .value { position: absolute; left: 0; right: 0; bottom: 4px; text-align: center; font-size: 44px; font-weight: 500; }
.divider { height: 1px; background: var(--hair); margin: 22px 0; }
.hint { font-size: 12px; color: var(--subtle); font-weight: 400; margin: 0 0 12px; }
.chartbox { position: relative; height: 260px; }
.chartbox.tall { height: 320px; }
.disclaimer { font-size: 12px; color: var(--subtle); text-align: center; margin-top: 28px; }

/* ===== KPI TILES / MATRIX ===== */
.kpis { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px; }
.kpi { padding: 18px; }
.kpi b { display: block; font-size: 26px; font-weight: 500; margin-bottom: 4px; }
.kpi span { font-size: 12.5px; color: var(--muted); }
.kpi .bar { margin-top: 12px; }
.matrix { display: grid; grid-template-columns: auto 1fr 1fr; gap: 6px; font-size: 12px; text-align: center; margin-top: 14px; }
.matrix div { padding: 22px 6px; border-radius: 8px; }
.matrix .h { color: var(--subtle); padding: 6px; display: grid; place-items: center; }
.matrix .v { font-family: 'Geist Mono', monospace; font-size: 24px; font-weight: 500; animation: pop 500ms var(--ease) both; animation-delay: var(--d); }
.matrix .ok { background: color-mix(in srgb, var(--ok) 13%, transparent); color: var(--ok); }
.matrix .no { background: color-mix(in srgb, var(--danger) 11%, transparent); color: var(--danger); }
@keyframes pop { from { opacity: 0; transform: scale(.85); } }
/* Static images (e.g. matplotlib PNGs) in dark mode */
.dark img.adapt { filter: invert(.88) hue-rotate(180deg) saturate(1.4); }

/* ===== SKELETON ===== */
.skeleton { background: linear-gradient(90deg, var(--hair) 0%, var(--surface2) 50%, var(--hair) 100%); background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite; border-radius: 4px; color: transparent !important; }
.skeleton.line { height: 14px; margin: 12px 0; }
@keyframes shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }

/* ===== FOOTER / TOAST ===== */
.foot { border-top: 1px solid var(--hair); margin-top: 88px; }
.foot-inner { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; padding: 22px 20px; font-size: 12.5px; color: var(--subtle); }
.toast { position: fixed; bottom: 24px; left: 50%; transform: translate(-50%, 20px); opacity: 0; background: var(--ink); color: var(--canvas);
  padding: 10px 16px; border-radius: 8px; font-size: 13px; pointer-events: none; transition: all 250ms var(--ease); z-index: 50; }
.toast.show { opacity: 1; transform: translate(-50%, 0); }

/* ===== RESPONSIVE ===== */
@media (max-width: 960px) {
  .grid-main, .grid2, .grid3, .steps { grid-template-columns: 1fr; }
  .feature-grid { grid-template-columns: 1fr 1fr; }
  .result { position: static; }
}
@media (max-width: 720px) {
  .menu-btn { display: grid; }
  .links { position: absolute; top: 100%; left: 0; right: 0; flex-direction: column; gap: 0; background: var(--canvas);
    border-bottom: 1px solid var(--hair); padding: 8px 12px; display: none; }
  .links.open { display: flex; animation: pageEnter 200ms var(--ease); }
  .links a { padding: 12px 10px; } .links a.active::after { display: none; }
  .nav-inner { gap: 12px; } .nav-actions { margin-left: auto; } .nav-actions .btn { display: none; }
  .hero { padding: 56px 0 48px; }
  .stats { grid-template-columns: 1fr 1fr; }
  .stat:nth-child(3) { padding-left: 0; border-left: 0; }
  .feature-grid { grid-template-columns: 1fr; }
  .section { padding-top: 64px; }
  .wrap { padding: 0 16px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 1ms !important; animation-iteration-count: 1 !important; transition-duration: 1ms !important; }
  .reveal { opacity: 1; transform: none; }
}
```

Breakpoints: **960px** (multi-column grids collapse to one column; the sticky side panel becomes
static) and **720px** (hamburger nav, 2-column stats, single-column features, 16px gutters).

---

## 5. Page anatomy and components (HTML)

### 5.1 Navigation bar
Sticky, translucent (82% canvas + 12px blur), hairline bottom border. Left: logomark + brand name
(600, 15px). Middle: text links (muted → ink on hover with a `surface2` hover pill; the active link
is ink with a 2px accent underline that sits on the nav's bottom border and scales in). Right: theme
toggle icon button, small primary CTA with an arrow, and a hamburger (mobile only).

```html
<header class="nav"><div class="nav-inner">
  <a href="#/home" class="brand focus-ring"><span class="mark">…logomark…</span>Brand</a>
  <nav class="links" id="links">
    <a href="#/page-a" data-route="page-a">Page A</a>
    <a href="#/page-b" data-route="page-b">Page B</a>
  </nav>
  <div class="nav-actions">
    <button class="icon-btn focus-ring" id="theme" aria-label="Toggle theme"><svg class="moon">…</svg><svg class="sun">…</svg></button>
    <a href="#/primary" class="btn btn-primary btn-sm focus-ring">Primary action <span class="arrow">→</span></a>
    <button class="icon-btn menu-btn focus-ring" id="menu" aria-label="Menu"><svg>…menu…</svg></button>
  </div>
</div></header>
```

### 5.2 Landing page, in this exact order
1. **Hero** (`.hero.dot-grid`): status **pill** with a pulsing green `.live` dot and a mono detail
   ("Live model · RBF SVM · 85.9% test accuracy") → **H1** in two lines (line 2 wrapped in
   `.accent-ink`) → **lede** (max 620px) → **CTA row** (primary + ghost) → **checks row** (3
   icon + short phrase items in accent icons) → **stats strip** (4 columns separated by hairlines,
   top border; big mono number that counts up + muted caption).
2. **How it works** (`.section`): eyebrow → H2 two-line (line 2 `.muted-ink`) → `.sub` → 3 `.step`
   cards, each with a mono number chip (`01`, `02`, `03` in `.num`), an H3 and a paragraph.
3. **Comparison / pricing-style table** (`.section`): eyebrow → H2 → sub → `.card.table-card` with
   an uppercase subtle header row, mono numbers, `± sd` in subtle, a "Selected"/"Popular" `.tag`
   on the best row, and animated `.bar` fills in the last column.
4. **Trust / features** (`.section`): eyebrow → H2 → 4 `.card`s in `.feature-grid` (22px accent
   icon, H3, one sentence) → a centred `.badges` line of `·`-separated fine print.
5. **Final CTA**: `.card.cta.dot-grid`, centred: eyebrow, two-line H2, CTA row.
6. **Footer**: hairline top, brand text on the left, mono tech list on the right, both `--subtle`.

Heading pattern (always):
```html
<p class="eyebrow reveal">How it works</p>
<h2 class="reveal">Three quiet steps.<br /><span class="muted-ink">One honest number.</span></h2>
<p class="sub reveal">One sentence of supporting copy.</p>
```

### 5.3 App/tool pages
- `.wrap.page` → `.page-head` (eyebrow = page name, `.h-page` title, `.sub` one line) → content.
- **Form + result layout:** `.grid-main` with a `.card.form` on the left (fieldsets with UPPERCASE
  legends, auto-fill 190px field grid, units right-aligned in the label row, a segmented control for
  binary choices, and an actions row with a hairline top: ghost "Load example" + primary submit with a
  spinner) and a sticky `.card.result` on the right (empty state with a beating icon in an
  accent-soft circle → on result: eyebrow, gauge, status tag, mono meta line, divider, explanation
  chart).
- **Dashboards:** `.kpis` grid of `.kpi.card` tiles (mono number that counts up, muted label, 6px
  accent progress bar), then `.grid3` / `.grid2` chart cards (H3 title + `.chartbox`), then a
  `.table-card`.
- **Lists/history:** `.table-card` with skeleton rows while loading, status `.tag.ok` / `.tag.bad`,
  and an empty state with an accent link ("Run one →").

### 5.4 Component quick reference
| Component | Class | Notes |
|---|---|---|
| Primary button | `.btn.btn-primary` | 42px tall (34 for `.btn-sm`), lifts 1px on hover, arrow nudges 3px |
| Secondary button | `.btn.btn-ghost` | surface bg, hairline border |
| Icon button | `.icon-btn` | 34×34, hairline border; the icon rotates slightly on press |
| Pill | `.pill` | status line in the hero; optional `.live` dot |
| Tag | `.tag`, `.tag.ok`, `.tag.bad` | 999px radius, tinted bg |
| Card | `.card` | 12px radius, hairline, soft shadow; hover lift only on marketing cards |
| Number chip | `.num.mono` | `01` in an accent-soft box |
| Progress bar | `.bar > i[data-w]` | width animates from 0 via JS |
| Segmented control | `.seg` | a sliding thumb via `::before` and `.right` |
| Gauge | SVG semicircle arc | `stroke-dasharray`/`dashoffset` animation |
| Matrix / heat cells | `.matrix .v.ok/.no` | staggered pop-in via `--d` |
| Skeleton | `.skeleton`, `.skeleton.line` | shimmer placeholder |
| Toast | `#toast.toast` | ink bg, canvas text, bottom-centre |

---

## 6. JavaScript behaviours (framework-agnostic; port to hooks or components as needed)

### 6.1 Pre-paint theme (in `<head>`, before CSS)
```html
<script>
  try {
    const t = localStorage.getItem("theme");
    if (t === "dark" || (!t && matchMedia("(prefers-color-scheme: dark)").matches))
      document.documentElement.classList.add("dark");
  } catch (e) {}
</script>
```

### 6.2 Helpers
```js
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
```

### 6.3 Theme toggle (+ re-theme charts)
```js
$("#theme").addEventListener("click", () => {
  const dark = document.documentElement.classList.toggle("dark");
  try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (e) {}
  // wait for the 200ms CSS colour transition, then redraw charts with the new token values
  setTimeout(() => { chartDefaults(); rerenderVisibleCharts(); }, 210);
});
$("#menu").addEventListener("click", () => $("#links").classList.toggle("open"));
```

### 6.4 Scroll reveal (IntersectionObserver, staggered)
```js
const io = new IntersectionObserver((entries) => entries.forEach((e) => {
  if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}), { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
function observeReveals(root = document) {
  $$(".reveal:not(.in)", root).forEach((el, i) => {
    el.style.setProperty("--d", `${Math.min(i % 4, 3) * 70}ms`);
    io.observe(el);
  });
}
```
Add `.reveal` to eyebrows, headings, subs, cards and table cards. Call `observeReveals()` after
each route change or after injecting new HTML.

### 6.5 Count-up numbers
```js
function countUp(el, to, fmt, ms = 1200) {
  el.classList.remove("skeleton");
  if (reduced) { el.textContent = fmt(to); return; }
  const t0 = performance.now();
  const step = (t) => {
    const k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3); // ease-out cubic
    el.textContent = fmt(to * e);
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
// countUp(el, 85.9, v => v.toFixed(1) + "%");  countUp(el, 918, v => Math.round(v).toLocaleString());
```
Before data arrives, render the number element with the `.skeleton` class and `&nbsp;`.

### 6.6 Progress bars
Render `<div class="bar"><i data-w="72.5"></i></div>`, then on the next frame:
```js
requestAnimationFrame(() => $$(".bar i").forEach((i) => (i.style.width = i.dataset.w + "%")));
```

### 6.7 Hash router (single-file apps; with a framework router, keep only the side effects)
```js
const loaders = { home: loadHome, pageA: loadA /* … */ };
function route() {
  const name = (location.hash.replace("#/", "") || "home").split("?")[0];
  const view = loaders[name] ? name : "home";
  $$(".view").forEach((v) => v.classList.toggle("active", v.dataset.view === view)); // triggers pageEnter
  $$(".links a[data-route]").forEach((a) => a.classList.toggle("active", a.dataset.route === view));
  $("#links").classList.remove("open");
  window.scrollTo({ top: 0, behavior: "instant" });
  observeReveals($(`.view[data-view="${view}"]`));
  loaders[view](); // each loader fetches once, guarded by a "done" flag
}
addEventListener("hashchange", route); route();
```

### 6.8 Segmented control
```js
const seg = $(".seg");
seg.addEventListener("click", (e) => {
  const b = e.target.closest("button"); if (!b) return;
  $$("button", seg).forEach((x) => x.classList.toggle("on", x === b));
  seg.classList.toggle("right", b === seg.lastElementChild);
});
```

### 6.9 Loading button, error shake, toast
```js
btn.disabled = true; btn.classList.add("loading");             // shows the spinner
// on error:
form.classList.remove("shake"); void form.offsetWidth; form.classList.add("shake");  // restart the animation
// finally:
btn.disabled = false; btn.classList.remove("loading");

function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 2200);
}
```

### 6.10 Gauge (semicircle)
```html
<div class="gauge">
  <svg viewBox="0 0 200 112"><path d="M14 100 A86 86 0 0 1 186 100" class="track"/><path id="arc" d="M14 100 A86 86 0 0 1 186 100" class="fill"/></svg>
  <div class="value mono" id="val">0%</div>
</div>
```
```js
const arc = $("#arc"), LEN = arc.getTotalLength();
arc.style.strokeDasharray = LEN; arc.style.strokeDashoffset = LEN;
function setGauge(p) { // p in 0..1
  const color = p >= .7 ? css("--danger") : p >= .4 ? css("--warn") : css("--ok");
  arc.style.stroke = color; $("#val").style.color = color;
  arc.style.strokeDashoffset = LEN;
  requestAnimationFrame(() => requestAnimationFrame(() => (arc.style.strokeDashoffset = LEN * (1 - p))));
  countUp($("#val"), p * 100, (v) => v.toFixed(1) + "%", 1100);
}
```

### 6.11 Re-animating a panel on new results
```js
out.style.animation = "none"; void out.offsetWidth; out.style.animation = ""; // replays pageEnter
```

---

## 7. Charts (Chart.js 4; the same rules apply to Recharts or ECharts)

CDN: `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js`

```js
function chartDefaults() {
  Chart.defaults.font.family = "Geist, ui-sans-serif, system-ui, sans-serif";
  Chart.defaults.font.size = 11;
  Chart.defaults.color = css("--subtle");
  Chart.defaults.animation.duration = reduced ? 0 : 900;
  Chart.defaults.animation.easing = "easeOutQuart";
  Object.assign(Chart.defaults.plugins.tooltip, {
    backgroundColor: css("--surface"), titleColor: css("--muted"), bodyColor: css("--ink"),
    borderColor: css("--hair"), borderWidth: 1, padding: 10, cornerRadius: 8, displayColors: false,
  });
}
const grid = () => ({ color: css("--hair"), drawTicks: false });

// Store a *builder* per chart so it can be rebuilt with fresh token values after a theme switch.
const renderers = new Map(), charts = {};
function draw(id, build) { renderers.set(id, build); charts[id]?.destroy(); charts[id] = new Chart($(id), build()); }
function rerenderVisibleCharts() { renderers.forEach((b, id) => { if ($(id)?.offsetParent) draw(id, b); }); }
```

Rules:
- **Line charts:** `borderColor: --accent`, `borderWidth: 2`, `pointRadius: 0`, area fill
  `--accent-soft` (`fill: "origin"`). Reference lines: `--hairS`, dashed `[4,4]`, width 1.
- **Scatter-ish points:** `pointRadius: 4`, `pointBackgroundColor: --surface`, `pointBorderWidth: 2`.
- **Horizontal bars:** `indexAxis: "y"`, `borderRadius: 4`, `barThickness: 14–16`, no y grid,
  no borders, y tick colour `--ink`. Positive/negative bars use `--danger` / `--ok`; ranked bars use
  the accent at decreasing alpha: `css("--accent") + alphaHex` (e.g. `ff`, `ed`, `db`…).
  **Don't pass `color-mix()` to canvas**; use hex+alpha.
- Legends off by default; explain colours in an inline `.hint` line instead
  (`<span style="color:var(--danger)">■</span> raises · <span style="color:var(--ok)">■</span> lowers`).
- Axis titles in `--subtle`, grid `--hair`, axis border `--hair`.
- Container: `.chartbox` (260px) with `maintainAspectRatio: false`.
- Static chart images (e.g. matplotlib): transparent background; top/right spines off. Theme A:
  ok `#4A8A5C`, danger `#B0413E`, grey text `#6B6B66`, colormap `Oranges`. Theme B: ok `#0F766E`,
  danger `#B91C1C`, grey text `#6B5F64`, colormap `RdPu`. Add
  `class="adapt"` so they invert in dark mode.

---

## 8. Content and copy patterns

- **Eyebrows:** 1–3 words ("How it works", "Model comparison", "Trust & method", "Start now").
- **H2s:** statement + counter-statement, both short, ending in full stops.
  "Honest scores. / No hidden leakage." "Quiet in the UI. / Rigorous underneath."
- **Hero H1:** 2 lines, 3–4 words each; line 2 in accent.
- **Pill:** "Live · <thing> · <key metric>" in mono after the dot.
- **Checks row:** 3 × (icon + 3–5 word benefit).
- **Stats strip:** 4 numbers that matter, each with a 1–3 word lowercase caption.
- **Step cards:** "01 Verb the thing" + one or two sentences.
- **Final CTA H2:** "The X is already Y. / Put it to work."
- Put a disclaimer or fine print in `.disclaimer` / `.badges` (12–12.5px, `--subtle`, centred).
- Mono for every number: metrics, counts, timestamps, IDs, prices.

---

## 9. Porting notes

- **React/Next.js:** put tokens and CSS in `globals.css`; load fonts with `next/font/google`
  (`Geist`, `Geist_Mono`) or the `<link>`; put the pre-paint script in `<head>` (e.g.
  `dangerouslySetInnerHTML` in `layout.tsx`); make `useReveal()` a hook wrapping §6.4; make
  `<CountUp to fmt/>` a component using §6.5 in `useEffect`; use the router's route-change event in
  place of `hashchange`.
- **Tailwind:** keep the CSS variables and extend the theme:
  ```js
  theme: { extend: {
    colors: { canvas: "var(--canvas)", surface: "var(--surface)", surface2: "var(--surface2)", ink: "var(--ink)",
      muted: "var(--muted)", subtle: "var(--subtle)", hair: "var(--hair)", hairS: "var(--hairS)",
      accent: { DEFAULT: "var(--accent)", hover: "var(--accent-hover)", soft: "var(--accent-soft)" },
      ok: "var(--ok)", warn: "var(--warn)", danger: "var(--danger)" },
    fontFamily: { sans: ["Geist", "ui-sans-serif", "system-ui"], mono: ["Geist Mono", "ui-monospace"] },
    borderRadius: { card: "12px" },
    transitionTimingFunction: { calm: "cubic-bezier(0.2,0.7,0.2,1)" } } },
  darkMode: "class"
  ```
  Keep keyframes (`pageEnter`, `shimmer`, `orbit`, `live`, `beat`, `pop`, `shake`, `grow`) in global CSS.
- **Vue/Svelte:** same CSS; the reveal becomes a directive/action; the count-up becomes a component.
- **Recharts:** style `.recharts-cartesian-grid line { stroke: var(--hair) }`, ticks
  `fill: var(--subtle); font-size: 11px`, tooltip = surface + hairline + 8px radius + soft shadow.
- **No build step:** all of the above works in a single `index.html` + `styles.css` + `app.js`.

---

## 10. QA checklist (must all pass)

- [ ] Light and dark both correct; the toggle persists across reload; no flash of the wrong theme.
- [ ] Charts recolour after toggling the theme.
- [ ] At **375px** width: no horizontal scroll (`document.documentElement.scrollWidth <= innerWidth`),
      the hamburger menu works, and grids collapse.
- [ ] Every interactive element shows a 2px accent focus outline with keyboard focus.
- [ ] `prefers-reduced-motion: reduce` disables animations and shows reveals immediately.
- [ ] Skeletons show while loading; empty states have an icon + one line + a link.
- [ ] All numbers use `.mono`; all borders are 1px hairlines; one accent colour only.
- [ ] Headline pattern (eyebrow → 2-line H2 → sub) is used on every section.
- [ ] Buttons: primary lifts on hover, arrows nudge, loading shows a spinner.
- [ ] No pure `#000`/`#fff` backgrounds on the page (cards may be `--surface` white in light mode).
- [ ] Only one theme's tokens are present; accent-filled elements use `var(--on-accent)` for text.
- [ ] Theme B: the accent and `--danger` are visually distinct in status tags and charts.

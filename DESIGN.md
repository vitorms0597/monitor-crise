---
name: Monitor de Crises
description: O mundo como sismograma; crises no mundo em tempo real, riscadas em papel enfumaçado.
colors:
  soot: "#121110"
  soot-deep: "#0c0b0a"
  graphite: "#2c2a27"
  graphite-2: "#3e3b37"
  ash: "#8f887d"
  bone-dim: "#b4ada0"
  bone: "#ede6d6"
  amber: "#e8a33d"
  heat-0: "#1f1d1b"
  heat-1: "#3b2a17"
  heat-2: "#6b4416"
  heat-3: "#a8661b"
  heat-4: "#e8a33d"
  heat-5: "#f6dba6"
typography:
  display:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "clamp(2rem, 5.4vw, 4.2rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.03em"
    fontVariation: "'wdth' 82"
  headline:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "clamp(1.25rem, 2.2vw, 1.6rem)"
    fontWeight: 640
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  figure:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "clamp(1.4rem, 3vw, 2rem)"
    fontWeight: 650
    fontFeature: "'tnum'"
    fontVariation: "'wdth' 85"
  title:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "1.02rem"
    fontWeight: 520
    lineHeight: 1.35
  body:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "'tnum'"
  lede:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "clamp(1rem, 1.6vw, 1.2rem)"
    fontWeight: 400
    lineHeight: 1.5
  margin-label:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "clamp(0.85rem, 1.4vw, 1rem)"
    fontWeight: 620
    fontVariation: "'wdth' 78"
  label:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 560
    letterSpacing: "0.06em"
    fontVariation: "'wdth' 72"
  annotation:
    fontFamily: "'Archivo Variable', 'Archivo', system-ui, sans-serif"
    fontSize: "0.68rem"
    fontWeight: 600
    fontFeature: "'tnum'"
    fontVariation: "'wdth' 72"
rounded:
  none: "0px"
spacing:
  hair: "4px"
  sm: "8px"
  row: "12px"
  md: "16px"
  gutter: "clamp(16px, 4vw, 40px)"
  section: "clamp(40px, 6vw, 72px)"
  grid-cell: "12px"
components:
  nav-link:
    textColor: "{colors.bone-dim}"
    typography: "{typography.title}"
    padding: "4px 0"
  nav-link-active:
    textColor: "{colors.bone}"
  segment-button:
    backgroundColor: "transparent"
    textColor: "{colors.bone-dim}"
    rounded: "{rounded.none}"
    padding: "7px 12px"
    height: "36px"
  segment-button-pressed:
    backgroundColor: "{colors.bone}"
    textColor: "{colors.soot}"
  button-on-bone:
    backgroundColor: "transparent"
    textColor: "{colors.soot}"
    rounded: "{rounded.none}"
    padding: "8px 14px"
    height: "40px"
  button-on-bone-primary:
    backgroundColor: "{colors.soot}"
    textColor: "{colors.bone}"
  ruled-row:
    backgroundColor: "transparent"
    textColor: "{colors.bone}"
    padding: "12px 0"
  tooltip:
    backgroundColor: "{colors.bone}"
    textColor: "{colors.soot}"
    rounded: "{rounded.none}"
    padding: "4px 8px"
  peak-annotation:
    backgroundColor: "{colors.soot}"
    textColor: "{colors.amber}"
    typography: "{typography.annotation}"
    padding: "0 3px"
---

# Design System: Monitor de Crises

## Overview

**Creative North Star: "The Smoked Drum"**

The site is a seismograph drum read in the dark. The page is soot; every theme is a bone-coloured trace scratched through it; the observatory's annotations sit in the margin in condensed capitals; one amber pencil marks what the reader must look at now: the needle, the "agora" tick, the peak of each band, a rising variation, a link. The amplitude of each hour is the real volume (news plus weighted official events), so the drawing is the data, never decoration.

Density is high and quiet. Information is organised as ruled lists separated by graphite hairlines, not as boxes. The instrument surfaces (the seismogram plot and the choropleth map) carry a millimetre drum-paper grid; the page body around them is plain soot. Depth is almost absent: surfaces are flat and tonal, and only floating overlays (tooltip, consent banner) lift off the paper. Tone is cold and factual PT-BR; big rises read as multipliers ("×13,8") instead of four-digit percentages.

The world refuses the neon war-room dashboard (glowing cyan, radar sweeps, red alarms) and the white news portal (cards, photos, headline hierarchy). Both refusals are visible in the build: no saturated hue other than amber, no card containers, no imagery.

**Key Characteristics:**
- Soot ground, bone trace, graphite rules, one amber pencil.
- Archivo variable with its width axis doing the work: condensed for margin labels and annotations, near-normal for reading.
- Tabular numerals everywhere (set on `body`).
- Ruled lists, square corners, flat surfaces.
- Millimetre grid only on instrument surfaces.
- One authored motion: traces record left-to-right once.
- Time before collection began is left blank and labelled "antes da coleta", never drawn as calm.

## Colors

A near-monochrome warm-dark palette (soot to bone) with a single amber accent, plus a heat ramp that runs from soot through ember to bone.

### Primary
- **Annotation Amber** (#e8a33d): the pencil. Needle, "agora" tick, per-band peak trace segment and peak label, rising variations, prose and lede links, the official-record meta tag in the feed, active nav underline, focus ring, the logo trace. It also happens to be heat step 4, so the hottest map countries and the pencil share a hue by design.

### Neutral
- **Soot** (#121110): page ground, masthead, footer, and the knock-out background behind labels that sit on top of a trace (peak label, "agora").
- **Deep Soot** (#0c0b0a): the millimetre grid lines on instrument surfaces only.
- **Graphite** (#2c2a27): hairline rules between list rows, seismogram band borders, hour grid lines, map graticule.
- **Graphite Light** (#3e3b37): stronger rules (masthead, footer, section heads in rankings), day boundaries in the plot, baseline, segmented-control borders, resting link underline.
- **Ash** (#8f887d): labels, timestamps, sources, positions, minor axis ticks (5.6:1 on soot).
- **Bone Dim** (#b4ada0): secondary text: ledes, inactive nav, compact mini-traces, day ticks, footer small print.
- **Bone** (#ede6d6): primary text and the main trace ink; also the fill of inverted overlays.

### Heat Scale
- **Heat 0 to 5** (#1f1d1b, #3b2a17, #6b4416, #a8661b, #e8a33d, #f6dba6): choropleth bins and the legend swatches, cold soot to ember to bone. The event page reuses heat-0 for land and heat-2 for the event's country.

### Named Rules
**The One Pencil Rule.** Amber is the only chromatic accent and it always means "look here": now, peak, rise, link, focus. Never use it for decoration, fills of large areas, or category colour (heat bins excepted).

**The Blank Before Collection Rule.** Hours with no collection are filled with soot and labelled "antes da coleta" in ash. Never draw them as a flat zero line; absence of data is not calm.

## Typography

**Display Font:** Archivo Variable (with Archivo, system-ui, sans-serif)
**Body Font:** Archivo Variable (same family)
**Label Font:** Archivo Variable at condensed width (font-stretch 72% to 78%)

**Character:** A single grotesque used like an instrument's printed scale: width is the expressive axis. Headlines condense to around 82% and tighten tracking; margin labels condense hard to 72% and go uppercase; reading text stays at normal width.

### Hierarchy
- **Display** (700, clamp(2rem, 5.4vw, 4.2rem), 1.1, wdth 82%, -0.03em): page H1. The country H1 runs slightly larger (up to 4.6rem), theme and static pages slightly smaller (3.4rem), event H1 smallest (3rem, max 24ch). Home H1 caps at 14ch.
- **Headline** (640, clamp(1.25rem, 2.2vw, 1.6rem), 1.1, -0.02em): section heads, ruled underneath.
- **Figure** (650, clamp(1.4rem, 3vw, 2rem), wdth 85%, tabular): fact values on country pages.
- **Title** (520, 1.02rem, 1.35): feed item headlines; official events step up to 620.
- **Body** (400, 1rem, 1.5, tabular): default text; prose capped at 68ch.
- **Lede** (400, clamp(1rem, 1.6vw, 1.2rem), bone-dim): factual intro sentence under H1, max 62 to 66ch; its strong figures go bone at 650.
- **Margin label** (620, clamp(0.85rem, 1.4vw, 1rem), wdth 78%): seismogram band names in the left margin.
- **Label** (560, 0.75rem, 0.06em, uppercase, wdth 72%, ash): observatory annotations, section-head meta, feed meta, stamps. Inside legends, captions and footers the label drops uppercase and tracking.
- **Annotation** (600, 0.68rem, wdth 72%, amber on soot): peak labels on the plot ("pico 14h · 1.204").

### Named Rules
**The Width Axis Rule.** Hierarchy between reading text and annotation is made with width and case, not with a second family. Margin and plot annotations are condensed (72% to 78%); reading text is never condensed below 85%.

**The Tabular Rule.** All numerals are tabular. Variations of +100% or more are written as multipliers ("×13,8").

## Layout

A single centred column (max 1280px, gutter clamp(16px, 4vw, 40px)). Sections open with clamp(40px, 6vw, 72px) of top padding and a section head: H2 left, label right, a graphite rule under it (stacks and left-aligns under 560px). Long lists and feeds use a narrower 900px measure aligned to the column's left edge rather than centred.

The home first viewport stacks H1 plus lede, then a full-width four-band seismogram (left margin for band names, clamp(92px, 16vw, 168px)), then a two-column grid: map at 2.1fr beside a ranking of at least 260px, collapsing to one column under 860px. Rows inside lists breathe at 7px to 12px vertical padding; gaps run 4, 8, 12, 16px. Footer is three columns (1.4fr 1fr 1fr) collapsing under 720px. The topic nav scrolls horizontally on mobile instead of wrapping.

## Elevation & Depth

Flat by default. Depth is tonal (soot ground, graphite rules) and the page never uses shadows on resting surfaces. The only lift belongs to things that float above the paper and invert to bone: the map tooltip and the consent banner.

### Shadow Vocabulary
- **Tooltip lift** (`box-shadow: 0 4px 14px rgb(0 0 0 / 0.5)`): map hover tooltip.
- **Banner lift** (`box-shadow: 0 10px 30px rgb(0 0 0 / 0.6)`): fixed consent banner.

### Named Rules
**The Paper Stays Flat Rule.** Anything resting on the page is flat and ruled. A shadow appears only on an inverted bone overlay that floats above content.

## Shapes

Square everything (0px radius): buttons, segmented controls, tooltip, banner, ad placeholder, legend swatches. Form is made by 1px hairlines: horizontal rules between rows, border-block around fact strips, a 1px graphite-2 frame around segmented controls with internal dividers. The ad placeholder alone uses a dashed graphite-2 border, marking reserved space. Round forms occur only as data marks on instruments (earthquake rings on the map, the amber ring on the event map), never as container corners.

### Named Rules
**The Ruled List Rule.** Content is grouped by hairline rules, not by cards. No filled or bordered tiles for feed items, rankings or rising themes.

**The Instrument Grid Rule.** The 12px millimetre grid (deep-soot lines) appears only on instrument surfaces: the seismogram plot and the choropleth map. Compact mini-traces and the page body carry no grid.

## Components

### Seismogram (signature)
The drum itself. Each theme is a band: margin label (name plus 24h total in ash) on the left, plot on the right with the millimetre grid, graphite hour lines, graphite-2 day lines and baseline. The trace is bone at 2px with non-scaling stroke; the segment around each band's peak turns amber and gets an amber annotation knocked out of soot (flips left near the right edge). An amber needle marks now, with "agora · HH:MM" on the axis. Bands are separated by graphite rules top and bottom.
- **Motion:** traces record left-to-right once (clip-path reveal, 1.8s, cubic-bezier(0.16, 1, 0.3, 1), staggered per band). Reduced motion collapses it to instant.
- **Compact variant:** 28px tall, 1.5px bone-dim ink, no grid, needle, axis, labels or animation; used inline in country and theme contexts.
- **Mobile:** under 640px only day ticks and "agora" remain; the "antes da coleta" label hides, the blank stays.

### Heat Map
SVG choropleth on the millimetre grid; graphite graticule; land filled by heat bin with soot outlines. Hover/focus outlines the country in bone at 1.2px. Earthquakes are thin bone rings. Legend: 22x10px square swatches in a row with unstyled-case labels. Colour is never the only channel: the ranking sits beside it.

### Ranking ("Onde está tremendo")
Ordered ruled list: position (ash), name (links turn amber on hover), 64x20 bone-dim mini trace, value (600, right), variation (ash; amber when rising; hidden when not comparable).

### Segmented Filters
- **Shape:** square, 1px graphite-2 frame with internal dividers, min 36px tall.
- **Rest:** transparent, bone-dim condensed (78%, 560, 0.85rem).
- **Hover:** text to bone. **Pressed:** inverted, bone fill with soot text. Transitions 0.2s on the ease-out curve.

### Feed
Ruled list; each row a two-column grid (7.5em timestamp in ash, then body), single column under 560px. Meta line of condensed labels (theme, country, source type); official records carry an amber "registro oficial · nível n/5" tag and a heavier title. Titles are unadorned until hover, which underlines in amber. Every row links to its source.

### Navigation
Masthead: amber seismic-trace logo mark with the condensed bold name, plus an ash stamp with the update time in bone. Topic nav below: condensed (85%, 520, 0.95rem) bone-dim links; hover to bone; current page bone with a 2px amber underline.

### Buttons (on bone overlays)
The consent banner is the only place with true buttons: square, 1px soot border, 600 weight, min 40px tall. Secondary is transparent with soot text; primary is soot fill with bone text.

### Links
Inherit text colour with a 1px graphite-2 underline offset 0.2em; underline turns amber on hover. In prose and ledes links are amber outright. Focus is always a 2px amber outline offset 2px.

## Do's and Don'ts

### Do:
- **Do** keep amber for now, peak, rise, link and focus only (The One Pencil Rule).
- **Do** separate content with 1px graphite hairlines and keep every corner square.
- **Do** use the width axis for hierarchy: condensed 72% to 78% uppercase labels in ash for annotations, normal width for reading.
- **Do** set all numbers tabular and write rises of +100% or more as multipliers ("×13,8").
- **Do** leave pre-collection hours blank in soot with an "antes da coleta" label.
- **Do** confine the 12px millimetre grid to the seismogram plot and the map.
- **Do** respect reduced motion; the record-once trace reveal is the authored motion.
- **Do** pair every colour-coded datum with text (ranking beside the map).

### Don't:
- **Don't** build cards or tiles for feed items, rankings or theme summaries; use ruled lists.
- **Don't** add neon or saturated hues (cyan, red alarms, glows); the world is soot, bone, graphite and amber.
- **Don't** put the millimetre grid on the page body or on compact mini-traces.
- **Don't** draw missing hours as a zero line.
- **Don't** add shadows to resting surfaces; only inverted bone overlays float.
- **Don't** loop or replay the trace animation, or add competing motion around the instruments.
- **Don't** write rises as four-digit percentages.

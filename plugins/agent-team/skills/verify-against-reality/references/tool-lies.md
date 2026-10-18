# Tools lie: where this owner's projects were fooled

Source: /Volumes/MyData/ProjectsPro/ai-business/xmarlin/AGENTS.md (Verification section, lines 131-213),
xmarlin/docs/21-AUTONOMOUS-DEPLOY.md, wallapopo-main/.backlog/RETROSPECTIVE-ARCHIVE.md.
Treat as a pre-flight before reporting a screenshot, measurement or deploy as good.

## Browser and measurement
- **Hidden tabs are throttled.** Timers suspended; IntersectionObservers never fire, entrance
  animations sit at opacity 0, screenshots/DOM reads come back stale or blank. Force a repaint
  (scroll one notch down and back) or measure from a fronted/headless tab. Several sessions drew wrong
  conclusions from a throttled tab.
- **Input gestures need the tab fronted, not merely visible.** A wheel gesture did nothing until
  `tabs_select` fronted the tab, which looked exactly like the bug under investigation. If a gesture
  does nothing, front the tab and repeat before concluding.
- **Shared browser tabs get hijacked** by other sessions. Pass an explicit tab id on every call.
- **`offsetWidth` is empty on a bare `<svg>`**: a scan using it silently misses SVG figures. Use
  `getBBox()` / `getBoundingClientRect()` on the svg or measure a wrapper.
- **`getBoundingClientRect` ignores `clip-path` and ancestor `overflow`.** A clipped element reports
  its full box. Compare against the clipping ancestor's real cut line.
- **A DOM element scan cannot see pseudo-element grounds** (`::before`/`::after` backgrounds). A
  "product is largest element" rule can pass while a pseudo-element owns the screen. Measure share of
  the first screen from a screenshot or forced layout.
- **A synthesized event is not a browser behaviour test.** `new Event("dragstart")` fires whatever the
  `draggable` attribute says. Use a real pointer gesture; dispatch a real wheel, do not call `scrollTo`.
- **"Looks fine" is not a measurement** - wrong more than once, including from the lead (46% garment
  on mobile). Require a number: percentage, pixel coordinate, byte count.
- **A callout/anchor placed by eye is a guess.** Sample the artwork's pixels at that coordinate
  (one marker pointed at transparent background).
- **RTL: physical CSS does not mirror, logical does.** `left`/`right`/signed `rotate()`/`translate3d()`
  must be re-authored per direction. Test the RTL page itself, never assume symmetry from LTR.

## Build and deploy
- **Cloudflare Pages returns 200 with index.html for a route that does not exist.** `curl -I` passes for
  a page never built. Verify by content (unique `<title>`/string) plus a known-bad path that must not
  match; allow for first-response lag after a fresh build (redeploy and recheck).
- **`grep -c` counts lines, not matches.** Minified builds put many matches on one line (read "2",
  truth 633). Use `grep -o ... | wc -l`.
- **Astro silently drops unknown props.** `opacity={0.1}` on a component without that prop compiles and
  renders full strength. Read the component's actual prop list.
- **Failed upstream step, successful downstream.** `export_static.py` empties `_site` first; with Studio
  stopped it exits non-zero and leaves it empty, and `wrangler deploy` then shipped an empty Studio.
  Check the precondition (`curl localhost:8790/` = 200) and never chain deploy after a failed export.
- **Two copies of every generated asset.** `assets/flatlay/vNN/web/` AND `web/public/assets/flatlay/vNN/web/`
  must both exist and be byte-identical (`cmp`); docs claiming a symlink were wrong.
- **A page exists but is missing from the list.** `ad.json` alone gives a working `/ads/<slug>` page absent
  from `/ads`; the list is built from `tools/test-registry/data/ads.json`. Check the index, not just the page.
- **Unclassified media hides.** A video under `clips/` is a clip; the default `/ads` view shows only cuts.
- **Gated live site:** if the live site is behind a password, verify the export (`_site`) and say the
  live check was not possible (`UNVERIFIED`).

## Code and data
- **Fixtures from memory** (TASK-151): v1 shape hand-written vs v2 live; 3/3 green on broken code.
- **Test of source text** (TASK-150): matched text in a file that did not compile.
- **SQL never executed** (TASK-136/150/157): `ORDER BY` a dropped column after `UNION ALL`.
- **Deleted filter, suite green** (TASK-122): 90/90 with `and sr.source = 'wallapop'` removed.
- **Mutating the fake** (TASK-159): marginal detection zero while the test count rose 92 -> 99.
- **Duplicate HTML attribute** (TASK-175): a second `style` attribute on a `<td>` was dropped by
  parsers; an assertion on the string was green while the feature was dead. Assert the rendered effect.
- **Run killed by network error** leaves a ticket `in-progress` without a note: check the ledger
  before believing an agent failed (and before believing it succeeded).
- **Wrong unit** ("saved euros" on a free model; ~90x off).
- **Stale typecheck** (archive §13): tsc run before the last file was added.

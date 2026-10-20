# Reading Log

Raw, chronological capture surface for literature reading. **Append-only.**
This is the messy intake; the curated synthesis will live in LITERATURE.md (not yet
created — open it once a tag has accumulated enough entries to earn a section).

## Conventions

- **Source anchor on every entry** — `[Author Year]`. Written as a Markdown
  reference-style link, the same `[Author Year]` text resolves to the full citation
  defined once in the References footer at the end of the file. This is the only
  non-negotiable: it's the link back to the source. Everything else can be messy.
- **Atomic entries** — one idea per bullet, not one paper per bullet. Atomic notes
  can be re-sorted and clustered later; paragraph-per-paper notes cannot.
- **Entry IDs** — every bullet opens with a stable global ID `eNNN ·` (zero-padded,
  assigned in order, never reused even if an entry is deleted). This is the identity
  used to cross-link to a *specific note* rather than to a whole source. Grep an ID to
  find its definition and every reference to it. Next free ID is tracked in the
  `<!-- next-id -->` comment below.
- **Tags** — append `#tag` to mark themes (`#methodology`, `#data-quality`, ...). When a tag accumulates several scattered entries, that's the signal it has earned a section in LITERATURE.md.
- **Cross-links** — when a note relates to another entry, source, or task, append
  `→ eNNN` (to a specific entry), `→ [Author Year]` (to a whole source), or `→ task-id`
  (to a WORK_TASKS.md item). A note may carry several. These weave the log into a small
  graph, so a thread can be followed across entries and into actionable work.
- **Date headers** — group entries under a `## YYYY-MM-DD` header by reading session.

## Referencing from LITERATURE.md

This log is the **permanent atomic store** and is kept intact — entries are never
moved or deleted out of it. When a tag/theme has accumulated enough, LITERATURE.md
**references** those entries by `eNNN` pointer in the relevant thematic section;
the synthesis (the messy → pattern → structure step) happens there, over the
pointers, leaving this log untouched.

---

<!-- next-id: e007 -->

## 2026-10-20

- e001 · [Khedhaouiria et al. 2026] CaSR v3.2 distributes CFIA (Confidence Index of the Analysis) daily alongside the CaPA-24h precipitation analysis; ranges 0–1 and "quantifies the degree to which each grid point is constrained by observations." No formula in this paper — cites [Fortin et al. 2015] for the definition. → e004 #CFIA #precipitation #data-quality
- e002 · [Khedhaouiria et al. 2026] CaPA OI error parameters (σo, σb, correlation length lb) are re-estimated **daily** by variographic analysis of the innovations, and are **spatially uniform** over the domain on a given day. My inference: spatial CFIA contrast on a given day comes from observation geometry, but CFIA can also drift in time with a fixed network, via the daily σo/σb ratio — a CFIA trend is not by itself proof of network change. [NEEDS REVIEW] → e004 #CFIA #trend #homogeneity #open-question
- e003 · [Khedhaouiria et al. 2026] σo and σb are estimated in the Box–Cox-transformed space required by the OI, "which prevents direct interpretation in precipitation units." Presumably CFIA is computed in that space too (not stated). #CFIA #open-question
- e004 · [Khedhaouiria et al. 2022] **CFIA formula (Eq. 11): CFIA = 1 − σa² / σb²**, with σa² the analysis error variance and σb² the background error variance, per grid cell and valid time. CFIA → 1: observations dominate the analysis; CFIA → 0: background dominates (no observation assimilated nearby). Confirms the definition assumed in Notes.md (2026-10-20). → e001 #CFIA #formula
- e005 · [Khedhaouiria et al. 2022] Authors state CFIA "is convenient for users desiring to select only grid cells influenced by observations" — first-party endorsement of CFIA thresholding as a mask for precipitation indices. Hybrid OI–EnKF (flow-dependent errors) is noted to affect CFIA estimates (their §7.4, not yet read). → e004 #CFIA #masking #methodology #to-read
- e006 · [Khedhaouiria et al. 2026] CaPA-24h accumulations are **valid at 12 UTC**, not midnight → the "precipitation day" boundary differs from the calendar day; matters for day→month attribution in daily indicators. Hourly reanalysis precipitation is disaggregated from the daily analysis using online short-range forecasts; when the forecast is zero but CaPA is not, the total is spread evenly → constant-hourly artefacts, often near stations. #precipitation #day-boundary #data-quality #open-question

---

## Watchlist (potentially relevant, not yet read)

Leads surfaced during reading but not yet sourced/read. Promote to a dated entry (with an
`eNNN` ID) once read; move its citation to References at that point.

- **Fortin et al. 2015** — Fortin, V., Roy, G., Donaldson, N. & Mahidjiba, A. (2015).
  Assimilation of radar quantitative precipitation estimations in the Canadian
  Precipitation Analysis (CaPA). *Journal of Hydrology*. https://doi.org/10.1016/j.jhydrol.2015.08.003
  Cited by [Khedhaouiria et al. 2026] as the CFIA reference and for the variographic
  error estimation. Paywalled (403 on ScienceDirect). Surfaced from e001.
- **Fortin et al. 2018** — Fortin, V., Roy, G., Stadnyk, T., Koenig, K., Gasset, N. &
  Mahidjiba, A. (2018). Ten Years of Science Based on the Canadian Precipitation Analysis:
  A CaPA System Overview and Literature Review. *Atmosphere-Ocean*, 56, 178–196.
  https://doi.org/10.1080/07055900.2018.1474728 — CaPA system overview; publisher page
  returned 403. Surfaced from e001.

---

## References

<!-- Define each [Author Year] anchor once. Reference-style links: the bracket text
     above resolves to the citation below. Keep alphabetical for scannability. -->

[Khedhaouiria et al. 2022]: Khedhaouiria, D., Bélair, S., Fortin, V., Roy, G. & Lespinas, F. (2022). Using a hybrid optimal interpolation–ensemble Kalman filter for the Canadian Precipitation Analysis. *Nonlinear Processes in Geophysics*, 29, 329–344. https://doi.org/10.5194/npg-29-329-2022

[Khedhaouiria et al. 2026]: Khedhaouiria, D., Gasset, N., Fortin, V., Dimitrijevic, M., Bulat, M. & Wang, X. (2026). The Canadian Surface Reanalysis (CaSR) v3.2 precipitation dataset: A 45-year high-resolution analysis for North America (1980–2024). *EGUsphere* preprint, discussion started 17 April 2026. https://doi.org/10.5194/egusphere-2026-620

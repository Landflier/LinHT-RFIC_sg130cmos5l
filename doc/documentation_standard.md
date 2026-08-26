# Documentation Standard

**Status:** v0.1 SPEC — nothing implemented yet. Review and approve before implementation;
every doc written before approval will have to be rewritten.
**Companion document:** [collaboration.md](collaboration.md) (chat, tracking, hosting).

This document specifies (a) what documentation every block of the chip must carry, (b) where it
lives in the repository, (c) how it is scaffolded automatically, and (d) how it is turned into a
website programmatically.

---

## 1. Principles

1. **The repository is the record.** Chat, calls and personal notes are not. If a design fact is
   not in git, it does not exist and will be lost the moment its author leaves.
2. **Generated, never typed.** Any number that appears in documentation must come from a
   committed script or a simulation artifact that can regenerate it. Hand-copied numbers go
   stale silently, and a stale spec table is worse than no spec table.
3. **Prose covers what tools cannot generate:** *why* this topology, *what* was rejected, *what*
   the waveform means, *what* is known to be broken. That is the irreplaceable part; everything
   else is machinery.
4. **Documented ≠ done; done requires documented.** A block is complete when its simulations run
   headless, its reports regenerate, and its doc page has no unfilled sections. This is the same
   Definition of Done used by the issue tracker.
5. **No notebooks.** The gm/ID work stays as `specs_<cell>.py` + `sizing_<cell>.py` →
   generated `sizing_<cell>.md`, which already exists in this repo and is strictly better for a
   team: it diffs cleanly in review, runs headless in CI, cannot carry hidden execution state,
   and produces a committed artifact that is readable without running anything. The doc page
   *includes* that generated report rather than duplicating it.
6. **The build must never require the PDK or a simulator.** Figures and reports are committed
   artifacts; the website builds from markdown in a plain CI container. Otherwise the docs break
   the moment the container version moves.
7. **Scaffolding beats discipline.** Whatever `make init-macro` / `make init-submodule` creates
   is what gets filled in. Anything requiring a person to remember to create a file will not
   exist for half the blocks.

---

## 2. The four layers

| Layer | Location | Written by | Regenerated? |
| --- | --- | --- | --- |
| **Chip level** | `doc/design_plan.md`, `specifications.md`, `pinout.md`, `floorplan.md` | Lead | hand-written |
| **Decisions (ADR)** | `doc/adr/NNNN-*.md`, `macros/<macro>/doc/adr/NNNN-*.md` | Whoever decides | hand-written, immutable once accepted |
| **Cell level** | `macros/<macro>/doc/<cell>.qmd` | Cell owner | prose by hand, artifacts included |
| **Artifacts** | `scripts/sizing/sizing_<cell>.md`, `scripts/plot_simulations/figures/*.svg`, CACE results, DRC/LVS reports | Tools | fully generated, committed |

The website (§6) is a *view* over layers 1–4. It contains no content of its own except
auto-generated index and status pages.

> **`.llm/` is not documentation.** It is git-ignored and agent-local. Real design knowledge
> currently sitting there — the frac-N/LC-VCO architecture decision, the PDK split, the VACASK
> evaluation — must be promoted to `doc/adr/` before anyone joins, or it is invisible to the team.
> See §8, Phase 0.

---

## 3. The cell documentation page

One page per cell (core cells and submodule cells alike), at
`macros/<macro>/doc/<cell>.qmd`.

`.qmd` (Quarto markdown) rather than `.md` because it is a strict markdown superset that adds
YAML frontmatter, file includes, cross-references and figure numbering — and because Quarto is
already in this repo and already wired to CI.

### 3.1 Frontmatter (machine-readable, mandatory)

```yaml
---
title: "cp — charge pump"
macro: pll_top          # directory under macros/
cell: cp                # matches specs_<cell>.py / <cell>.yaml naming
owner: "Vasil Yordanov" # single accountable person, not a team
status: sized           # see the ladder below
pdk: ihp-sg13cmos5l     # must match verification/cace/<cell>.yaml
updated: 2026-08-19
specs_source: scripts/sizing/specs_cp.py
sizing_report: scripts/sizing/sizing_cp.md
cace: verification/cace/cp.yaml
issues: "label:macro:pll_top label:stage:sizing"
---
```

These fields are what makes the status dashboard (§6.3) and the CI doc gate (§7) possible; they
are not decoration.

**Status ladder** — one word, strictly increasing, and the only place project progress is
declared:

| `status` | Means |
| --- | --- |
| `spec` | Specifications written, nothing designed |
| `sized` | `make sizing` runs, report committed |
| `schematic` | Schematic + symbol entered, netlists |
| `simulated` | Testbenches run headless, figures + measured numbers committed |
| `characterized` | CACE green at PVT + Monte Carlo |
| `layout` | Layout drawn, DRC/LVS clean in both engines |
| `signed-off` | Post-PEX re-simulation meets spec, margins recorded |

### 3.2 Mandatory sections

Fixed order, all present. A section may legitimately read `N/A — <reason>`, but it may not be
deleted: the gate checks for the headings, and an explicit "not applicable, because…" is itself
information.

| # | Section | Content | Source |
| --- | --- | --- | --- |
| 1 | **Purpose and context** | What the block does in one paragraph; where it sits in the chain; link to the relevant `doc/design_plan.md` section; block diagram | hand |
| 2 | **Interface** | Pin table (name, direction, type, voltage/current range) and parameter table | hand (long-term: generated from the CACE `pins:` block, which already has exactly these fields) |
| 3 | **Specifications** | Table: parameter │ target │ source (spec / derived / inherited) │ measured │ status | target from CACE yaml, measured from CACE results |
| 4 | **Topology and design decisions** | Why *this* circuit; what was considered and rejected and why; links to the ADRs; the trade-offs a successor must not re-litigate blindly | **hand — the highest-value section** |
| 5 | **Sizing** | Narrative of the design equations and the gm/ID reasoning, then `{{< include ../scripts/sizing/sizing_cp.md >}}` | prose by hand, table generated |
| 6 | **Simulation results** | One subsection per testbench: what it proves, the exact command to reproduce it, the figure, the measured numbers, and **the interpretation** | figures + numbers generated, interpretation by hand |
| 7 | **Verification status** | CACE summary (PVT + MC), DRC/LVS status per engine, PEX deltas vs schematic | generated |
| 8 | **Known issues and next steps** | Checklist; what is broken; what the current owner would do next. **This section is the handover note** — it is what an offboarding owner fills in | hand |
| 9 | **References** | Papers, datasheets, prior art, related cells | hand |

### 3.3 Reproducibility rule

Every figure and every measured number carries the command that regenerates it, e.g.:

```
Reproduce: make sim-xschem TB=cp_tb_tran && make sim-view-xschem CELL=cp
```

If a number cannot be reproduced by a committed command, it does not belong in the
documentation.

### 3.4 Where artifacts live (no duplication)

Figures stay where the existing flow already writes them
(`scripts/plot_simulations/figures/`), and the doc page references them by relative path.
The `doc/` directory of a macro holds **only** `.qmd` pages and `adr/` — never copies of
figures or data. One location per artifact, always.

---

## 4. Architecture Decision Records

Design decisions have a lifetime measured in years and outlive the people who made them. A
one-page ADR per decision, immutable once accepted.

**Location:** chip-wide decisions in `doc/adr/`, macro-local decisions in
`macros/<macro>/doc/adr/`. Numbered `NNNN-short-title.md`, never renumbered.

**Template:**

```markdown
# ADR-0007: LC-tank VCO instead of ring oscillator for pll_top

- **Status:** accepted            <!-- proposed | accepted | superseded by ADR-NNNN -->
- **Date:** 2026-07-26
- **Deciders:** Vasil Yordanov
- **Affects:** macros/pll_top (vco, mash, mmd)

## Context
What forced a decision; the constraints (PDK, area, schedule, spec) in force at the time.

## Options considered
| Option | Pros | Cons |
|---|---|---|

## Decision
What was chosen, and the single decisive reason.

## Consequences
What this makes easy, what it makes hard, what new work it creates,
what would have to be true to revisit it.
```

**Rule:** any decision taken in a call or a chat thread that changes the design becomes an ADR
in the same week (see [collaboration.md](collaboration.md) §1.5). The cell doc page's §4 links
to it rather than restating it.

**ADRs owed immediately** (the knowledge exists but is not in the repo):
frac-N vs integer-N and LC vs ring for `pll_top`; the SG13G2 / SG13CMOS5L split; MASH 1-1-1
order and word length; VACASK alongside ngspice; the sizing-flow choice (`specs_*.py` +
`sizing_*.py` + committed report); gnuplot as the plotting standard; CIFF vs other ΣΔ
topologies for the RX ADC.

---

## 5. Scaffolding: what `make init-macro` and `make init-submodule` create

The mechanism already exists — `scripts/init_macro.sh` and `scripts/init_submodule.sh` copy
`macros/_templates/{analog,digital}` and substitute `__CELL__`, `__TOP__`, `__NAME__`,
`__DESIGNER__`, `__DATE__`. The change is additive: new template files plus a few lines in the
"next steps" output.

**New template files**

```
macros/_templates/analog/doc/__CELL__.qmd        # the page of §3, sections pre-stubbed with TODO(__NAME__)
macros/_templates/analog/doc/__TOP__.qmd         # wrapper-cell page (thinner: interface + integration)
macros/_templates/analog/doc/adr/0001-topology.md# pre-filled ADR stub for the topology choice
macros/_templates/digital/doc/__CELL__.qmd       # digital variant: §5 sizing → "Implementation
                                                 #   (RTL structure, FSM, timing constraints)";
                                                 #   §7 → synthesis/STA/CDC results
```

**Script changes**

- `init_macro.sh`: nothing structural (the whole template tree is copied and placeholders already
  substituted in filenames and contents); add the doc page to the printed "next steps".
- `init_submodule.sh`: add `doc/<sub>.qmd` to its explicit scaffold list, alongside the
  `specs_`/`sizing_`/`plot_`/CACE files it already creates.
- Macro `Makefile`: add `docs` / `docs-check` targets that build and validate just that macro.
- Template `README.md`: replace the current prose-heavy structure section with a pointer to the
  generated docs page, so there is one place to read about the block, not two.

**Frontmatter defaults on creation:** `status: spec`, `owner: __DESIGNER__`,
`updated: __DATE__`, `pdk` from the environment `PDK` at scaffold time.

---

## 6. The website

### 6.1 Layout

The goal is that a cell's page lives next to the design it documents — and therefore next to the
figures and sizing report it includes — while still being rendered into one site.

**A Quarto website project can only render inputs that live under the project root.** Since the
cell pages live under `macros/`, the project root must be the **repository root**, not
`doc/site/`:

```
_quarto.yml              # project root = repo root; explicit render list
doc/site/
├─ index.qmd             # project overview (includes doc/design_plan.md §0–§3)
├─ architecture.qmd      # system architecture, block diagram, frequency plan
├─ status.qmd            # GENERATED — status dashboard (§6.3)
├─ macros.qmd            # GENERATED — index of all cell pages
├─ adr.qmd               # GENERATED — index of all ADRs, chip + macro
└─ _site/                # build output, git-ignored
macros/<macro>/doc/*.qmd # rendered in place, from the repo-root project
```

```yaml
project:
  type: website
  output-dir: doc/site/_site
  render:
    - doc/site/*.qmd
    - macros/*/doc/*.qmd
    - "!tutorial/"          # has its own project + workflow, see §6.6
```

Two things to settle during implementation (flagged rather than assumed):

- A root-level project plus the existing `tutorial/_quarto.yml` is a nested-project situation;
  confirm the exclusion behaves against the Quarto version in CI.
- **Fallback if the root-project route proves awkward:** keep the project at `doc/site/` and have
  `gen_index.py` stage the cell pages into `doc/site/macros/` (copy or symlink) before rendering,
  rewriting relative figure/include paths as it goes. This preserves "one source location" —
  the staged copies are build output and git-ignored — at the cost of a path-rewriting step.
  Decide by trying the root project first; it is simpler if it works.

### 6.2 Generator

`scripts/docs/gen_index.py` — plain Python, no dependencies beyond a YAML parser, consistent
with the rest of the repo's scripting style:

1. Walk `macros/*/doc/*.qmd` and `**/adr/*.md`.
2. Parse frontmatter; **fail loudly** on a missing or invalid required field.
3. Emit `status.qmd`, `macros.qmd`, `adr.qmd`.
4. In `--check` mode emit nothing and exit non-zero on any violation — this is the CI gate.

### 6.3 Status dashboard

The single page that answers "where is the chip?", generated from frontmatter:

| Macro | Cell | Owner | Status | PDK | Updated | Sizing | CACE | Issues |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pll_top | cp | Vasil | sized | cmos5l | 2026-08-19 | [report](#) | [yaml](#) | [3 open](#) |

Plus a progress bar per macro over the status ladder of §3.1. This replaces `ToDo.md` and
manual status reporting, and it is the page to open at the start of every bi-weekly call.

### 6.4 Make targets

```
make docs         # gen_index.py + quarto render doc/site
make docs-serve   # live preview at localhost:4200
make docs-check   # gen_index.py --check: frontmatter + required sections, no rendering
```

### 6.5 Publication

GitHub Pages (already configured for `gh-pages`), optionally CNAME'd to `docs.landflier.com`.
Hosting it on GitHub rather than the home server is deliberate — see
[collaboration.md](collaboration.md) §3.2.

### 6.6 Relationship to `tutorial/`

The existing `tutorial/index.qmd` is the upstream JKU flow tutorial, not LinHT documentation.
Keep it, publish it as a section of the same site ("Flow tutorial"), and do not edit it beyond
the URL fixes below — it should stay cheap to re-sync from upstream.

**Defect to fix regardless of this proposal:** `tutorial/_quarto.yml` still carries the
upstream `site-url`, `repo-url` and an `include-after-body` script that rewrites "Edit this
page" / "Report an issue" to `iic-jku/ihp-sg13g2-ams-chip-template`. As published today, the
site directs contributors' issue reports to a different project's tracker.

---

## 7. CI doc gate

Extend the existing workflows rather than adding new ones.

**On every pull request** (`make docs-check`, seconds, no PDK needed):

- [ ] every required frontmatter field present and well-formed; `status` from the allowed set
- [ ] `owner` non-empty and not `TODO`
- [ ] all nine section headings present, in order
- [ ] no `TODO(` left in a page whose `status` is `simulated` or higher
- [ ] every macro listed in the top-level `MACROS` has a doc page for each of its cells
- [ ] every `{{< include >}}` target and every referenced figure exists
- [ ] `pdk` in the frontmatter matches `PDK:` in the corresponding CACE yaml
      *(this check would already have caught `macros/pll_top/verification/cace/cp.yaml`, which
      says `ihp-sg13g2` while `pll_top` targets `ihp-sg13cmos5l`)*
- [ ] `updated` not older than the newest commit touching that cell's schematic or specs

**On push to main:** build and publish the site.

**Nightly** (the existing `regression.yml`): re-run `make sizing` for every macro and fail if a
committed report changes — proving the reports are reproducible and not hand-edited. The gm/ID
data (`scripts/sizing/data/*.mat`) is committed and the sizing scripts are pure Python, so this
should run without the EDA container; verify before relying on it.

Turn the gate on **after** the existing pages pass, so it never blocks day-one work.

---

## 8. Implementation plan

| Phase | Work | Effort |
| --- | --- | --- |
| **0 — Do first, independent of approval** | Fix the inherited Quarto URLs. Create `doc/adr/` and promote the decisions listed in §4 out of `.llm/` (they are git-ignored today). Add `doc/onboarding.md`. | 0.5 d |
| **1 — Templates** | `doc/__CELL__.qmd` + ADR stub for both templates; `init_submodule.sh` change; macro `Makefile` targets; template README pointer. Pilot on `pll_top`: write real pages for `cp` and `pfd`, which already have specs, sizing scripts and figures. **Do not roll out to other macros until the pilot page has been reviewed** — the template will change once real content meets it. | 1 d |
| **2 — Site** | `doc/site/` Quarto project, `scripts/docs/gen_index.py`, `make docs` / `docs-serve` / `docs-check`. | 1 d |
| **3 — CI** | Publish workflow retargeted at `doc/site`; `docs-check` on PRs; optional CNAME. | 0.5 d |
| **4 — Enforce** | Gate turned on; Definition of Done in the issue templates references it. | 0.25 d |

**≈3.25 days total.** Phases 0–1 should be complete before the first teammate joins; 2–3 can
follow while people work.

---

## 9. Questions for review

| # | Question | Recommendation |
| --- | --- | --- |
| D1 | Quarto, or MkDocs/mdBook? | Quarto — already in the repo and in CI, handles LaTeX + figure cross-refs, and can emit a PDF of the whole design record |
| D2 | Nine mandatory sections, or fewer? | Nine. Dropping §4 (decisions) or §8 (handover) removes the reason for doing this at all |
| D3 | One page per cell, or one per macro? | Per cell — matches `specs_<cell>.py` / CACE granularity and the submodule scaffolding |
| D4 | Public site from day one? | Yes — the project is Apache-2.0 and Chipalooza is public; a private site adds auth infrastructure for no benefit |
| D5 | Commit generated SVG figures? | Yes. Repo growth is modest and it keeps the site buildable without the EDA container |
| D6 | Should the doc gate block merges, or only warn? | Warn for two weeks, then block |
| D7 | Does `README.md` per macro survive, or fold into the doc page? | Fold: README becomes a 5-line pointer, so there is one place to look |

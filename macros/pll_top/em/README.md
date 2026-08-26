<!--
SPDX-FileCopyrightText: 2026 Vasil Yordanov
SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
-->

# openEMS inductor flow — `pll_top` LC tank (IHP SG13CMOS5L)

Scaffolding for designing the LC-VCO tank inductor by EM simulation. The infrastructure is
here and verified; **the inductor design is not done** — that is the work this exists to
support.

Everything runs inside the IIC-OSIC-TOOLS container (`iic-osic-tools_xserver_uid_1000`),
which ships openEMS v0.0.36, AppCSXCAD, gdspy and both IHP PDKs.

```bash
docker exec -it iic-osic-tools_xserver_uid_1000 bash -l
cd /foss/designs/LinHT-RFIC-chipalooza_6/macros/pll_top/em
make check          # confirm openEMS / gdspy / PDK are reachable
```

---

## Layout of this directory

| Path | What it is |
|---|---|
| `scripts/gen_stackup.py` | Derives the CMOS5L EM stackup from the PDK. **Self-validating.** |
| `scripts/gen_spiral.py` | Parametric octagonal spiral → GDSII |
| `scripts/em_env.py` | Locates the IHP openEMS helper modules, sets `sys.path` |
| `scripts/em_run.py` | Headless FDTD runner + CSV writer |
| `stackup/SG13CMOS5L.xml` | Generated stackup (committed on purpose — see below) |
| `models/run_inductor_diffport.py` | 1-port differential L/Q extraction |
| `gds/`, `results/` | Generated geometry and FDTD output (git-ignored) |
| `plot/inductor.gp` | gnuplot L/Q plot |

The heavy lifting — GDS reading, meshing, port creation, S-parameter extraction — is IHP's
official openEMS workflow, which we reference rather than copy:

```
$PDK_ROOT/ihp-sg13g2/libs.tech/openems/openems_ihp_sg13g2/workflow/modules/
```

Read its documentation before going deep; it is genuinely good:
`.../openems_ihp_sg13g2/doc/Using_OpenEMS_Python_with_IHP_SG13G2_v2.pdf`

**Those modules live in the sg13g2 PDK, but they are technology-agnostic** — every process
detail comes from the stackup XML we hand them. `ihp-sg13cmos5l` ships no `openems/`
directory at all, which is why `em_env.py` reaches into the G2 PDK for code while feeding it
the CMOS5L stackup. Override with `OPENEMS_WORKFLOW_DIR` if you ever need a patched copy.

---

## The stackup, and why you can trust it

`gen_stackup.py` builds `stackup/SG13CMOS5L.xml` from CMOS5L's own machine-readable data.
Nothing is hand-transcribed:

| Quantity | Source |
|---|---|
| Layer thicknesses, z-positions, GDS layer numbers | `libs.tech/klayout/tech/xsect/sg13cmos5l_for_EM.xs` |
| Metal conductivity | `libs.tech/magic/ihp-sg13cmos5l-extract.tech` — σ = 1/(R_sheet·t) |
| Via conductivity | same magic deck (Ω/contact) + via size from the DRC deck |
| **Dielectric permittivity, substrate/EPI conductivity** | **assumed — inherited from SG13G2** |

Run the self-check any time:

```bash
make stackup-validate
```

It does two things:

1. **Geometry** — re-derives *sg13g2* from its `.xs` and diffs against IHP's official
   hand-written `SG13G2.xml`. Worst deviation **0.30 nm** (IHP rounded their file; the
   parser does not). This proves the parser.
2. **Materials** — derives conductivities from CMOS5L's Magic deck and compares to IHP's G2
   XML. Two completely independent sources agree to **<0.1 %** on every layer the spiral
   uses.

So the metal losses and geometry are cross-checked, not guessed.

### What is still assumed

`eps_SiO2 = 4.1`, `eps_nitride = 6.6`, substrate 2 S/m, EPI 5 S/m, 3.75 µm.
These are **not** in any CMOS5L file — they come from IHP's G2 openEMS stackup. They set the
capacitive and substrate-loss side of Q. If simulated Q ever disagrees with silicon, these
are the numbers to challenge first. The generator prints them under
`INHERITED VALUES` every run, and they are listed in the XML header comment.

One more: `t_epi = 3.75` is **commented out** in the CMOS5L `.xs` with a `TO DO` marker.
We use the value anyway. Watch that line across PDK updates.

The XML is generated but **committed** — it is the one artefact that depends on the
installed PDK version, so keeping it in git makes PDK drift show up as a diff.

The Magic deck also carries three metal-resistance corners, so corner runs are nearly free:

```bash
python3 scripts/gen_stackup.py --corner hr -o stackup/SG13CMOS5L_hr.xml   # high R
python3 scripts/gen_stackup.py --corner lr -o stackup/SG13CMOS5L_lr.xml   # low R
```

---

## First session

```bash
make stackup-validate            # see the evidence above for yourself
make spiral-show                 # geometry summary, writes nothing
make spiral                      # -> gds/spiral_n3_r218_w30_s14.gds
make preview                     # AppCSXCAD: inspect geometry + mesh
make sim                         # FDTD run -> results/<name>/{*.s1p,*.csv}
make plot                        # -> results/<name>/<name>.png
```

Sweep by overriding variables:

```bash
make spiral sim plot N=4 ROUT=150 W=20 S=10 CELLSIZE=8
```

`make preview` before `make sim`, always. A bad mesh is invisible in the numbers and
expensive in wall-clock.

---

## Things worth knowing before you start

**The default geometry is a starting point, not an answer.**
`N=3, R_out=218 µm, W=30 µm, S=14 µm` is the *SG13G2* optimum from the SMACD'26 open frac-N
PLL paper (arXiv 2607.08852) — where the spiral sits on **TopMetal2 at 11.2 µm with 3 µm of
metal**. CMOS5L has no TopMetal2: the winding goes on **TopMetal1 at 5.4 µm, 2 µm thick**.
Closer to a lossy substrate, thinner metal. That geometry is a familiar place to start
sweeping from, nothing more. Re-optimising it for this stackup is the design work.

**`W = 30 µm` sits exactly on a DRC limit.**
CMOS5L rule `Slt.c.TM1`: *max TopMetal1 width without requiring a slit = 30.00 µm*. Go wider
and the trace must be slotted — which changes both the drawn geometry and the EM result.
`gen_spiral.py` warns but does **not** draw slits. Other limits it checks: `TM1.a` min width
1.64 µm, `TM1.b` min space 1.64 µm.

**Mesh convergence is on you.** `--cellsize` is the main runtime knob and the main way to
get a confidently wrong Q. Start coarse (8 µm), tighten until L and Q stop moving, then use
that. Do this once, early — before you trust any sweep.

**Differential vs 2-port.** `run_inductor_diffport.py` places one in-plane port across both
terminals, so L and Q are *differential* — which is what a cross-coupled tank sees, and the
cheaper simulation. If you later want a substrate-referenced π-model for the netlist, the
2-port variant is `run_inductor_2port.py` in the PDK workflow directory; it needs the
`SUBGND` via ports (already in our stackup, layer 210) and a ground polygon in the GDS.

**The PDK's `runSimulation()` force-launches a GUI.** It calls AppCSXCAD unconditionally and
blocks until you close the window, which makes batch sweeps impossible. `scripts/em_run.py`
reimplements it with the viewer opt-in (`--preview`), keeping IHP's SHA-256 model hashing so
an unchanged model is not re-simulated. Use `--force` to override that.

---

## Where to start — a learning path

Suggested order. Each step is small and answers one question.

**1. See the model before you trust any number.**
`make spiral && make preview`. In AppCSXCAD, turn layers on and off. Confirm: the winding is
on TopMetal1, the underpass is on Metal4 below it, the TopVia1 blocks connect them, and the
port sits in the gap between the two terminals. If the geometry is wrong, everything
downstream is wrong.

**2. Learn what the mesh is doing.** Still in the preview, look at the grid lines. Re-run
with `CELLSIZE=15` and `CELLSIZE=4` and compare. This is the single most important intuition
in FDTD — where cells are needed and where they are wasted.

**3. Run one simulation end to end.** `make sim && make plot` at a coarse `CELLSIZE=10`.
Do not care about the numbers yet. Care that the flow completes and produces `.s1p`, `.csv`
and a plot.

**4. Do the convergence study.** Same geometry, `CELLSIZE` = 12, 10, 8, 6, 4. Plot L and Q
at 2.45 GHz against cell size. They converge; find where. Everything after this uses that
cell size. Skipping this step is how people publish wrong Q.

**5. Sanity-check against a hand calculation.** Compute L for the default geometry with a
closed-form spiral expression (Wheeler / Mohan monomial) and compare. If the EM result is
off by more than ~20 %, something is wrong with the model, not with the formula.

**6. Only now start sweeping.** One parameter at a time, watching L *and* Q.

Useful references while doing this: IHP's PDF (linked above) has worked examples for exactly
this workflow, and `run_inductor_diffport.py` / `run_inductor_2port.py` in the PDK workflow
directory are the upstream versions of our model.

---

## What is missing

Infrastructure that is **not** built yet, roughly in the order it will be wanted:

- **A sweep driver.** Nothing loops over geometries and collects results into one table.
  `make sim` runs a single point. A sweep script that fans out over (N, R_out, W, S) and
  writes one CSV of L/Q/SRF per geometry is the obvious next tool.
- **Open/short de-embedding.** The port has its own parasitic inductance, and it is included
  in the result today. The paper's flow de-embeds it with open and short dummy structures.
  Until that exists, absolute L is slightly optimistic and small inductors are worse hit.
- **The 2-port / π-model path.** For dropping the inductor into an ngspice or VACASK tank
  simulation you want a substrate-referenced 2-port and a lumped π extraction, not just a
  differential 1-port. The stackup already carries `SUBGND` (layer 210) for this; the GDS
  needs a ground polygon and the model needs two via ports.
- **Patterned ground shield option** in `gen_spiral.py`.
- **Slit drawing** for `W > 30 µm` (DRC `Slt.c.TM1`), if wide traces turn out to be wanted.
- **DRC on the generated GDS.** `gen_spiral.py` does four arithmetic checks; it does not run
  KLayout DRC. The geometry it emits is *not* verified DRC-clean.
- **A varactor/tank model** to turn L and Q into a tuning range and phase noise number —
  that is where this connects back to the PLL spec.

---

## TODO plan

Ordered, with the decision each step unblocks.

### Phase 1 — trust the flow (do this first)
- [ ] Walk steps 1–4 of the learning path above.
- [ ] Record the converged cell size in this README so later sweeps are comparable.
- [ ] Cross-check one geometry against a closed-form L estimate.

### Phase 2 — find the achievable design space
- [ ] Write the sweep driver (`scripts/sweep_spiral.py`) — fan out over N / R_out / W / S,
      one CSV of L, Q, SRF per geometry.
- [ ] Sweep at fixed L ≈ target tank inductance, maximise Q at 2.45 GHz.
- [ ] Answer the real question: **what Q is actually achievable on TopMetal1?** The
      architecture note assumes 10–13 by analogy with the paper's TopMetal2 result on a
      different stack. Confirm or replace that number — the phase-noise budget depends on it.
- [ ] Check the winner against the Chipalooza area budget (default geometry is already
      375 × 420 µm = 0.16 mm² for the coil alone, before keep-out).

### Phase 3 — make the result trustworthy
- [ ] Add open/short de-embedding structures and re-extract the chosen geometry.
- [ ] Re-run the winner at the `hr` and `lr` metal corners (`--corner`, already supported)
      to get a Q spread rather than a single optimistic number.
- [ ] Try a patterned ground shield and measure whether it earns its area.

### Phase 4 — hand off to the circuit
- [ ] 2-port simulation + π-model extraction of the chosen inductor.
- [ ] Drop the model into the tank and close the loop on tuning range and phase noise.
- [ ] Run KLayout DRC on the final drawn spiral.
- [ ] Fold the outcome back into `.llm/pll-top-fracn-lc.md` and the proposal, replacing the
      assumed Q with the simulated one.

### Open questions to resolve along the way
- Do the inherited dielectric constants (SiO2 4.1, nitride 6.6, substrate 2 S/m) hold for
  CMOS5L? They are the largest remaining assumption in the stackup.
- Is a shield worth it when the substrate is only 5.4 µm below the winding?
- Does the LC tuning range cover the required band, given the coverage-gap trade already
  flagged in the architecture note?

See `.llm/pll-top-fracn-lc.md` for the architecture context and
`doc/chipalooza_pll_proposal.md` for where the tank sits in the PLL.

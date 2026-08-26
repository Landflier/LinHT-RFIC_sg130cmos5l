# Fractional-N LC-VCO PLL

> [!NOTE]
> This proposal was drafted with AI assistance (Claude by Anthropic, used
> through Claude Code). The architecture, specifications, and final decisions
> are reviewed and owned by Vasil Yordanov.

## IP block type

Fractional-N charge-pump PLL / RF clock synthesizer with a **cross-coupled
LC-tank VCO** built around a **custom, EM-verified spiral inductor**, and a
**MASH 1-1-1 ΣΔ modulator** dithering a multi-modulus feedback divider. Loop
filter fully integrated — no off-chip components.

SG13CMOS5L has no characterized inductors on its reduced metal stack, so the
inductor is designed and verified in-house with **openEMS** (FDTD), following
the parameterized-spiral workflow published in the SMACD'26 open-source
SG13G2 2.4 GHz LC-VCO fractional-N PLL
([arXiv 2607.08852](https://arxiv.org/abs/2607.08852), sources at
[Manimohan05/SG13G2_2.4GHz_LC_VCO_FPLL](https://github.com/Manimohan05/SG13G2_2.4GHz_LC_VCO_FPLL)).
That project's parametric inductor scripts, VCO core, and type-II loop are
reused as the starting point and ported to the CMOS5L stack; the fractional
machinery is upgraded from their 1st-order/9-bit ΣΔ to the MASH 1-1-1
developed for the LinHT_IC synthesizer.

## Functional description

The PLL synthesizes f_out = (N + FRAC/2^20)·f_ref / P from a 10–50 MHz
reference (32 MHz nominal). Signal path: phase-frequency detector, charge
pump, integrated third-order passive loop filter (MOM caps — CMOS5L has no
MIM), LC-tank VCO (core ≈ 2.2–2.6 GHz: 3-bit switched-cap band select +
MOS-cap varactor for continuous in-band tuning), multi-modulus feedback
divider (2/3-cell cascade, ÷64–127, first cell rated for the VCO frequency),
output post-divider P = 4/8/16/32/64, and a lock detector. A **MASH 1-1-1 ΣΔ
modulator** (20-bit fractional word, ±3/+4 modulus span, LSB dither) runs on
the divider output clock and dithers the modulus; bypassing it falls back to
plain **integer-N operation** — the bring-up and de-risk mode. Charge-pump
linearization (constant-offset current) keeps folded ΣΔ quantization noise
in check.

The VCO and charge pump run from a local regulator off the 3.3 V analog
rail, referenced to the shared bandgap, for supply-noise rejection; dividers,
MASH and logic use the 1.2 V digital rail. Bias derives from one
bandgap-referenced current source. Configuration (N, FRAC, band select,
post-divider, MASH enable/bypass, dither, CP trim, test modes) loads through
the 3-wire shift interface. An open-loop test mode disconnects the charge
pump so the VCO control voltage can be forced/monitored through a shared
analog pin; a ÷16 VCO tap allows external frequency counting.

### Inductor (EM workflow)

Starting point: the SMACD'26 three-turn symmetric octagonal spiral
(R_out = 218 µm, W = 30 µm, S = 14 µm → 4.0 nH, Q ≈ 16.8 at 2.45 GHz on
SG13G2). Port to CMOS5L: spiral on thick TopMetal1, underpass on Metal4 (no
TopMetal2/TopVia2 on this stack), full re-optimization of (R_out, W, S) in
openEMS with the CMOS5L substrate/dielectric stack, Gaussian-pulse
excitation, open-short de-embedding, L/Q extracted from Z_diff. Expected
penalty from the thinner stack: Q ≈ 10–13, budgeted as ~3–4 dB phase-noise
margin against the paper's numbers. If the floorplan slot allows, a
standalone inductor test structure with open/short de-embed frames is added
for silicon-vs-EM correlation.

### CMOS5L device substitutions

- **Varactor:** no varicap model in the PDK — use a MOS-cap varactor
  (inversion-mode PMOS, gate vs. tied S/D/B), simulated with the standard
  compact model; C–V and K_VCO linearity characterized in simulation.
- **Capacitors:** no MIM — tank bank and loop filter use MOM
  (`cap_mfringe`) and MOS caps; loop-filter area budgeted accordingly.

## I/O

Pinout unchanged from the earlier integer-N draft — all new functionality is
behind the configuration shift register.

| Pin | Type | Function |
|---|---|---|
| ref_in | digital in | reference clock, 10–50 MHz (32 MHz nominal) |
| clk_out | digital out | synthesized clock (post-divider output) |
| en | digital in | enable / power-down |
| lock | digital out | lock-detector flag |
| cfg_clk, cfg_data, cfg_load | digital in | configuration shift register (N, FRAC[19:0], band, P, MASH/dither, CP trim, test modes) |
| test_out | digital out | VCO ÷16 tap for frequency counting |
| vctrl | analog (shared) | force/monitor VCO control voltage; low current, no special pad resistance requirement |
| ibias | analog in | bandgap-referenced bias current |
| vbg | analog in | 1.2 V bandgap reference for VCO regulator |
| VDD1V2 / VDD3V3A / VSS | supply | digital / analog / ground |

## Target specification

| Parameter | Min | Typ | Max | Absolute limit |
|---|---|---|---|---|
| VCO core frequency | 2.2 GHz | 2.45 GHz | 2.6 GHz | all corners, −40…125 °C; band overlap ≥ 20 % |
| Output frequency (pads) | 34 MHz | — | 650 MHz | f_VCO/P, P = 4…64; continuous within each P band (≈18 % tuning per band — not gap-free across bands, unlike the ring draft) |
| Fractional resolution | — | f_ref/2^20 (≈ 30.5 Hz at VCO, 32 MHz ref) | — | 20-bit FRAC word |
| Feedback modulus N | 67 | — | 124 | ÷64–127 MMD minus MASH ±3/+4 span |
| VCO phase noise @ 1 MHz, 2.45 GHz | — | −98 dBc/Hz | −92 dBc/Hz | paper: −100.8 dBc/Hz on SG13G2; margin for lower CMOS5L inductor Q |
| Integrated jitter (10 kHz–40 MHz, at VCO) | — | 3 ps RMS | — | 10 ps RMS |
| Reference spurs | — | −55 dBc | — | −45 dBc |
| Fractional spurs (worst in-band, near-integer channel) | — | −45 dBc | — | −35 dBc |
| Loop bandwidth | 75 kHz | 150 kHz | 300 kHz | MASH noise vs. reference-noise trade |
| Lock time | — | 50 µs | — | 100 µs |
| Supply sensitivity | — | 1 %/V | — | — |
| Power (2.45 GHz, frac mode) | — | 15 mW | — | 25 mW |
| Power-down current | — | 10 µA | — | — |
| Area (incl. inductor) | — | ≤ 0.7 mm² | — | paper: 0.62 mm²; **confirm against assigned Chipalooza slot** |

## Test plan outline

1. **Static:** supply currents, enabled and powered down.
2. **Open-loop VCO:** force vctrl, count test_out — tuning curve per band,
   range, K_VCO and band overlap versus supply and temperature.
3. **Closed-loop integer-N (MASH bypassed):** sweep N, P, and reference
   frequency; verify output frequency, lock flag, and lock time (en toggle
   and N step, oscilloscope capture).
4. **Fractional-N:** sweep FRAC across a band including near-integer
   channels; verify frequency resolution against a counter; fractional and
   reference spurs on a spectrum analyzer, MASH on/off and dither on/off
   comparison.
5. **Jitter/noise:** phase-noise measurement on clk_out; integrate; compare
   against the openEMS-predicted inductor Q via the VCO PN model.
6. **Sensitivity:** ±10 % on each rail — frequency pushing and jitter change.
7. **Inductor test structure** (if placed): S-parameters via RF probing,
   open/short de-embedding — silicon vs. openEMS correlation.

## Reuse map

| Piece | Source | State |
|---|---|---|
| Parametric spiral + openEMS scripts (FDTD, Wheeler-formula init, sweep/optimize, open-short de-embed) | SMACD'26 repo `openems/` | re-run with CMOS5L stackup; geometry re-optimized |
| Cross-coupled LC VCO core (NMOS pair + PMOS pair) | SMACD'26 repo `xschem/` | port G2→CMOS5L devices; varactor replaced by MOS-cap |
| PFD (DFF + NAND reset, dead-zone mitigation), CP, type-II loop | SMACD'26 repo + own sizing scripts (`scripts/sizing/`) | PFD/CP work already started in this macro |
| MASH 1-1-1 ΣΔ (20-bit) | LinHT_IC digital plan (`doc/design_plan.md` §5) | RTL shared with LinHT `digital_core`; here instantiated inside the macro |
| MMD ÷64–127 (2/3 cells) | new (paper has fixed-÷4 + dual-modulus ÷240/248 — insufficient modulus span for MASH 1-1-1) | design here, reuse in LinHT |
| Bandgap-referenced bias, local regulator, cfg shift register | previous integer-N draft | unchanged |

## Relation to the LinHT_IC fractional-N synthesizer

This block is now a **direct silicon prototype** of the LinHT_IC transceiver
synthesizer (`pll_top`, SG13G2): same type-II charge-pump loop, same MASH
1-1-1 modulator, same MMD architecture, and the same openEMS
inductor-verification workflow the LinHT VCO will use. What this tapeout
retires: charge-pump nonidealities and linearization, MASH-dithered MMD
operation and fractional spur levels, in-house inductor EM-to-silicon
correlation, loop-filter area, lock behavior, supply sensitivity. Remaining
deltas for LinHT: widen the VCO to the octave 2.08–4.16 GHz band-switched
design (6-bit cap bank), add the CML ÷2 quadrature LO divider chain, move
the ΣΔ modulator into the companion `digital_core` (SPI-controlled), and
port back to the full SG13G2 stack — where the thicker TopMetal2 recovers
inductor Q and the PDK's characterized inductors provide a model
cross-check.

# LinHT RFIC — An Open-Source Handheld Radio IC in IHP SG13CMOS5L

[![License: Solderpad Hardware License v2.1](https://img.shields.io/badge/License-Solderpad%20Hardware%20License%20v2.1-blue.svg)](LICENSE)

This repository designs the radio IC for the **LinHT** open-source handheld radio. Every
block of the IC is built on the IHP SG13CMOS5L Open-PDK.

The PLL comes first. It is an entry to
[**Chipalooza Challenge #2**](https://opencircuitdesign.com/chipalooza/), an open-source
analog IP shuttle that runs on the same PDK.

> [!IMPORTANT]
> All work needs the [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS) container,
> tag `2026.08` or later.


## Aim

LinHT is an open-source handheld radio. It transmits and receives **M17**, an open digital
voice and data protocol, and analog FM.

No vendor sells the IC that the radio needs. It must cover 130 MHz to 520 MHz without a
gap. It must also give the host processor an I/Q data stream.

This repository designs that IC. It will hold every block of it, and it builds them all on
one PDK: **IHP SG13CMOS5L**. [`doc/design_plan.md`](doc/design_plan.md) states the
specifications and the schedule.

The frequency synthesizer comes first, because Chipalooza gives it a free tapeout and three
design reviews. The receive chain, the transmit chain and the data converters follow. Each
one becomes a macro under [`macros/`](macros/), in the same structure the PLL uses now.


## Where to find the PLL

The PLL is the macro [`macros/pll_top/`](macros/pll_top/). Read these three files first:

| File | Contents |
| --- | --- |
| [`macros/pll_top/doc/chipalooza_pll_proposal.md`](macros/pll_top/doc/chipalooza_pll_proposal.md) | The architecture, the specification table and the Chipalooza submission. |
| [`macros/pll_top/README.md`](macros/pll_top/README.md) | The macro itself: cells, testbenches and how to run them. |
| [`doc/design_plan.md`](doc/design_plan.md) | The complete radio IC that this PLL serves. |

The PLL is a fractional-N charge-pump synthesizer. An LC-tank VCO sets the frequency. A
MASH 1-1-1 delta-sigma modulator, 20 bits wide, dithers a multi-modulus divider that
divides by 64 to 127. If you bypass the modulator, the loop becomes an integer-N PLL. That
is the mode for first bring-up.

SG13CMOS5L constrains the design in three ways. The metal stack has M1 to M4 and TopMetal1
only. The PDK has no MIM capacitors and no varicap model.

1. The PDK characterizes no inductor, so the spiral is designed in-house with openEMS.
2. The spiral goes on TopMetal1 instead of TopMetal2. The expected Q is therefore 10 to 13.
3. An inversion-mode PMOS device replaces the varactor, and MOM capacitors replace the MIM
   capacitors.

These numbers are budgets and not measurements. The proposal budgets a phase noise of
−98 dBc/Hz at 1 MHz offset, and an area of 0.7 mm² or less. Nobody has confirmed the area
against the assigned Chipalooza slot.


## Repository structure

```text
├─ doc/                Chip and PDK documentation. Start at doc/README.md.
├─ macros/             One directory per design block.
│  ├─ pll_top/         The PLL. This is the design.
│  ├─ inverter/        Analog example from the template.
│  ├─ counter/         Digital example from the template.
│  └─ _templates/      Skeletons that init-macro and init-submodule copy.
├─ models/vacask/      SG13CMOS5L device models, ported to VACASK.
├─ scripts/            Repository-wide scripts: macro setup, sizing, gnuplot.
├─ flow/               LibreLane configuration for the chip top level.
├─ ip/                 Bondpads and logos from the template.
├─ rtl/                Chip top-level RTL.
├─ schematic/          Chip top-level schematic.
└─ testbenches/        Chip top-level testbenches.
```

Every macro is self-contained. It owns a `Makefile`, a schematic, testbenches, a CACE
specification and a `final/` directory that hands its GDS to the chip top level. You
simulate and verify a macro on its own, before any assembly.

The repository pins the PDK to `ihp-sg13cmos5l` in every Makefile and every `xschemrc`.
You therefore do not set the `PDK` variable, and an inherited value cannot change the
result. `make PDK=<other>` on the command line still overrides the pin.


## Add a macro, or add a submodule

The template creates macros. This repository adds two scripts, so **read this section even
if you know the template**.

**A macro is a block that the chip assembles**, for example the PLL. It gets its own
directory under `macros/`, its own `Makefile` and its own `final/` handoff.

```sh
make init-macro MACRO=<name> [TYPE=analog|digital]
```

**A submodule is a cell inside a macro**, for example the phase detector or the VCO inside
the PLL. It is not a macro. It gets no directory of its own, no `Makefile` and no `final/`
handoff, because the parent macro delivers it.

```sh
make init-submodule MACRO=pll_top SUB=vco
```

That command writes four files into the parent macro:

```text
macros/pll_top/scripts/sizing/specs_vco.py
macros/pll_top/scripts/sizing/sizing_vco.py
macros/pll_top/scripts/plot_simulations/plot_vco.gp
macros/pll_top/verification/cace/vco.yaml
```

The script writes no schematic, because no template for one exists. Draw `vco.sch` and
`vco.sym` in `macros/pll_top/schematic/xschem/`, then place the symbol in the parent cell.
Use the cell name without a `_top` suffix. That suffix belongs to the macro top cell.

The parent `Makefile` then drives the new cell through three variables:

```sh
make sizing SIZING_CELL=vco          # from macros/pll_top/
make sim-xschem TB=vco_tb_tran
make klayout-verify CELL=vco
```

Read [`scripts/init_submodule.sh`](scripts/init_submodule.sh) for the digital file list and
for the auto-detection of the macro type.


## Build and simulate

```sh
make -C macros/pll_top sim-xschem TB=<testbench> SIM=vacask
```

`SIM` selects the simulator. `SIM=ngspice` is the default. `SIM=vacask` netlists the
schematic in Spectre format and runs VACASK with the ported models in
[`models/vacask/`](models/vacask/). The `SIM` variable is an addition to the template.

Run `make help` at the top level, or in any macro, for the full target list.
[`doc/template_flow.md`](doc/template_flow.md) documents every target, the Xschem
configuration and the directory tree in full.


## Based on

This repository derives from the
[**ihp-sg13cmos5l-ams-chip-template**](https://github.com/iic-jku/ihp-sg13cmos5l-ams-chip-template)
by Simon Dorrer and Harald Pretl, Institute for Integrated Circuits and Quantum Computing,
Johannes Kepler University Linz. The template supplies the directory structure, the
Makefile flow and the two example macros. Cite the template as:

```
@software{2026_ams_chip_template_cmos5l,
	author = {Dorrer, Simon and Pretl, Harald},
	month = aug,
	year = {2026},
	title = {{GitHub Repository of an Open-Source Analog Mixed-Signal Chip Design Template for the ihp-sg13cmos5l Open-PDK}},
	url = {https://github.com/iic-jku/ihp-sg13cmos5l-ams-chip-template},
	doi = {10.5281/zenodo.22115134}
}
```

The PLL reuses the openEMS inductor workflow and the VCO core of the SMACD'26 open-source
SG13G2 PLL ([arXiv 2607.08852](https://arxiv.org/abs/2607.08852), sources at
[Manimohan05/SG13G2_2.4GHz_LC_VCO_FPLL](https://github.com/Manimohan05/SG13G2_2.4GHz_LC_VCO_FPLL)).
The proposal lists what this design reuses and what it changes.


## License

Solderpad Hardware License v2.1. See [`LICENSE`](LICENSE).

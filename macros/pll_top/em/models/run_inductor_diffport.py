#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Vasil Yordanov
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
Differential (1-port) EM simulation of a spiral inductor on IHP SG13CMOS5L.

One in-plane port is placed across the two terminals, so the extracted L and Q are the
DIFFERENTIAL values -- which is what a cross-coupled LC-VCO tank actually sees. That makes
this the right model for the pll_top tank, and it is also much cheaper than the 2-port
version (one excitation, no substrate ground reference needed).

    Zdiff = Z0 * (1 + S11) / (1 - S11)
    Ldiff = Im(Zdiff) / omega
    Qdiff = Im(Zdiff) / Re(Zdiff)

Outputs (under em/results/<model>/):
    <model>.s1p     Touchstone, for use as a black box in a circuit simulator
    <model>.csv     f / L / Q / R / X columns, for gnuplot
    summary printed to stdout

Typical flow:
    ./run_inductor_diffport.py --gds ../gds/spiral_n3_r218_w30_s14.gds --preview   # check mesh first
    ./run_inductor_diffport.py --gds ../gds/spiral_n3_r218_w30_s14.gds             # then simulate

Mesh resolution is the main runtime knob. Start coarse (--cellsize 8), confirm the model
looks right, then tighten until L and Q stop moving -- that convergence check is on you,
and it is the single most common way to get a confidently wrong Q out of FDTD.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import em_env

em_env.bootstrap()

import numpy as np

import util_stackup_reader as stackup_reader
import util_gds_reader as gds_reader
import util_utilities as utilities
import util_simulation_setup as simulation_setup
import util_meshlines as util_meshlines
from openEMS import openEMS

import em_run

# Port layer convention, must match scripts/gen_spiral.py
PORT1_LAYER = 201


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gds", default=em_env.gds("spiral_n3_r218_w30_s14.gds"),
                    help="input GDS (default: the geometry `make spiral` writes)")
    ap.add_argument("--stackup", default=em_env.STACKUP_XML,
                    help="stackup XML (default: em/stackup/SG13CMOS5L.xml)")
    ap.add_argument("--fstop", type=float, default=15e9, help="upper frequency in Hz (default 15G)")
    ap.add_argument("--numfreq", type=int, default=601, help="frequency points (default 601)")
    ap.add_argument("--target-freq", type=float, default=2.45e9,
                    help="extraction frequency in Hz (default 2.45G, the tank frequency)")
    ap.add_argument("--cellsize", type=float, default=6.0,
                    help="mesh cell size in the conductor region, um (default 6)")
    ap.add_argument("--margin", type=float, default=200.0,
                    help="distance from geometry to the simulation boundary, um (default 200)")
    ap.add_argument("--energy-limit", type=float, default=-40.0,
                    help="residual energy end criterion in dB (default -40)")
    ap.add_argument("--cells-per-wavelength", type=int, default=20)
    ap.add_argument("--preview", action="store_true",
                    help="open AppCSXCAD to inspect geometry and mesh, then exit")
    ap.add_argument("--postprocess", action="store_true",
                    help="re-evaluate existing simulation data without re-running")
    ap.add_argument("--force", action="store_true",
                    help="re-simulate even if unchanged results already exist")
    args = ap.parse_args()

    if not os.path.isfile(args.gds):
        sys.exit(f"GDS not found: {args.gds}\nGenerate one first: scripts/gen_spiral.py")
    if not os.path.isfile(args.stackup):
        sys.exit(f"Stackup not found: {args.stackup}\nGenerate it: scripts/gen_stackup.py")

    model = os.path.splitext(os.path.basename(args.gds))[0]
    sim_path = os.path.join(em_env.RESULTS_DIR, model)
    os.makedirs(sim_path, exist_ok=True)

    print(f"model    : {model}")
    print(f"geometry : {args.gds}")
    print(f"stackup  : {args.stackup}")
    print(f"results  : {sim_path}\n")

    unit = 1e-6
    fstart = 0.0

    # ---- technology ----------------------------------------------------------------
    materials_list, dielectrics_list, metals_list = stackup_reader.read_substrate(args.stackup)

    layernumbers = metals_list.getlayernumbers()
    simulation_ports = simulation_setup.all_simulation_ports()
    simulation_ports.add_port(simulation_setup.simulation_port(
        portnumber=1, voltage=1, port_Z0=50,
        source_layernum=PORT1_LAYER, target_layername="TopMetal1", direction="x"))
    layernumbers.extend(simulation_ports.portlayers)

    # ---- geometry ------------------------------------------------------------------
    allpolygons = gds_reader.read_gds(args.gds, layernumbers, purposelist=[0],
                                      metals_list=metals_list, preprocess=False,
                                      merge_polygon_size=1.0)

    # ---- FDTD setup ----------------------------------------------------------------
    wavelength_air_um = 3e8 / args.fstop / unit
    max_cellsize = wavelength_air_um / (np.sqrt(materials_list.eps_max) * args.cells_per_wavelength)

    FDTD = openEMS(EndCriteria=10 ** (args.energy_limit / 10))
    FDTD.SetGaussExcite((fstart + args.fstop) / 2, (args.fstop - fstart) / 2)
    FDTD.SetBoundaryCond(["PEC"] * 6)

    FDTD = simulation_setup.setupSimulation(
        [1], simulation_ports, FDTD, materials_list, dielectrics_list, metals_list,
        allpolygons, max_cellsize, args.cellsize, args.margin, unit,
        xy_mesh_function=util_meshlines.create_xy_mesh_from_polygons)

    if not args.postprocess:
        em_run.run_fdtd(FDTD, sim_path, model, [1], preview=args.preview, force=args.force)
        if args.preview:
            print("\nPreview only -- no simulation run. Drop --preview to simulate.")
            return 0

    # ---- evaluation ----------------------------------------------------------------
    f = np.linspace(fstart, args.fstop, args.numfreq)
    s11 = utilities.calculate_Sij(1, 1, f, sim_path, simulation_ports)

    s1p = os.path.join(sim_path, model + ".s1p")
    utilities.write_snp(np.array([s11]), f, s1p)

    with np.errstate(divide="ignore", invalid="ignore"):
        z0 = simulation_ports.get_port_by_number(1).port_Z0
        zdiff = z0 * (1 + s11) / (1 - s11)
        omega = 2 * np.pi * f
        ldiff = zdiff.imag / omega
        qdiff = zdiff.imag / zdiff.real
        rdiff = zdiff.real

    csv = os.path.join(sim_path, model + ".csv")
    em_run.write_csv(csv,
                     [f / 1e9, ldiff * 1e9, qdiff, rdiff, zdiff.imag],
                     ["f_GHz", "L_nH", "Q", "R_ohm", "X_ohm"])

    # ---- summary -------------------------------------------------------------------
    idx = int(np.argmin(np.abs(f - args.target_freq)))
    # self-resonance = first zero crossing of the reactance
    srf = None
    sign = np.sign(zdiff.imag[1:])
    crossings = np.where(np.diff(sign) < 0)[0]
    if len(crossings):
        srf = f[crossings[0] + 1]

    finite_q = qdiff[np.isfinite(qdiff)]

    print(f"\n{'-' * 52}")
    print(f"Differential inductor, extracted at {f[idx] / 1e9:.3f} GHz")
    print(f"{'-' * 52}")
    print(f"  L        : {ldiff[idx] * 1e9:8.3f} nH")
    print(f"  Q        : {qdiff[idx]:8.2f}")
    print(f"  R series : {rdiff[idx]:8.3f} ohm")
    print(f"  L at DC  : {ldiff[1] * 1e9:8.3f} nH")
    print(f"  peak Q   : {np.max(finite_q):8.2f} at "
          f"{f[int(np.nanargmax(np.where(np.isfinite(qdiff), qdiff, -np.inf)))] / 1e9:.2f} GHz")
    if srf:
        print(f"  SRF      : {srf / 1e9:8.2f} GHz")
        if srf < 2.5 * args.target_freq:
            print("             ^ close to the operating frequency; L will be strongly")
            print("               inflated at 2.45 GHz and the tank will be hard to tune.")
    else:
        print(f"  SRF      :  not reached below {args.fstop / 1e9:.1f} GHz")
    print(f"{'-' * 52}")
    print(f"\nWrote {s1p}")
    print(f"Wrote {csv}")
    print(f"\nPlot it:  gnuplot -e \"datafile='{csv}'\" ../plot/inductor.gp")
    return 0


if __name__ == "__main__":
    sys.exit(main())

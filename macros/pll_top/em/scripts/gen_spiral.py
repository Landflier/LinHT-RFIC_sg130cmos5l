#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Vasil Yordanov
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
Parametric octagonal spiral inductor -> GDSII, for openEMS simulation on SG13CMOS5L.

Geometry
--------
  * Spiral winding on TopMetal1 (GDS 126) -- the top metal in CMOS5L, 2 um thick, 5.4 um
    above the silicon. There is no TopMetal2 in this PDK, so this is as far from the lossy
    substrate as a winding can get.
  * The inner terminal is brought out on a Metal4 underpass (GDS 50), connected with
    TopVia1 (GDS 125) blocks at each end. Both terminals end up on TopMetal1, side by side,
    separated by one (W + S) pitch.
  * A port polygon on GDS layer 201 spans the terminal gap. The openEMS model reads that
    layer and places an in-plane port there -- see models/run_inductor_diffport.py.

The via blocks are drawn as solid squares the width of the trace. In layout they would be
via arrays; for EM a solid block is the standard approximation (and IHP's own workflow has
via-array merging for exactly this reason).

IMPORTANT -- the defaults are a STARTING POINT, not an answer
-------------------------------------------------------------
The default 3 turns / R_out 218 um / W 30 um / S 14 um is the optimum reported for
*SG13G2* in the SMACD'26 open frac-N PLL paper (arXiv 2607.08852), where the spiral sits on
TopMetal2 at 11.2 um with 3 um of metal. On CMOS5L the winding is 2 um thick and ~5.8 um
closer to the substrate, so that geometry is not the CMOS5L optimum -- it is a familiar
place to start sweeping from. Re-optimising it for this stackup is the actual design work.

Usage
-----
    ./gen_spiral.py                                  # defaults -> ../gds/spiral_default.gds
    ./gen_spiral.py -n 3 -r 218 -w 30 -s 14
    ./gen_spiral.py -n 4 -r 150 -w 20 -s 10 -o ../gds/L_n4_r150.gds
    ./gen_spiral.py --name spiral_n3 --print         # geometry summary only, no file
"""

import argparse
import math
import os
import sys

try:
    import gdspy
except ImportError:
    sys.exit("gdspy not found. It ships with the IIC-OSIC-TOOLS container "
             "(pip install gdspy if you are outside it).")

HERE = os.path.dirname(os.path.abspath(__file__))
EM_DIR = os.path.dirname(HERE)
GDS_DIR = os.path.join(EM_DIR, "gds")

# GDS layers (drawing purpose 0). Layer numbers come from the CMOS5L cross-section deck --
# the same source gen_stackup.py parses, so geometry and stackup can never disagree.
LAYER_TOPMETAL1 = 126
LAYER_METAL4 = 50
LAYER_TOPVIA1 = 125

# Port layers are a convention of IHP's openEMS workflow, not PDK layers. The model script
# names the same numbers when it declares its ports.
LAYER_PORT1 = 201
LAYER_PORT2 = 202
LAYER_SUBGND = 210

# DRC limits worth knowing before you sweep. Source:
# libs.tech/klayout/tech/drc/rule_decks/sg13cmos5l_maximal.drc
TM1_MAX_WIDTH_NO_SLIT_UM = 30.0   # rule Slt.c.TM1
TM1_MIN_WIDTH_UM = 1.64           # rule TM1.a
TM1_MIN_SPACE_UM = 1.64           # rule TM1.b

# Octagon vertices sit at odd multiples of 22.5 deg, so the shape is symmetric about the
# y axis and both terminals leave from the bottom.
START_ANGLE_DEG = -67.5
SEGMENTS_PER_TURN = 8


def octagon_spiral_centerline(r_out, w, s, n_turns):
    """Centerline points of the winding, from the outer start to the inner end."""
    pitch = w + s
    n_seg = int(round(SEGMENTS_PER_TURN * n_turns))
    r_start = r_out - w / 2.0
    points = []
    for k in range(n_seg + 1):
        angle = math.radians(START_ANGLE_DEG + 45.0 * k)
        radius = r_start - pitch * k / SEGMENTS_PER_TURN
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    return points


def build_spiral(r_out, w, s, n_turns, lead_len, cellname):
    pitch = w + s
    centerline = octagon_spiral_centerline(r_out, w, s, n_turns)

    r_start = r_out - w / 2.0
    r_end = r_start - pitch * n_turns
    if r_end <= w:
        raise SystemExit(
            f"geometry collapses: inner radius {r_end:.1f} um <= trace width {w} um.\n"
            f"Reduce turns ({n_turns}), reduce pitch (W+S = {pitch} um), "
            f"or increase R_out ({r_out} um)."
        )

    cell = gdspy.Cell(cellname)

    # --- winding on TopMetal1 -------------------------------------------------------
    winding = gdspy.FlexPath(centerline, w, layer=LAYER_TOPMETAL1, datatype=0,
                             corners="miter", ends="flush").to_polygonset()
    cell.add(winding)

    x_outer, y_outer = centerline[0]
    x_inner, y_inner = centerline[-1]

    y_bottom = y_outer - lead_len
    y_jog = y_outer - lead_len * 0.5
    x_term2 = x_outer - pitch          # second terminal, one pitch to the left

    # --- outer terminal lead, straight down on TopMetal1 -----------------------------
    outer_lead = gdspy.FlexPath([(x_outer, y_outer), (x_outer, y_bottom)], w,
                                layer=LAYER_TOPMETAL1, datatype=0,
                                corners="miter", ends="flush").to_polygonset()
    cell.add(outer_lead)

    # --- inner terminal: Metal4 underpass out to the second terminal ------------------
    underpass = gdspy.FlexPath(
        [(x_inner, y_inner), (x_inner, y_jog), (x_term2, y_jog), (x_term2, y_bottom)],
        w, layer=LAYER_METAL4, datatype=0, corners="miter", ends="flush").to_polygonset()
    cell.add(underpass)

    # --- TopVia1 blocks at both ends of the underpass ---------------------------------
    for cx, cy in ((x_inner, y_inner), (x_term2, y_bottom)):
        cell.add(gdspy.Rectangle((cx - w / 2, cy - w / 2), (cx + w / 2, cy + w / 2),
                                 layer=LAYER_TOPVIA1, datatype=0))

    # --- TopMetal1 landing pad on the second terminal ---------------------------------
    cell.add(gdspy.Rectangle((x_term2 - w / 2, y_bottom - w / 2),
                             (x_term2 + w / 2, y_bottom + w / 2),
                             layer=LAYER_TOPMETAL1, datatype=0))

    # --- port polygon spanning the terminal gap ---------------------------------------
    # The openEMS model turns this into an in-plane port on TopMetal1, excited along x.
    gap_x0 = x_term2 + w / 2
    gap_x1 = x_outer - w / 2
    cell.add(gdspy.Rectangle((gap_x0, y_bottom - w / 2), (gap_x1, y_bottom + w / 2),
                             layer=LAYER_PORT1, datatype=0))

    info = {
        "cellname": cellname,
        "n_turns": n_turns, "r_out": r_out, "w": w, "s": s, "pitch": pitch,
        "r_inner": r_end,
        "outer_diameter": 2 * r_out,
        "port_gap": gap_x1 - gap_x0,
        "terminals": ((x_outer, y_bottom), (x_term2, y_bottom)),
        "conductor_length": _centerline_length(centerline) + 2 * lead_len,
        "bbox": cell.get_bounding_box(),
    }
    return cell, info


def _centerline_length(points):
    return sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))


def check_drc(w, s, info):
    """Cheap sanity checks against the CMOS5L rules that bite spiral designs."""
    warnings = []
    if w > TM1_MAX_WIDTH_NO_SLIT_UM:
        warnings.append(
            f"W = {w} um exceeds the {TM1_MAX_WIDTH_NO_SLIT_UM} um TopMetal1 max width "
            f"without a slit (DRC Slt.c.TM1). Wider traces need slits cut into them, which "
            f"changes both the EM result and the drawn geometry -- this generator does not "
            f"draw slits. Keep W <= {TM1_MAX_WIDTH_NO_SLIT_UM} um or add slitting yourself."
        )
    if w < TM1_MIN_WIDTH_UM:
        warnings.append(f"W = {w} um is below the TopMetal1 minimum width {TM1_MIN_WIDTH_UM} um.")
    if s < TM1_MIN_SPACE_UM:
        warnings.append(f"S = {s} um is below the TopMetal1 minimum spacing {TM1_MIN_SPACE_UM} um.")
    if info["r_inner"] < 2 * w:
        warnings.append(
            f"inner radius {info['r_inner']:.1f} um is under 2*W; the innermost turns "
            f"contribute little inductance and a lot of loss (current crowding)."
        )
    return warnings


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", "--turns", type=float, default=3,
                    help="number of turns (default 3; fractional turns in 1/8 steps work)")
    ap.add_argument("-r", "--r-out", type=float, default=218.0,
                    help="outer radius in um (default 218)")
    ap.add_argument("-w", "--width", type=float, default=30.0,
                    help="trace width in um (default 30)")
    ap.add_argument("-s", "--space", type=float, default=14.0,
                    help="turn-to-turn spacing in um (default 14)")
    ap.add_argument("--lead-len", type=float, default=30.0,
                    help="terminal lead length below the coil in um (default 30)")
    ap.add_argument("--name", default=None, help="cell name (default derived from parameters)")
    ap.add_argument("-o", "--output", default=None, help="output GDS path")
    ap.add_argument("--print", dest="print_only", action="store_true",
                    help="print the geometry summary, write no file")
    args = ap.parse_args()

    name = args.name or (
        f"spiral_n{args.turns:g}_r{args.r_out:g}_w{args.width:g}_s{args.space:g}"
        .replace(".", "p")
    )
    out = args.output or os.path.join(GDS_DIR, name + ".gds")

    gdspy.current_library = gdspy.GdsLibrary()
    cell, info = build_spiral(args.r_out, args.width, args.space,
                              args.turns, args.lead_len, name)

    (x0, y0), (x1, y1) = info["bbox"]
    print(f"cell               : {info['cellname']}")
    print(f"turns              : {info['n_turns']:g}")
    print(f"outer radius       : {info['r_out']:.1f} um   (outer diameter {info['outer_diameter']:.1f} um)")
    print(f"inner radius       : {info['r_inner']:.1f} um")
    print(f"width / space      : {info['w']:g} / {info['s']:g} um   (pitch {info['pitch']:g} um)")
    print(f"conductor length   : {info['conductor_length']:.1f} um")
    print(f"port gap           : {info['port_gap']:.1f} um")
    print(f"bounding box       : {x1 - x0:.1f} x {y1 - y0:.1f} um")
    print(f"footprint          : {(x1 - x0) * (y1 - y0) / 1e6:.4f} mm^2")

    for warning in check_drc(args.width, args.space, info):
        print(f"\nWARNING: {warning}")

    if args.print_only:
        return 0

    os.makedirs(os.path.dirname(out), exist_ok=True)
    lib = gdspy.GdsLibrary(unit=1e-6, precision=1e-9)
    lib.add(cell)
    lib.write_gds(out)
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

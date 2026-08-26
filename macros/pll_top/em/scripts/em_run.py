# SPDX-FileCopyrightText: 2026 Vasil Yordanov
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
Headless replacement for the IHP workflow's runSimulation(), plus CSV/Touchstone output.

Why not use the PDK's runSimulation() directly
----------------------------------------------
util_simulation_setup.runSimulation() unconditionally launches the AppCSXCAD GUI on every
run that is not postprocess-only, and blocks until you close the window:

    if 1 in excite_portnumbers:
        ret = os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

That is fine for a single interactive model, but it makes batch sweeps impossible and breaks
any run without an X display. run_fdtd() below does the same work with the viewer made
OPT-IN (preview=True), and otherwise keeps the framework's behaviour -- including its
SHA-256 model hashing, which skips re-simulation when the model has not changed.
"""

import os
import sys

import util_simulation_setup as simulation_setup
import util_utilities as utilities


def run_fdtd(FDTD, sim_path, basename, excite_ports, preview=False, force=False):
    """
    Write the CSX model, optionally show it in AppCSXCAD, then run the FDTD solver.

    preview=True  -> open the 3D viewer and STOP without simulating (mesh/geometry check)
    force=True    -> re-simulate even if a result with an identical model hash exists

    Returns the excitation data path.
    """
    excitation_path = utilities.get_excitation_path(sim_path, excite_ports)
    os.makedirs(excitation_path, exist_ok=True)

    csx_file = os.path.join(excitation_path, basename + ".xml")
    FDTD.GetCSX().Write2XML(csx_file)

    if preview:
        from CSXCAD import AppCSXCAD_BIN
        print(f"Opening AppCSXCAD: {csx_file}")
        print("Close the viewer to continue.")
        ret = os.system(AppCSXCAD_BIN + f' "{csx_file}"')
        if ret != 0:
            print(f"[WARNING] AppCSXCAD exited with code {ret} "
                  f"(no X display? the model XML is still written)")
        return excitation_path

    existing_hash = simulation_setup.get_hash_from_data_folder(excitation_path)
    model_hash = simulation_setup.calculate_sha256_of_file(csx_file)

    if existing_hash == model_hash and not force:
        print("Model unchanged since the last run -- reusing existing data.")
        print("Pass --force to re-simulate anyway.")
        return excitation_path

    print(f"Running FDTD, excitation ports {excite_ports} ...")
    try:
        FDTD.Run(excitation_path)
    except AssertionError as exc:
        sys.exit(f"[ERROR] openEMS failed: {exc}")
    simulation_setup.write_hash_to_data_folder(excitation_path, model_hash)
    print("FDTD finished.")
    return excitation_path


def write_csv(path, columns, header):
    """
    Write plain columnar data for gnuplot.

    columns: list of equal-length sequences. header: list of column names.
    Emits a '#'-prefixed header line so gnuplot skips it automatically.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nrows = len(columns[0])
    with open(path, "w") as fh:
        fh.write("# " + "\t".join(header) + "\n")
        for i in range(nrows):
            fh.write("\t".join(f"{col[i]:.9g}" for col in columns) + "\n")
    return path

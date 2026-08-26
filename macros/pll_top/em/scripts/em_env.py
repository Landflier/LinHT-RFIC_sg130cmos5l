# SPDX-FileCopyrightText: 2026 Vasil Yordanov
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
Path bootstrap for the pll_top openEMS flow.

Why this exists
---------------
The IHP openEMS helper modules (stackup reader, GDS reader, mesher, port/setup helpers)
ship ONLY with the ihp-sg13g2 PDK, under

    $PDK_ROOT/ihp-sg13g2/libs.tech/openems/openems_ihp_sg13g2/workflow/

ihp-sg13cmos5l ships no openems/ directory at all. That is fine: those modules are
technology-agnostic -- every process detail they use comes from the stackup XML we hand
them (../stackup/SG13CMOS5L.xml). So we borrow the *code* from the G2 PDK and feed it the
*CMOS5L stackup*. Nothing G2-specific leaks in.

We reference the PDK copy instead of vendoring it so PDK updates are picked up for free.
Override with OPENEMS_WORKFLOW_DIR if you ever need a patched/local copy.

Usage in a model script:

    import em_env
    em_env.bootstrap()
    import modules.util_stackup_reader as stackup_reader
    ...
"""

import os
import sys

# repo-side directories, resolved relative to this file
EM_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STACKUP_DIR  = os.path.join(EM_DIR, "stackup")
GDS_DIR      = os.path.join(EM_DIR, "gds")
MODELS_DIR   = os.path.join(EM_DIR, "models")
RESULTS_DIR  = os.path.join(EM_DIR, "results")
SCRIPTS_DIR  = os.path.join(EM_DIR, "scripts")

STACKUP_XML  = os.path.join(STACKUP_DIR, "SG13CMOS5L.xml")

# candidate locations for the IHP openEMS workflow modules, first hit wins
_PDK_ROOT_CANDIDATES = [
    os.environ.get("PDK_ROOT"),
    "/foss/pdks",
    os.path.expanduser("~/pdk"),
]
_WORKFLOW_SUBPATH = os.path.join(
    "ihp-sg13g2", "libs.tech", "openems", "openems_ihp_sg13g2", "workflow"
)


def find_workflow_dir():
    """Return the directory holding the IHP openEMS `modules` package."""
    explicit = os.environ.get("OPENEMS_WORKFLOW_DIR")
    if explicit:
        if not os.path.isdir(os.path.join(explicit, "modules")):
            raise RuntimeError(
                f"OPENEMS_WORKFLOW_DIR={explicit} has no modules/ subdirectory"
            )
        return explicit

    for root in _PDK_ROOT_CANDIDATES:
        if not root:
            continue
        candidate = os.path.join(root, _WORKFLOW_SUBPATH)
        if os.path.isdir(os.path.join(candidate, "modules")):
            return candidate

    raise RuntimeError(
        "Could not locate the IHP openEMS workflow modules.\n"
        "Looked for '<PDK_ROOT>/" + _WORKFLOW_SUBPATH + "' under: "
        + ", ".join(str(c) for c in _PDK_ROOT_CANDIDATES) + "\n"
        "Set OPENEMS_WORKFLOW_DIR to override. Note these modules live in the *sg13g2* PDK "
        "even though we simulate the CMOS5L stackup -- that is expected, see this file's docstring."
    )


def bootstrap(verbose=False):
    """Put the IHP `modules` package and our own scripts/ on sys.path."""
    workflow_dir = find_workflow_dir()
    for path in (workflow_dir, os.path.join(workflow_dir, "modules"), SCRIPTS_DIR):
        if path not in sys.path:
            sys.path.insert(0, path)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if verbose:
        print(f"[em_env] IHP openEMS modules : {workflow_dir}")
        print(f"[em_env] stackup             : {STACKUP_XML}")
    return workflow_dir


def gds(name):
    """Absolute path to a GDS in em/gds/."""
    return os.path.join(GDS_DIR, name)


def results(*parts):
    """Absolute path inside em/results/, creating parent directories."""
    path = os.path.join(RESULTS_DIR, *parts)
    os.makedirs(os.path.dirname(path) if os.path.splitext(path)[1] else path, exist_ok=True)
    return path


if __name__ == "__main__":
    bootstrap(verbose=True)
    print("[em_env] OK")

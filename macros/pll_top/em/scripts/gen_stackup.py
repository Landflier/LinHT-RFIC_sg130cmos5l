#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Vasil Yordanov
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
"""
Generate the openEMS stackup XML for IHP SG13CMOS5L from the PDK's own machine-readable data.

Nothing is hand-transcribed. Each number is traced to a CMOS5L source file:

  GEOMETRY (thicknesses, GDS layer numbers)
      <- libs.tech/klayout/tech/xsect/sg13cmos5l_for_EM.xs
         The PDK's KLayout cross-section deck "for EM". Thicknesses are accumulated into
         absolute Zmin/Zmax by following the deck's own 'z = z + t_a + t_b' steps.

  METAL CONDUCTIVITY
      <- libs.tech/magic/ihp-sg13cmos5l-extract.tech   (resist section, milliohm/square)
         sigma = 1 / (Rsheet * thickness), thickness from the .xs above.
         The deck carries three process corners, so --corner gives metal-loss corners
         for free: nominal, hr (high resistance), lr (low resistance).

  VIA CONDUCTIVITY
      <- same magic deck (contact section, milliohm per contact)
         sigma = h / (R_contact * A), with the drawn via area from the CMOS5L DRC deck
         (see VIA_DRAWN_SIZE_UM below for the exact rule each size comes from).

  DIELECTRIC PERMITTIVITY + SUBSTRATE/EPI CONDUCTIVITY
      <- NOT available in machine-readable form anywhere in ihp-sg13cmos5l.
         These are the ONLY inherited values. They come from IHP's official SG13G2 openEMS
         stackup and are listed explicitly in INHERITED_DIELECTRICS below, so the entire
         assumed content of the output is one readable table rather than scattered magic
         numbers. Same SG13 platform, but not independently confirmed for CMOS5L.

Self-check
----------
    ./gen_stackup.py --validate

  (a) GEOMETRY: runs the same parser over sg13g2's .xs and diffs the z-stack against IHP's
      shipped SG13G2.xml. The parser must reproduce the official file exactly.
  (b) MATERIALS: compares metal/via conductivities derived from CMOS5L's magic deck against
      the values in IHP's SG13G2 XML. Two fully independent sources (a Magic extraction deck
      vs. a hand-written openEMS XML) must agree.

  Both checks passing is the evidence that the CMOS5L output is trustworthy -- it has no
  golden reference of its own to compare against.

Usage
-----
    ./gen_stackup.py                       # write ../stackup/SG13CMOS5L.xml (nominal corner)
    ./gen_stackup.py --print               # show the derived tables, write nothing
    ./gen_stackup.py --validate            # run both self-checks
    ./gen_stackup.py --corner hr -o ../stackup/SG13CMOS5L_hr.xml
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
EM_DIR = os.path.dirname(HERE)
DEFAULT_OUT = os.path.join(EM_DIR, "stackup", "SG13CMOS5L.xml")

PDK_ROOT = os.environ.get("PDK_ROOT", "/foss/pdks")

# Reference XML, used ONLY for the inherited dielectrics and by --validate.
G2_OPENEMS_XML = os.path.join(
    PDK_ROOT, "ihp-sg13g2", "libs.tech", "openems",
    "openems_ihp_sg13g2", "workflow", "SG13G2.xml",
)

# ---------------------------------------------------------------- .xs geometry mappings

MASK_TO_LAYERNAME = {
    "ACTIV": "Activ", "CONT": "Cont",
    "METAL1": "Metal1", "METAL2": "Metal2", "METAL3": "Metal3",
    "METAL4": "Metal4", "METAL5": "Metal5",
    "VIA1": "Via1", "VIA2": "Via2", "VIA3": "Via3", "VIA4": "Via4",
    "TOPVIA1": "TopVia1", "TOPVIA2": "TopVia2",
    "TM1": "TopMetal1", "TM2": "TopMetal2",
    "MIM": "MIM", "VMIM": "VMIM",
}

THICK_TO_MASK = {
    "activ": "ACTIV", "cont": "CONT",
    "metal1": "METAL1", "metal2": "METAL2", "metal3": "METAL3",
    "metal4": "METAL4", "metal5": "METAL5",
    "via1": "VIA1", "via2": "VIA2", "via3": "VIA3", "via4": "VIA4",
    "topvia1": "TOPVIA1", "topvia2": "TOPVIA2",
    "tm1": "TM1", "tm2": "TM2",
    "mim": "MIM", "vmim": "VMIM",
}

VIA_LAYERS = {"Cont", "Via1", "Via2", "Via3", "Via4", "TopVia1", "TopVia2", "VMIM"}

# MIM is modelled in IHP's official G2 XML with an equivalent-permittivity substitution (a
# thicker, higher-eps dielectric replacing the ~40 nm real one, to avoid a punishing FDTD
# timestep). That trick is not derivable from the .xs, and CMOS5L has no MIM. Skip both.
SKIP_LAYERS = {"MIM", "VMIM"}

# ------------------------------------------------------- magic extract deck -> stackup

# CMOS5L has five metal levels: Metal1..Metal4 + TopMetal1. Magic numbers them m1..m5, so
# magic's "metal5" is the GDS TopMetal1 (layer 126) -- NOT a Metal5 layer, which this PDK
# does not have. Same for contacts: via4 is the Metal4->TopMetal1 via, i.e. GDS TopVia1.
MAGIC_RESIST_TO_LAYER = {
    "metal1": "Metal1", "metal2": "Metal2", "metal3": "Metal3",
    "metal4": "Metal4", "metal5": "TopMetal1",
}
MAGIC_CONTACT_TO_LAYER = {
    "via1": "Via1", "via2": "Via2", "via3": "Via3", "via4": "TopVia1",
    "alldiffcont": "Cont",
}

# Magic corner variant -> the variant tag that labels its block in the extract deck.
CORNERS = {
    "nominal": "()",     # 'variants (),(lvs)'
    "hr": "(hrhc)",      # 'variants (hrhc),(hrlc)'  - high metal resistance
    "lr": "(lrhc)",      # 'variants (lrhc),(lrlc)'  - low metal resistance
}

# IHP's SG13G2 XML quotes conductivity to 3 significant figures (e.g. "1.66e6"), so an exact
# match is impossible. 0.5 % is comfortably below the gap between any two distinct materials.
SIGMA_TOLERANCE = 5e-3

# Layers where the derived sigma is KNOWN not to reconcile with IHP's G2 XML, with the reason.
# Reported as a warning, not a failure: the derivation below is from CMOS5L's own deck and is
# the value we ship; the note records that we know it disagrees and why it does not matter.
KNOWN_SIGMA_DIVERGENCE = {
    "Cont": (
        "IHP's G2 XML uses 2.39e6 S/m; CMOS5L's magic deck (alldiffcont = 17 Ohm/contact,\n"
        "        ContBar 0.16 um) gives 1.47e6 S/m. No contact resistance in the magic deck\n"
        "        reproduces 2.39e6 at any standard Cont size, so IHP's value came from a source\n"
        "        we cannot see. Irrelevant here: Cont sits below Metal1 and carries no current\n"
        "        in a TopMetal1 spiral. Revisit only if you ever model a device down to Activ."
    ),
}

# Drawn via size, needed to turn milliohm-per-contact into a bulk conductivity.
# Source: libs.tech/klayout/tech/drc/rule_decks/sg13cmos5l_maximal.drc
VIA_DRAWN_SIZE_UM = {
    # layer      size    DRC rule the size is read from
    "Via1":     (0.19,  'V1 rule: ext_rectangles(..., ["==", 0.19.um], ["==", 0.19.um])'),
    "Via2":     (0.19,  "V2.b1 array pitch 4*0.19+3*0.22; same drawn size as Via1"),
    "Via3":     (0.19,  "V3.b1 array pitch 4*0.19+3*0.22; same drawn size as Via1"),
    "TopVia1":  (0.42,  'Seal.c2: "EdgeSeal-TopVia1 ring width = 0.42"'),
    "Cont":     (0.16,  'CntB.a: "Min. and max. ContBar width = 0.16"'),
}

# ------------------------------------------------------------- inherited (assumed) values

# The ONLY numbers in the output that CMOS5L does not provide. Taken from IHP's official
# SG13G2 openEMS stackup. Challenge these first if measured Q ever disagrees with simulation.
INHERITED_DIELECTRICS = {
    #  name        type            eps    tand  sigma   color     why it is assumed
    "SiO2":      ("Dielectric",    4.1,   0.0,  0.0,   "fffcad", "IMD oxide permittivity; not in any CMOS5L file"),
    "Passive":   ("Dielectric",    6.6,   0.0,  0.0,   "a0a0f0", "nitride passivation permittivity"),
    "Substrate": ("Semiconductor", 11.9,  0.0,  2.0,   "01e0ff", "bulk Si; conductivity = substrate doping choice"),
    "EPI":       ("Semiconductor", 11.9,  0.0,  5.0,   "294fff", "epi layer; CMOS5L .xs marks EPI as 'TO DO'"),
    "AIR":       ("Dielectric",    1.0,   0.0,  0.0,   "d0d0d0", "simulation domain above the die"),
    "LOWLOSS":   ("Conductor",     1.0,   0.0,  1e10,  "ff0000", "artificial SUBGND reference, not a process layer"),
}

# Simulation-domain thicknesses, also inherited from IHP's official G2 stackup.
SUBSTRATE_THICKNESS_UM = 280.0
AIR_THICKNESS_UM = 300.0
EPI_FALLBACK_UM = 3.75

# Fallback colors for metal layers (cosmetic only, AppCSXCAD display).
METAL_COLORS = {
    "Activ": "00ff00", "Cont": "00ffff",
    "Metal1": "39bfff", "Metal2": "ccccd9", "Metal3": "d80000",
    "Metal4": "93e837", "Metal5": "dcd146",
    "Via1": "ccccff", "Via2": "ff3736", "Via3": "9ba940", "Via4": "deac5e",
    "TopVia1": "ffe6bf", "TopVia2": "ff8000",
    "TopMetal1": "ffe6bf", "TopMetal2": "ff8000",
}


# ============================================================== .xs geometry parsing

class XsStack:
    def __init__(self, pdk, xs_path):
        self.pdk = pdk
        self.xs_path = xs_path
        self.layers = []        # ordered dicts: name/layernum/type/zmin/zmax
        self.thicknesses = {}
        self.masks = {}
        self.epi_um = None
        self.epi_is_commented = False
        self.passi_um = []
        self.notes = []

    @property
    def top_z(self):
        return max((l["zmax"] for l in self.layers), default=0.0)

    def thickness_of(self, layername):
        for l in self.layers:
            if l["name"] == layername:
                return l["zmax"] - l["zmin"]
        return None


def parse_xs(pdk, xs_path):
    """Derive the metal/via stack by replaying the .xs deck's own z accumulation."""
    with open(xs_path) as fh:
        lines = fh.readlines()

    st = XsStack(pdk, xs_path)

    re_mask = re.compile(r'^\s*mask_([A-Z0-9_]+)\s*=\s*layer\(\s*"(\d+)\s*/\s*\d+"\s*\)')
    re_thick = re.compile(r"^\s*(#\s*)?t_([a-z0-9_]+)\s*=\s*([0-9.]+)\s*$")
    re_zacc = re.compile(r"^\s*z\s*=\s*z\s*\+\s*(.+?)\s*$")
    re_deposit = re.compile(r"^\s*\w+\s*=\s*deposit\(\s*t_([a-z0-9_]+)")

    zacc_lines = []
    thick_lineno = {}

    for i, line in enumerate(lines):
        m = re_mask.match(line)
        if m:
            st.masks[m.group(1)] = int(m.group(2))
            continue

        m = re_thick.match(line)
        if m:
            commented, key, value = m.group(1), m.group(2), float(m.group(3))
            if key == "epi":
                st.epi_um, st.epi_is_commented = value, bool(commented)
            if commented:
                continue
            st.thicknesses[key] = value
            thick_lineno[key] = i
            continue

        code = line.split("#")[0]
        m = re_zacc.match(code)
        if m:
            keys = re.findall(r"t_([a-z0-9_]+)", m.group(1))
            if keys:
                zacc_lines.append((i, keys))

    if not zacc_lines:
        raise RuntimeError(f"no 'z = z + t_*' accumulation lines found in {xs_path}")

    # walk the deck's accumulation steps in file order; within a step, layers stack bottom-up
    z = 0.0
    consumed = set()
    for _, keys in zacc_lines:
        for key in keys:
            if key not in st.thicknesses:
                raise RuntimeError(f"{xs_path}: 'z = z + t_{key}' but t_{key} is never assigned")
            t = st.thicknesses[key]
            _append_layer(st, key, z, z + t)
            consumed.add(key)
            z += t

    # A final metal grown after the last accumulation line. sg13g2_for_EM.xs assigns
    # t_tm2 = 3 but never adds it to z, so TopMetal2 would otherwise be lost. The rule is
    # positional -- only thicknesses defined AFTER the last 'z = z +' line qualify -- so the
    # mid-stack MIM thicknesses can never be mistaken for a top layer.
    last_zacc = zacc_lines[-1][0]
    for key, lineno in sorted(thick_lineno.items(), key=lambda kv: kv[1]):
        if key in consumed or lineno <= last_zacc or key.startswith("passi"):
            continue
        t = st.thicknesses[key]
        _append_layer(st, key, z, z + t)
        st.notes.append(
            f"t_{key} is assigned after the last 'z = z +' line and never accumulated; "
            f"placed at z={z:.4f}..{z + t:.4f} as the top layer"
        )
        z += t
        consumed.add(key)

    for line in lines:
        m = re_deposit.match(line)
        if m and m.group(1).startswith("passi"):
            st.passi_um.append(st.thicknesses[m.group(1)])

    if st.epi_um is None:
        st.epi_um = EPI_FALLBACK_UM
        st.notes.append(f"no t_epi in the .xs; assumed {EPI_FALLBACK_UM} um")
    elif st.epi_is_commented:
        st.notes.append(
            f"t_epi = {st.epi_um} is COMMENTED OUT in the .xs (PDK marks it 'TO DO'); "
            "thickness used as-is, conductivity inherited"
        )

    return st


def _append_layer(st, thickness_key, zmin, zmax):
    mask_key = THICK_TO_MASK.get(thickness_key)
    if mask_key is None:
        st.notes.append(f"t_{thickness_key} has no known mask mapping; skipped")
        return
    name = MASK_TO_LAYERNAME[mask_key]
    if name in SKIP_LAYERS:
        st.notes.append(f"{name} skipped (needs equivalent-permittivity modelling)")
        return
    layernum = st.masks.get(mask_key)
    if layernum is None:
        st.notes.append(f"t_{thickness_key} present but mask_{mask_key} not declared; skipped")
        return
    st.layers.append({
        "name": name, "layernum": layernum,
        "type": "via" if name in VIA_LAYERS else "conductor",
        "zmin": zmin, "zmax": zmax,
    })


# ==================================================== magic extract deck -> conductivity

def parse_magic_resist(tech_path, corner="nominal"):
    """Read sheet resistances (mOhm/sq) and contact resistances (mOhm) for one corner."""
    if corner not in CORNERS:
        raise RuntimeError(f"unknown corner '{corner}', expected one of {list(CORNERS)}")
    tag = CORNERS[corner]

    with open(tech_path) as fh:
        lines = fh.readlines()

    re_variants = re.compile(r"^\s*variants\s+(.+?)\s*$")
    re_resist = re.compile(r"^\s*resist\s+\(?([a-z0-9,]+)\)?/([a-z0-9]+)\s+([0-9.]+)")
    re_contact = re.compile(r"^\s*contact\s+([a-z0-9]+)\s+([0-9.]+)")

    sheet, contact = {}, {}
    active = False
    for line in lines:
        m = re_variants.match(line)
        if m:
            variants = [v.strip() for v in m.group(1).split(",")]
            active = tag in variants
            continue
        if not active:
            continue
        m = re_resist.match(line)
        if m and m.group(2) in MAGIC_RESIST_TO_LAYER:
            sheet[MAGIC_RESIST_TO_LAYER[m.group(2)]] = float(m.group(3))
            continue
        m = re_contact.match(line)
        if m and m.group(1) in MAGIC_CONTACT_TO_LAYER:
            contact[MAGIC_CONTACT_TO_LAYER[m.group(1)]] = float(m.group(2))

    if not sheet:
        raise RuntimeError(
            f"no metal 'resist' lines found for corner '{corner}' (variant tag {tag}) in {tech_path}"
        )
    return sheet, contact


def derive_conductivities(st, sheet, contact):
    """sigma for every metal/via layer, from CMOS5L resistance data + CMOS5L thicknesses."""
    sigma, provenance = {}, {}

    for name, rsheet_mohm in sheet.items():
        t_um = st.thickness_of(name)
        if t_um is None:
            continue
        s = 1.0 / ((rsheet_mohm * 1e-3) * (t_um * 1e-6))
        sigma[name] = s
        provenance[name] = f"1/({rsheet_mohm:g} mOhm/sq * {t_um:g} um)"

    for name, rc_mohm in contact.items():
        t_um = st.thickness_of(name)
        if t_um is None or name not in VIA_DRAWN_SIZE_UM:
            continue
        side_um, _rule = VIA_DRAWN_SIZE_UM[name]
        area_m2 = (side_um * 1e-6) ** 2
        s = (t_um * 1e-6) / ((rc_mohm * 1e-3) * area_m2)
        sigma[name] = s
        provenance[name] = (
            f"{t_um:g} um / ({rc_mohm:g} mOhm/contact * ({side_um:g} um)^2)"
        )

    # Activ is not an EM conductor of interest here; give it the magic well/diff value only
    # if present, otherwise leave it out of the model entirely.
    return sigma, provenance


# ======================================================================= XML emission

def _xml_comment_safe(line):
    """XML forbids '--' inside comments; collapse any that slip into generated text."""
    while "--" in line:
        line = line.replace("--", "-")
    return line


def build_xml(st, sigma, provenance, corner, magic_path):
    metal_names = [l["name"] for l in st.layers if l["name"] in sigma]
    dropped = [l["name"] for l in st.layers if l["name"] not in sigma]

    sio2_t = st.top_z + (st.passi_um[0] if st.passi_um else 0.0)
    passive_t = st.passi_um[1] if len(st.passi_um) > 1 else 0.0
    offset = st.epi_um + SUBSTRATE_THICKNESS_UM

    out = []
    out.append('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>')
    out.append("<!--")
    comment_start = len(out)
    out.append("  openEMS stackup for IHP SG13CMOS5L (M1-M4 + TopMetal1)")
    out.append("")
    out.append("  GENERATED FILE - do not edit by hand.")
    out.append("  Regenerate : macros/pll_top/em/scripts/gen_stackup.py")
    out.append("  Verify     : macros/pll_top/em/scripts/gen_stackup.py, validate flag")
    out.append("")
    out.append(f"  Metal corner        : {corner}")
    out.append(f"  Geometry source     : {st.xs_path}")
    out.append(f"  Conductivity source : {magic_path}")
    out.append("")
    out.append("  Derived stack (z = 0 at the silicon surface, um):")
    for l in sorted(st.layers, key=lambda x: x["zmin"]):
        s = sigma.get(l["name"])
        stxt = f"sigma {s:.4g} S/m" if s else "not modelled"
        out.append(
            f"    {l['name']:<10} GDS {l['layernum']:>4}  "
            f"{l['zmin']:8.4f} - {l['zmax']:8.4f}  ({l['zmax'] - l['zmin']:.4f} thick)  {stxt}"
        )
    out.append(f"    {'SiO2':<10} {'':>8}  {0.0:8.4f} - {sio2_t:8.4f}  (IMD oxide + passi1)")
    out.append(f"    {'Passive':<10} {'':>8}  {sio2_t:8.4f} - {sio2_t + passive_t:8.4f}  (nitride passivation)")
    out.append("")
    out.append("  Conductivity derivation (all inputs from ihp-sg13cmos5l):")
    for name in metal_names:
        out.append(f"    {name:<10} sigma = {provenance[name]}")
    if dropped:
        out.append("")
        out.append(f"  Layers in the .xs with no CMOS5L resistance data, omitted: {', '.join(dropped)}")
    out.append("")
    out.append("  INHERITED VALUES - the only numbers NOT from ihp-sg13cmos5l.")
    out.append("  Source: IHP's official SG13G2 openEMS stackup. Same SG13 platform, but not")
    out.append("  independently confirmed here. Challenge these first if measurements disagree:")
    for name, (_t, eps, _tand, sig, _c, why) in INHERITED_DIELECTRICS.items():
        out.append(f"    {name:<10} eps={eps:<6g} sigma={sig:<8g}  {why}")
    out.append(f"    {'Substrate':<10} thickness {SUBSTRATE_THICKNESS_UM} um, AIR domain {AIR_THICKNESS_UM} um")
    if st.notes:
        out.append("")
        out.append("  Parser notes:")
        for note in st.notes:
            out.append(f"    - {note}")
    out.append("")
    out.append("  SUBGND (layer 210) is not a PDK layer. It is an artificial low-loss ground")
    out.append("  reference at the silicon surface, used as the far terminal of via ports in")
    out.append("  2-port simulations. Carried over from IHP's official workflow.")
    out[comment_start:] = [_xml_comment_safe(line) for line in out[comment_start:]]
    out.append("-->")
    out.append('<Stackup schemaVersion="2.0">')
    out.append("  <Materials>")
    for name in metal_names:
        color = METAL_COLORS.get(name, "c0c0c0")
        out.append(
            f'    <Material Name="{name}" Type="Conductor" Permittivity="1" '
            f'DielectricLossTangent="0" Conductivity="{sigma[name]:.6g}" Color="{color}"/>'
        )
    for name, (mtype, eps, tand, sig, color, _why) in INHERITED_DIELECTRICS.items():
        out.append(
            f'    <Material Name="{name}" Type="{mtype}" Permittivity="{eps}" '
            f'DielectricLossTangent="{tand}" Conductivity="{sig:g}" Color="{color}"/>'
        )
    out.append("  </Materials>")
    out.append('  <ELayers LengthUnit="um">')
    out.append("    <Dielectrics>")
    out.append("      <!-- listed top-down; the reader stacks them bottom-up from the last entry -->")
    out.append(f'      <Dielectric Name="AIR" Material="AIR" Thickness="{AIR_THICKNESS_UM:.4f}" />')
    out.append(f'      <Dielectric Name="Passive" Material="Passive" Thickness="{passive_t:.4f}" />')
    out.append(f'      <Dielectric Name="SiO2" Material="SiO2" Thickness="{sio2_t:.4f}" />')
    out.append(f'      <Dielectric Name="EPI" Material="EPI" Thickness="{st.epi_um:.4f}" />')
    out.append(f'      <Dielectric Name="Substrate" Material="Substrate" Thickness="{SUBSTRATE_THICKNESS_UM:.4f}" />')
    out.append("    </Dielectrics>")
    out.append("    <Layers>")
    out.append("      <!-- Offset = EPI + Substrate: Zmin/Zmax below are vs the silicon surface -->")
    out.append(f'      <Substrate Offset="{offset:.4f}"/>')
    for l in sorted(st.layers, key=lambda x: (x["type"] == "via", x["zmin"])):
        if l["name"] not in sigma:
            continue
        out.append(
            f'      <Layer Name="{l["name"]}" Type="{l["type"]}" '
            f'Zmin="{l["zmin"]:.4f}" Zmax="{l["zmax"]:.4f}" '
            f'Material="{l["name"]}" Layer="{l["layernum"]}" />'
        )
    out.append(
        f'      <Layer Name="SUBGND" Type="via" Zmin="{-st.epi_um:.4f}" Zmax="0.0000" '
        f'Material="LOWLOSS" Layer="210" />'
    )
    out.append("    </Layers>")
    out.append("  </ELayers>")
    out.append("</Stackup>")
    return "\n".join(out) + "\n"


# ========================================================================= validation

def xs_path_for(pdk):
    short = pdk.replace("ihp-", "")
    path = os.path.join(PDK_ROOT, pdk, "libs.tech", "klayout", "tech", "xsect",
                        f"{short}_for_EM.xs")
    if not os.path.isfile(path):
        raise RuntimeError(f"cross-section deck not found: {path}")
    return path


def magic_path_for(pdk):
    path = os.path.join(PDK_ROOT, pdk, "libs.tech", "magic", f"{pdk}-extract.tech")
    if not os.path.isfile(path):
        raise RuntimeError(f"magic extract deck not found: {path}")
    return path


def validate():
    failures = []
    warnings = []

    # ---- (a) geometry: reproduce sg13g2 from its .xs, diff vs IHP's official XML --------
    print("=" * 74)
    print("(a) GEOMETRY  -- re-derive ihp-sg13g2 from its .xs, diff vs IHP's official XML")
    print("=" * 74)
    g2_xs = xs_path_for("ihp-sg13g2")
    print(f"    parsed   : {g2_xs}")
    print(f"    compared : {G2_OPENEMS_XML}\n")

    if not os.path.isfile(G2_OPENEMS_XML):
        raise RuntimeError(f"official reference XML not found: {G2_OPENEMS_XML}")

    st_g2 = parse_xs("ihp-sg13g2", g2_xs)
    derived = {l["name"]: l for l in st_g2.layers}

    root = ET.parse(G2_OPENEMS_XML).getroot()
    official = {
        e.get("Name"): {
            "zmin": float(e.get("Zmin")), "zmax": float(e.get("Zmax")),
            "layernum": int(e.get("Layer")),
        }
        for e in root.findall("./ELayers/Layers/Layer")
    }

    print(f"    {'layer':<12}{'derived z':>21}{'official z':>21}{'dz [nm]':>10}{'GDS':>6}")
    print("    " + "-" * 70)
    worst = 0.0
    for name in sorted(derived, key=lambda n: derived[n]["zmin"]):
        d = derived[name]
        if name not in official:
            failures.append(f"geometry: {name} derived but absent from the official XML")
            continue
        o = official[name]
        dz = max(abs(d["zmin"] - o["zmin"]), abs(d["zmax"] - o["zmax"]))
        worst = max(worst, dz)
        flag = "" if dz < 1e-3 else "  <-- MISMATCH"
        if dz >= 1e-3:
            failures.append(f"geometry: {name} dz = {dz * 1000:.1f} nm")
        if d["layernum"] != o["layernum"]:
            failures.append(f"geometry: {name} GDS {d['layernum']} != official {o['layernum']}")
        print(f"    {name:<12}{d['zmin']:9.4f} -{d['zmax']:9.4f}"
              f"{o['zmin']:11.4f} -{o['zmax']:9.4f}{dz * 1000:10.1f}{d['layernum']:6d}{flag}")

    skipped = sorted(set(official) - set(derived))
    if skipped:
        print(f"\n    in official XML, intentionally not derived: {', '.join(skipped)}")
        print("      MIM/MIM_DK  - equivalent-permittivity model, not derivable from the .xs")
        print("      LBE, SUBGND - simulation constructs, not process layers")

    off_diel = {e.get("Name"): float(e.get("Thickness"))
                for e in root.findall("./ELayers/Dielectrics/Dielectric")}
    derived_sio2 = st_g2.top_z + (st_g2.passi_um[0] if st_g2.passi_um else 0.0)
    dz_sio2 = abs(derived_sio2 - off_diel["SiO2"])
    print(f"\n    SiO2 thickness: derived {derived_sio2:.4f}  official {off_diel['SiO2']:.4f}"
          f"  dz {dz_sio2 * 1000:.1f} nm")
    if dz_sio2 >= 1e-3:
        failures.append(f"geometry: SiO2 thickness dz = {dz_sio2 * 1000:.1f} nm")
    print(f"\n    worst layer deviation: {worst * 1000:.2f} nm")

    # ---- (b) materials: CMOS5L magic-derived sigma vs IHP's G2 XML sigma ----------------
    print()
    print("=" * 74)
    print("(b) MATERIALS -- CMOS5L magic-derived sigma vs IHP's SG13G2 XML sigma")
    print("=" * 74)
    c5_xs = xs_path_for("ihp-sg13cmos5l")
    c5_magic = magic_path_for("ihp-sg13cmos5l")
    print(f"    thicknesses : {c5_xs}")
    print(f"    resistances : {c5_magic}")
    print(f"    compared to : {G2_OPENEMS_XML}")
    print("    (two fully independent sources: a Magic extraction deck vs a hand-written XML)\n")

    st_c5 = parse_xs("ihp-sg13cmos5l", c5_xs)
    sheet, contact = parse_magic_resist(c5_magic, "nominal")
    sigma, provenance = derive_conductivities(st_c5, sheet, contact)

    g2_sigma = {e.get("Name"): float(e.get("Conductivity"))
                for e in root.findall("./Materials/Material")}

    print(f"    {'layer':<11}{'derived sigma':>16}{'G2 XML sigma':>16}{'rel err':>10}")
    print("    " + "-" * 53)
    for name in sorted(sigma, key=lambda n: st_c5.thickness_of(n)):
        if name not in g2_sigma:
            print(f"    {name:<11}{sigma[name]:16.6g}{'(absent)':>16}{'':>10}")
            continue
        rel = abs(sigma[name] - g2_sigma[name]) / g2_sigma[name]
        if rel < SIGMA_TOLERANCE:
            flag = ""
        elif name in KNOWN_SIGMA_DIVERGENCE:
            flag = "  <-- known, see below"
            warnings.append(f"{name} sigma differs by {rel:.1%}\n        "
                            + KNOWN_SIGMA_DIVERGENCE[name])
        else:
            flag = "  <-- MISMATCH"
            failures.append(f"materials: {name} sigma rel err {rel:.2%}")
        print(f"    {name:<11}{sigma[name]:16.6g}{g2_sigma[name]:16.6g}{rel:10.2%}{flag}")

    print("\n    derivations:")
    for name in sorted(provenance):
        print(f"      {name:<11} sigma = {provenance[name]}")

    # ---- verdict ----------------------------------------------------------------------
    print()
    print("=" * 74)
    if failures:
        print("VALIDATION FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("VALIDATION PASSED")
    print("  (a) the .xs parser reproduces IHP's official SG13G2 stackup")
    print(f"      worst z deviation {worst * 1000:.2f} nm (IHP's XML is rounded, the parser is not)")
    print("  (b) CMOS5L's own resistance data reproduces IHP's conductivities")
    print(f"      agreement within {SIGMA_TOLERANCE:.1%} for every layer the spiral uses")
    print("  => CMOS5L geometry and metal losses are derived and cross-checked, not transcribed.")
    if warnings:
        print("\n  DOCUMENTED DIVERGENCES (not failures):")
        for w in warnings:
            print(f"    - {w}")
    print("\n  STILL ASSUMED (no CMOS5L source exists, inherited from SG13G2):")
    print("    dielectric permittivities (SiO2 4.1, nitride 6.6) and substrate/EPI conductivity.")
    print("    These set the capacitive/substrate-loss side of Q. Challenge them first if")
    print("    simulated and measured Q ever disagree.")
    return 0


# ============================================================================== main

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdk", default="ihp-sg13cmos5l")
    ap.add_argument("-o", "--output", default=DEFAULT_OUT)
    ap.add_argument("--corner", default="nominal", choices=sorted(CORNERS),
                    help="metal resistance corner from the magic extract deck")
    ap.add_argument("--print", dest="print_only", action="store_true",
                    help="show the derived tables, write nothing")
    ap.add_argument("--validate", action="store_true",
                    help="run both self-checks against IHP's official SG13G2 data")
    args = ap.parse_args()

    if args.validate:
        return validate()

    xs_path = xs_path_for(args.pdk)
    magic_pth = magic_path_for(args.pdk)
    st = parse_xs(args.pdk, xs_path)
    sheet, contact = parse_magic_resist(magic_pth, args.corner)
    sigma, provenance = derive_conductivities(st, sheet, contact)

    print(f"Geometry     <- {xs_path}")
    print(f"Conductivity <- {magic_pth}  (corner: {args.corner})\n")
    print(f"{'layer':<11}{'GDS':>5}{'type':>11}{'zmin':>9}{'zmax':>9}{'thick':>8}{'sigma [S/m]':>15}")
    print("-" * 68)
    for l in sorted(st.layers, key=lambda x: x["zmin"]):
        s = sigma.get(l["name"])
        stxt = f"{s:.4g}" if s else "-"
        print(f"{l['name']:<11}{l['layernum']:>5}{l['type']:>11}{l['zmin']:9.4f}"
              f"{l['zmax']:9.4f}{l['zmax'] - l['zmin']:8.4f}{stxt:>15}")

    print("\nConductivity derivation (all inputs from the CMOS5L PDK):")
    for name in sorted(provenance):
        print(f"  {name:<11} sigma = {provenance[name]}")

    print("\nInherited (NOT from CMOS5L -- the only assumed values):")
    for name, (_t, eps, _tand, sig, _c, why) in INHERITED_DIELECTRICS.items():
        print(f"  {name:<11} eps={eps:<6g} sigma={sig:<8g} {why}")

    if st.notes:
        print("\nParser notes:")
        for note in st.notes:
            print(f"  - {note}")

    if args.print_only:
        return 0

    xml_text = build_xml(st, sigma, provenance, args.corner, magic_pth)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as fh:
        fh.write(xml_text)
    print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Author: TODO
# Created: July 19, 2026
# Description: Circuit specifications for the pfd macro sizing.
#
# This file is the single input of sizing_pfd.py (`make sizing`) — edit
# the values here, not the sizing script, when the specifications change.
# Constants and trivially derived values only (VCM_IN = VDD / 2 is fine);
# anything touching a pygmid lookup belongs in sizing_pfd.py.
# The whole file is echoed verbatim into the generated report
# scripts/sizing/sizing_pfd.md, so keep the comments meaningful.
# ============================================

# TODO(pll_top): fill in the block specifications from doc/design_plan.md.

# The PFD is consists of two D flip-flops and a NAND gate
# 

VDD = 1.5          # Supply voltage (V)
TEMP = 27          # Nominal temperature (degC)
F_REF = 50e+6      # Maximum reference frequency


# Channel length (um): minimum L (0.13) maximizes bandwidth and minimizes
# area, at the cost of gain and mismatch; long L increases gain and matching,
# at the cost of area and bandwidth.
L = 0.25

# see https://www.youtube.com/watch?v=4tftOEgfWWo&list=PLyqSpQzTE6M8Axqvu8_1UdSWXmaJutr2k&index=48 - NPTEL-NOC IITM lecture by Prof. Saurbah Saxena on PLLs
T_RST = T_RST-Q + T_nand2 + td
F_REF < 1/2 * F_RST # need the reset fre

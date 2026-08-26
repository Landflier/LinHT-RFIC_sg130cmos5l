# ~/.config/gnuplot/common.gp
# Shared gnuplot defaults for all figure styles.
# Loaded by ~/.gnuplot at startup.

# Enable string-macro expansion, so commands like @TYPST and @LINESET_OKABE work.
set macros

# -----------------------------------------------------------------------------
# Fonts
# -----------------------------------------------------------------------------
# For cairo/png/svg terminals, these are resolved through fontconfig / Pango.
# In WSL, make sure the fonts are installed and visible to fontconfig.
FONT_TEXT = "STIX Two Text"
FONT_MATH = "STIX Two Math"

# -----------------------------------------------------------------------------
# Shared colors
# -----------------------------------------------------------------------------
# Catppuccin Latte-like document background and foreground colors.
C_LATTE_BG      = "#eff1f5"
C_LATTE_FG      = "#4c4f69"
C_LATTE_GRID    = "#acb0be"
C_WHITE         = "#ffffff"
C_BLACK         = "#000000"

# Named Okabe-Ito colors (first 4)
okabe_blue   = "#0072B2"
okabe_orange = "#D55E00"
okabe_green  = "#009E73"
okabe_pink   = "#CC79A7"

# -----------------------------------------------------------------------------
# Shared categorical line styles
# -----------------------------------------------------------------------------
# Default choice: Okabe-Ito. It is compact, high-contrast, and color-vision-
# deficiency friendly, so it is a safe default for papers, Typst documents,
# and presentation slides.
# Use in plotting commands with: plot ... ls 1, ... ls 2, etc.
LINESET_OKABE = "\
set linetype 1 lc rgb '#0072B2' lw 2 pt 7  ps 1.4; \
set linetype 2 lc rgb '#D55E00' lw 2 pt 13 ps 1.4; \
set linetype 3 lc rgb '#009E73' lw 2 pt 9  ps 1.4; \
set linetype 4 lc rgb '#CC79A7' lw 2 pt 11 ps 1.4; \
set linetype 5 lc rgb '#E69F00' lw 2 pt 5  ps 1.4; \
set linetype 6 lc rgb '#56B4E9' lw 2 pt 3  ps 1.4; \
set linetype 7 lc rgb '#F0E442' lw 2 pt 1  ps 1.4; \
set linetype 8 lc rgb '#000000' lw 2 pt 2  ps 1.4"

# Paul Tol's Bright qualitative scheme – the author's recommended default for
# line plots. Colour-blind safe, print-friendly, distinct on screen and paper.
# Recommended cycling order: blue, red, green, yellow, cyan, purple, grey.
# Reference: https://sronpersonalpages.nl/~pault/
LINESET_TOL_BRIGHT = "\
set linetype 1 lc rgb '#4477AA' lw 2 pt 7  ps 1.4; \
set linetype 2 lc rgb '#EE6677' lw 2 pt 5  ps 1.4; \
set linetype 3 lc rgb '#228833' lw 2 pt 9  ps 1.4; \
set linetype 4 lc rgb '#CCBB44' lw 2 pt 13 ps 1.4; \
set linetype 5 lc rgb '#66CCEE' lw 2 pt 11 ps 1.4; \
set linetype 6 lc rgb '#AA3377' lw 2 pt 3  ps 1.4; \
set linetype 7 lc rgb '#BBBBBB' lw 2 pt 1  ps 1.4; \
set linetype 8 lc rgb '#000000' lw 2 pt 2  ps 1.4"

# -----------------------------------------------------------------------------
# Catppuccin palette – accent colors only (no neutrals/grayscale)
# https://catppuccin.com/palette/
# Usage: plot sin(x) lc rgb cattpuccin_mocha_blue
# -----------------------------------------------------------------------------

# Latte
cattpuccin_latte_rosewater  = "#dc8a78"
cattpuccin_latte_flamingo   = "#dd7878"
cattpuccin_latte_pink       = "#ea76cb"
cattpuccin_latte_mauve      = "#8839ef"
cattpuccin_latte_red        = "#d20f39"
cattpuccin_latte_maroon     = "#e64553"
cattpuccin_latte_peach      = "#fe640b"
cattpuccin_latte_yellow     = "#df8e1d"
cattpuccin_latte_green      = "#40a02b"
cattpuccin_latte_teal       = "#179299"
cattpuccin_latte_sky        = "#04a5e5"
cattpuccin_latte_sapphire   = "#209fb5"
cattpuccin_latte_blue       = "#1e66f5"
cattpuccin_latte_lavender   = "#7287fd"

# Frappé
cattpuccin_frappe_rosewater = "#f2d5cf"
cattpuccin_frappe_flamingo  = "#eebebe"
cattpuccin_frappe_pink      = "#f4b8e4"
cattpuccin_frappe_mauve     = "#ca9ee6"
cattpuccin_frappe_red       = "#e78284"
cattpuccin_frappe_maroon    = "#ea999c"
cattpuccin_frappe_peach     = "#ef9f76"
cattpuccin_frappe_yellow    = "#e5c890"
cattpuccin_frappe_green     = "#a6d189"
cattpuccin_frappe_teal      = "#81c8be"
cattpuccin_frappe_sky       = "#99d1db"
cattpuccin_frappe_sapphire  = "#85c1dc"
cattpuccin_frappe_blue      = "#8caaee"
cattpuccin_frappe_lavender  = "#babbf1"

# Macchiato
cattpuccin_macchiato_rosewater = "#f4dbd6"
cattpuccin_macchiato_flamingo  = "#f0c6c6"
cattpuccin_macchiato_pink      = "#f5bde6"
cattpuccin_macchiato_mauve     = "#c6a0f6"
cattpuccin_macchiato_red       = "#ed8796"
cattpuccin_macchiato_maroon    = "#ee99a0"
cattpuccin_macchiato_peach     = "#f5a97f"
cattpuccin_macchiato_yellow    = "#eed49f"
cattpuccin_macchiato_green     = "#a6da95"
cattpuccin_macchiato_teal      = "#8bd5ca"
cattpuccin_macchiato_sky       = "#91d7e3"
cattpuccin_macchiato_sapphire  = "#7dc4e4"
cattpuccin_macchiato_blue      = "#8aadf4"
cattpuccin_macchiato_lavender  = "#b7bdf8"

# Mocha
cattpuccin_mocha_rosewater = "#f5e0dc"
cattpuccin_mocha_flamingo  = "#f2cdcd"
cattpuccin_mocha_pink      = "#f5c2e7"
cattpuccin_mocha_mauve     = "#cba6f7"
cattpuccin_mocha_red       = "#f38ba8"
cattpuccin_mocha_maroon    = "#eba0ac"
cattpuccin_mocha_peach     = "#fab387"
cattpuccin_mocha_yellow    = "#f9e2af"
cattpuccin_mocha_green     = "#a6e3a1"
cattpuccin_mocha_teal      = "#94e2d5"
cattpuccin_mocha_sky       = "#89dceb"
cattpuccin_mocha_sapphire  = "#74c7ec"
cattpuccin_mocha_blue      = "#89b4fa"
cattpuccin_mocha_lavender  = "#b4befe"

# Select the shared categorical set used by all profiles.
DEFAULT_LINESET = LINESET_OKABE
@DEFAULT_LINESET

# Shared continuous palette for maps/images.
# set palette cubehelix start 0.5 cycles -1.5 saturation 1

# -----------------------------------------------------------------------------
# Shared data/parsing defaults
# -----------------------------------------------------------------------------
set decimalsign '.'
# set datafile separator ','

# -----------------------------------------------------------------------------
# Axes styles
# -----------------------------------------------------------------------------
set ytics nomirror
set xtics nomirror

# -----------------------------------------------------------------------------
# Legend style
# -----------------------------------------------------------------------------
set key right top spacing 0.9

# -----------------------------------------------------------------------------
# Small convenience aliases
# -----------------------------------------------------------------------------
st = "set title"
sx = "set xlabel"
sy = "set ylabel"

# Optional: quick output alias, e.g. @so "figure.svg" is not valid gnuplot syntax,
# so use it as: eval so." 'figure.svg'" if you like; otherwise ignore.
so = "set output"

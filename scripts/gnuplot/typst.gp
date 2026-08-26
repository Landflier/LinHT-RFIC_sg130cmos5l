# ~/.config/gnuplot/typst.gp
# Typst figure profile.
# Intended output: SVG, included in Typst documents compiled with --font-path.

# SVG keeps text as text and names the font; Typst/browser rendering must be able
# to find the font. This matches your current Typst-oriented settings.
set terminal svg enhanced size 1000,700 font "STIX Two Text,16" background rgb "#eff1f5"

# Re-apply shared categorical colors after changing terminal/profile.
@DEFAULT_LINESET

set pointsize 2.1
set grid back lw 1.0 lc rgb "#acb0be"
set border linewidth 1.4 lc rgb "#4c4f69"
set tics out scale 0.8 textcolor rgb "#4c4f69"
set key top right opaque box lw 1.0 spacing 1.25 width 2 samplen 1.6 \
    font "STIX Two Text,14" textcolor rgb "#4c4f69"

# Typst/SVG notes:
# - Use enhanced text syntax for simple super/subscripts, e.g. x^{2}, a_{0}.
# - This is not real Typst/LaTeX math rendering; for that, create labels in Typst
#   or use a LaTeX-oriented terminal in a separate workflow.
# - You can try STIX Two Math in selected labels if the SVG renderer resolves it,
#   e.g. set xlabel "{/STIX Two Math:Italic k}"

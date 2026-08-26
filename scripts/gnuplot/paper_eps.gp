# ~/.config/gnuplot/paper_eps.gp
# Academic paper figure profile.
# Intended output: EPS, single-column width.

# Single-column target: approximately 3.35 in wide. Adjust height if needed.
# epscairo gives EPS output while using cairo/Pango font handling, which is much
# friendlier to STIX fonts in WSL than the classic postscript terminal.
set terminal epscairo enhanced color size 3.35in,2.35in font "STIX Two Text,9" \
    linewidth 1.0 background rgb "white"

@DEFAULT_LINESET

set pointsize 1.1
set grid back lw 0.7 lc rgb "#c9c9c9" dt 3
set border linewidth 1.0 lc rgb "black"
set tics out scale 0.55 textcolor rgb "black"
set key top right opaque box lw 0.7 spacing 1.05 width 1 samplen 1.4 \
    font "STIX Two Text,8" textcolor rgb "black"

# Paper notes:
# - EPS transparency is not something to rely on in publication workflows; white
#   background is the safest default.
# - For true LaTeX-rendered labels, consider a separate cairolatex workflow, but
#   this profile keeps the requested EPS target.
# - If your journal requires a different column width, change the terminal size.

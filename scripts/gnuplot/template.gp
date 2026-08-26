# TODO(name).gp — TODO: what the figure shows, in one line
# Data:   TODO: who produces the table, e.g.
#         python3 pfd_char.py <raw> > data/pfd_char.dat
# Render: gnuplot TODO(name).gp
#
# Styling comes from scripts/gnuplot (loaded via ~/.gnuplot, see README.md
# there). Pick ONE profile below; ls 1..8 are the shared Okabe-Ito line styles
# (colour-blind safe) from common.gp.
#   @TYPST        SVG 1000x700, Typst/Latte background
#   @PAPER        EPS single-column (3.35in), 9 pt
#   @PPT          SVG 960x540 half-slide   (also: @PPT_QUARTER, @PPT_ONE_EIGHT,
#                 @PPT_FULLHD, @PPT_WITH_TITLE)

@TYPST
set output 'figures/TODO.svg'      # extension must match the profile: svg/eps

DATA = 'data/TODO.dat'
# set datafile separator ','       # only for CSV input; default is whitespace

# ---- tags ------------------------------------------------------------------
# Keep units in the label, not the title; 'noenhanced' where names carry
# underscores (net/file names) so gnuplot does not typeset them as subscripts.
set title  'TODO quantity vs condition (TT, 27 {/Symbol \260}C)' noenhanced
set xlabel 'TODO x quantity ({/Symbol m}s)'
set ylabel 'TODO y quantity (V)'
set key top right                  # 'set key off' for single-trace figures
# set y2label 'TODO (unit)'        # second axis: also enable the two lines
# set y2tics                       #   below and plot with 'axes x1y2'
# set logscale x 10
# set format x '10^{%T}'           # decade labels on log axes
# set xrange [*:*]
# set yrange [*:*]

# ---- plot ------------------------------------------------------------------
plot DATA using 1:2 with lines       ls 1 title 'TODO',\
     DATA using 1:3 with linespoints ls 2 title 'TODO'
#    DATA using 1:4 axes x1y2        ls 3 title 'TODO (right axis)'

set output                         # close/flush the output file

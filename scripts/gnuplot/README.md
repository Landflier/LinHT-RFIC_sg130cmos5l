# Shared gnuplot configuration

Vasil's split gnuplot setup (imported from `gnuplot_setup.tar`), versioned here
so every checkout — host or IIC-OSIC-TOOLS container — renders figures
identically. The `.gp` plot scripts in the macros assume these profiles are
loaded.

## Layout

| File | Role |
|---|---|
| `dot_gnuplot` | startup file, linked to `~/.gnuplot`; defines the profile aliases |
| `common.gp` | shared defaults: fonts, Okabe-Ito / Tol / Catppuccin palettes, axes, key |
| `typst.gp` | `@TYPST` — SVG 1000×700, Latte background, for Typst documents |
| `paper_eps.gp` | `@PAPER` — single-column EPS (3.35 in, 9 pt) via epscairo |
| `presentation_svg.gp` | `@PPT` family — slide SVGs (half/quarter/1-8th/full-HD/with-title) |
| `template.gp` | skeleton for new plot scripts (also linked into `~/.vim/templates`) |
| `fonts/` | STIX Two Text/Math OTFs (v2.13, [OFL-licensed](fonts/OFL.txt), from [stipub/stixfonts](https://github.com/stipub/stixfonts)) |
| `install.sh` | idempotent linker: `~/.gnuplot`, `~/.config/gnuplot`, user fonts |

## Applying it

**Container** (redo after the container is recreated; `$HOME` there is not part
of the image):

```sh
docker exec iic-osic-tools_xserver_uid_1000 \
    /foss/designs/LinHT-RFIC-chipalooza_6/scripts/gnuplot/install.sh
```

**Host**: run `scripts/gnuplot/install.sh` (an existing real `~/.gnuplot` is
backed up to `~/.gnuplot.bak`, an existing real `~/.config/gnuplot` directory
is left untouched with a warning).

**Without touching `$HOME`** (CI, one-off shells):

```sh
export GP_CONFIG_DIR=<repo>/scripts/gnuplot   # picked up by dot_gnuplot
```

`gnuplot -d` skips `~/.gnuplot` entirely if an unstyled run is ever needed.

## Usage in plot scripts

```gnuplot
@PAPER
set output 'figures/example.eps'
set xlabel 'x (unit)'
set ylabel 'y (unit)'
plot 'data/example.dat' using 1:2 with linespoints ls 1 title 'measurement'
set output
```

Start new scripts from `template.gp`. Line styles `ls 1..8` are the shared
Okabe-Ito set; alternative palettes (`LINESET_TOL_BRIGHT`, Catppuccin colors)
live in `common.gp`.

## Fonts note

The cairo terminals (`@PAPER`/epscairo) rasterize text through fontconfig, so
the STIX fonts must be installed where gnuplot runs — `install.sh` links the
bundled `fonts/` into `~/.local/share/fonts`. The `svg` terminals only *name*
the font; the file renders with STIX wherever it is viewed (Typst with
`--font-path`, browsers with the font installed).

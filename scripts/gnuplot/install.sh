#!/bin/sh
# Link this repo's gnuplot configuration (and the bundled STIX Two fonts) into
# $HOME, so plain `gnuplot` picks it up automatically. Idempotent — safe to
# re-run. Run it:
#   - inside the IIC-OSIC-TOOLS container, once per container (re)creation:
#       docker exec <container> /foss/designs/LinHT-RFIC-chipalooza_6/scripts/gnuplot/install.sh
#   - or on any host where you want the same setup.
# See README.md in this directory for details.
set -eu

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# ~/.config/gnuplot -> this directory (the loader's default GP_CONFIG_DIR)
mkdir -p "$HOME/.config"
if [ -e "$HOME/.config/gnuplot" ] && [ ! -L "$HOME/.config/gnuplot" ]; then
    echo "warning: $HOME/.config/gnuplot exists and is not a symlink; left untouched." >&2
    echo "         export GP_CONFIG_DIR=$DIR to use the repo config instead." >&2
else
    ln -sfn "$DIR" "$HOME/.config/gnuplot"
fi

# ~/.gnuplot -> the loader (back up a pre-existing real file once)
if [ -e "$HOME/.gnuplot" ] && [ ! -L "$HOME/.gnuplot" ]; then
    mv "$HOME/.gnuplot" "$HOME/.gnuplot.bak"
    echo "note: existing ~/.gnuplot moved to ~/.gnuplot.bak" >&2
fi
ln -sf "$DIR/dot_gnuplot" "$HOME/.gnuplot"

# STIX Two fonts — needed by the cairo terminals (@PAPER/epscairo) which
# rasterize text locally; the svg terminals only reference the font by name.
# fontconfig's user dir is $XDG_DATA_HOME/fonts (the IIC-OSIC-TOOLS container
# sets XDG_DATA_HOME=/headless/.data-default), falling back to ~/.local/share.
# Individual file links so an existing user font dir is never clobbered.
if [ -d "$DIR/fonts" ] && command -v fc-cache >/dev/null 2>&1; then
    FONTDST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"
    mkdir -p "$FONTDST"
    for f in "$DIR"/fonts/*.otf; do
        ln -sf "$f" "$FONTDST/"
    done
    fc-cache -f >/dev/null 2>&1 || true
fi

# vim skeleton for new .gp scripts (only if a vim templates dir is in use)
if [ -d "$HOME/.vim/templates" ]; then
    ln -sf "$DIR/template.gp" "$HOME/.vim/templates/"
fi

echo "gnuplot config linked: ~/.gnuplot and ~/.config/gnuplot -> $DIR"

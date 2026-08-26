# ~/.config/gnuplot/gnuplot_presentation_svg.gp
# PowerPoint / slide figure profile.
# Intended output: transparent SVG, 16:9 aspect ratio.

# Size selector. The main ~/.gnuplot aliases set PPT_FIGSIZE before loading this.
# Available values: "half", "quarter", "one_eight", "fullhd", "ppt_with_title".
if (!exists("PPT_FIGSIZE")) PPT_FIGSIZE = "half"

# --- Font-size conversion note -------------------------------------------
# A PowerPoint widescreen slide is 960 pt × 540 pt (13.33" × 7.5" at 72 pt/in).
# A fullhd SVG (1920×1080) is scaled by 0.5 when it fills the slide, so:
#   PPT visible pt = gnuplot font size × 0.5   (for fullhd variants)
# Example: gnuplot 36  →  18 pt visible in PowerPoint.
# For the half/quarter/one_eight figures the scale depends on how much of
# the slide they occupy, but they are typically used at lower magnification
# so smaller gnuplot values are appropriate.
# -------------------------------------------------------------------------


if (PPT_FIGSIZE eq "one_eight") {
    set terminal svg enhanced size 480,270 font "STIX Two Text,14" background rgb "white"
    PPT_KEY_FONT = '"STIX Two Text,13"'
} else {
if (PPT_FIGSIZE eq "quarter") {
    set terminal svg enhanced size 640,360 font "STIX Two Text,16" background rgb "white"
    PPT_KEY_FONT = '"STIX Two Text,15"'
} else {
    if (PPT_FIGSIZE eq "fullhd") {
        # 1920×1080 fills slide → scale 0.5 → gnuplot 36 ≈ 18 pt in PPT
        set terminal svg enhanced size 1920,1080 font "STIX Two Text,36" background rgb "white"
        PPT_KEY_FONT = '"STIX Two Text,34"'
    } else {
    if (PPT_FIGSIZE eq "ppt_with_title") {
        # 1920×900: leaves ~90 pt of slide height for a two-line 28 pt heading.
        # Same font calibration as fullhd (scale 0.5).
        set terminal svg enhanced size 1920,900 font "STIX Two Text,36" background rgb "white"
        PPT_KEY_FONT = '"STIX Two Text,34"'
    } else {
        set terminal svg enhanced size 960,540 font "STIX Two Text,20" background rgb "white"
        PPT_KEY_FONT = '"STIX Two Text,17"'
    }
    }
}
}


@DEFAULT_LINESET

set pointsize 1.4
# set grid back lw 1.4 lc rgb "#b8b8b8" dt 3
set border linewidth 1.8 lc rgb "black"
set tics out scale 0.9 textcolor rgb "black"
set key top right opaque box lw 1.2 spacing 1.25 width 2 samplen 1.8 \
    font @PPT_KEY_FONT textcolor rgb "black"

# Presentation notes:
# - pngcairo supports transparent PNG output via the 'transparent' terminal option.
# - If your slide background is dark, switch text/border colors to white and use
#   brighter gridlines.
# - For quarter-slide plots, use @PPT_QUARTER instead of @PPT.

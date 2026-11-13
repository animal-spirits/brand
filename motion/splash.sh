#!/bin/sh
# Animal Spirits CLI splash: a red block, then the name set letter by letter. Shown on first launch or --version only.
# Truecolor escapes; terminals without truecolor show the nearest colour. Respects NO_COLOR.
if [ -n "$NO_COLOR" ]; then printf 'animal spirits\n'; exit 0; fi
ink='\033[38;2;236;230;216m'; red='\033[38;2;195;43;31m'; reset='\033[0m'
printf '\033[?25l'
printf "${red}\342\226\210\342\226\210${reset} "
sleep 0.3
for ch in a n i m a l ' ' s p i r i t s; do printf "${ink}%s${reset}" "$ch"; sleep 0.055; done
printf "\n\033[?25h"

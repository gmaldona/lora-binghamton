#!/bin/bash

# CS 526 Internet of Things
# 
# Analysis of LoRa/LoRaWAN Under Varied Environmental Conditions 
# within the Southern Tier Region of New York State
#
# contributors: Annie Wu, Callisto Hess, Gregory Maldonado
# date: 2024-11-15
#
# Thomas J. Watson College of Engineering and Applied Sciences, Binghamton University

git_root=$(git worktree list | cut -d' ' -f1)

if [[ $(uname) == Darwin ]] || [[ $(uname) == Linux ]]; then
    python=python3
else
    python=python
fi

if [ -n $(which $python) ]; then
    $python -m venv venv
    source "$git_root"/venv/bin/activate
    $python -m pip install --upgrade pip
    $python -m pip install -r "$git_root"/requirements.txt
fi

>&2 echo ""
>&2 echo "[DONE] Activate python environment "$git_root"/venv/bin/activate"
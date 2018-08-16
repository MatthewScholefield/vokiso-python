#!/usr/bin/env bash
is_command() { hash "$1" 2>/dev/null; }

#############################################
set -e; cd "$(dirname "$0")" # Script Start #
#############################################

VENV=${VENV-$(pwd)/.venv}

os=$(uname -s)
if [ "$os" = "Linux" ]; then
    if is_command eopkg; then
        sudo eopkg it -y python3 swig portaudio-devel pulseaudio-devel openal-soft miniupnpc
    elif is_command apt-get; then
        sudo apt-get install -y python3-pip swig portaudio19-dev libpulse-dev openal-soft libminiupnpc10
    fi
elif [ "$os" = "Darwin" ]; then
    if is_command brew; then
        brew install portaudio miniupnpc openal-soft
    fi
fi

if [ ! -x "$VENV/bin/python" ]; then python3 -m venv "$VENV" --without-pip; fi
source "$VENV/bin/activate"
if [ ! -x "$VENV/bin/pip" ]; then curl https://bootstrap.pypa.io/get-pip.py | python; fi

pip install -r requirements.txt
pip install -e .

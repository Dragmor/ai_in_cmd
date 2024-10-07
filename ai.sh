#!/bin/bash
cd "/home/fervuld/aiconsole"
source /home/fervuld/aiconsole/env/bin/activate
python /home/fervuld/aiconsole/mistral.py "$@"

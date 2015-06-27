#!/bin/sh
set -e
python build.py
python compile.py $*
node runtime.js $*

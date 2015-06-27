#!/bin/sh
python build.py
python compile.py $*
node runtime.js $*

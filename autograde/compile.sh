#!/bin/sh
cat ./autograde.py > ./autograde.pyx
python cython_autograde.py build_ext --inplace
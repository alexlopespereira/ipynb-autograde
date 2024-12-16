#!/bin/bash
#Usage: ./package.sh 0.0.28 "incremental improvements"
tag=$1
message=$2
rm ./dist/*.gz
sed "s/\${TAG}/${tag}/g" ./setup_template.py >./setup.py

git commit . -m "$message"
git push origin master
git tag "${tag}"
git push origin "${tag}"
#python setup.py sdist
python setup.py build_ext --inplace
python setup.py sdist bdist_wheel
twine upload dist/*

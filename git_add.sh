#!/bin/bash

# This script updates the __version__ variable in Python files and commits all changed
# files to git repo.

function current_version {
	git log --name-only --pretty=format: | sort | uniq -c | sed -e "s/^ *//g" | sort -nr | grep $1 | cut -d" " -f1
}

for file in $(git ls-files -m); do
	version=$(( $(current_version ${file}) + 1 ))
	echo ${file} ${version}
	sed -i -e "s/__version__ = .*/__version__ = \"${version}\"/g" ${file}
	git add ${file}
done
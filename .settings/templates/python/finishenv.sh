#!/bin/bash

# To make environments
cd "$(dirname ${0})"

## ./tools_pyproject.toml >> ~/pyproject.toml
if [ -f ../../../pyproject.toml ]; then
    cat ./tools_pyproject.toml >> ../../../pyproject.toml
fi

## Edit docs/source/conf.py
if [ -f ../../../docs/source/conf.py ]; then
    sed -i -e "s/extensions = \[\]/extensions = \[\n    'sphinx.ext.autodoc',\n    'sphinx.ext.napoleon',\n    'myst_parser'\n\]/g" ../../../docs/source/conf.py
fi

## Get tool name from double-quoted string at the line starting with `name =` in pyproject.toml
TOOLNAME=`grep '^name *= *' ../../../pyproject.toml | sed -E "s/^name *= *['\"]([^'\"]+)['\"].*/\1/"`

## Edit .vscode/tasks.json
if [ -f ../../../.vscode/tasks.json ]; then
    sed -i -e "s/TOOLNAME/${TOOLNAME}/g" ../../../.vscode/tasks.json
fi

## Edit pyproject.toml
if [ -f ../../../pyproject.toml ]; then
    sed -i -e "s/PACKAGENAME/${TOOLNAME}/g" ../../../pyproject.toml
fi

## Rename src/{original_name} to src/{package_name}
if [ -d ../../../src/${TOOLNAME} ]; then
    echo "src/${TOOLNAME} already exists"
else
    SRCDIR=$(ls -d ../../../src/*/ | head -n 1)
    if [ -d "${SRCDIR}" ]; then
        mv "${SRCDIR%/}" "../../../src/${TOOLNAME}"
    fi
fi

# Initialize virtual environment at home directory
cd ../../../
uv sync
. .venv/bin/activate # activate virtual environment

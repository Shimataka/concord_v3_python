#!/bin/bash

# To make environments
cd "$(dirname ${0})"

## Copy ./extensions.json to ~/.vscode/extensions.json
cp ./extensions.json ../../../.vscode/extensions.json

## Copy ./settings.json to ~/.vscode/settings.json
cp ./settings.json ../../../.vscode/settings.json

## Makedir for test
mkdir -p ../../../tests/
touch ../../../tests/.gitkeep

## examples
mkdir -p ../../../examples/
touch ../../../examples/.gitkeep

## Copy .gitignore to ~/
cp ./.gitignore ../../../.gitignore

## Copy ./rustfmt.toml to ~/
cp ./rustfmt.toml ../../../.rustfmt.toml

## git config (core.hooksPath -> .settings/templates/git/hooks)
git config --local core.hooksPath .settings/templates/git/hooks

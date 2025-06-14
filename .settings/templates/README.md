# example_new_repo

## Description

このリポジトリは、GitHubにおける開発環境のセットアップを容易にするためのテンプレートです。
このプロジェクトは、バージョン管理と協力作業のための基本的なテンプレートとして機能します。

## How to use

1. このリポジトリからテンプレートを作成( `Use this template` ボタンから)、
または `.git` 以外の中身を新しいリポジトリにコピーしてください。
1. 目的に合わせて調整してください。
    - Pythonの場合、[Python開発環境の場合](python/template.md)を参照してください。
    - Rustの場合、[Rust開発環境の場合](rust/template.md)を参照してください。
    - Gitによるバージョン管理を行う場合、[Git環境の場合](git/template.md)を参照してください。
    - その他の言語は考慮されていません。希望がある場合はissueにてお願いします。

## Technology stack

| カテゴリー | ツール |
| --- | --- |
| IDE設定 | [EditorConfig](https://editorconfig.org/) |
| CI/CD | [GitHub Actions](https://github.com/features/actions) |
| コードレビュー | [reviewdog](https://github.com/reviewdog/reviewdog) |
| リリース | [semantic-release](https://semantic-release.gitbook.io/semantic-release/) |
| 依存性更新 | [Dependabot](https://docs.github.com/ja/code-security/dependabot) |
| Git commit messages | [commitlint](https://commitlint.js.org/) |
| Credentials | [Secretlint](https://github.com/secretlint/secretlint) |
| Markdown | [markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli) |
| YAML | [yamllint](https://yamllint.readthedocs.io/) |
| GitHub Actions Workflow | [actionlint](https://github.com/rhysd/actionlint) |

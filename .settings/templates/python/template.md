# Python開発環境

今回のテンプレートの説明を以下に示します。

- 仮想環境に [uv]((https://github.com/astral-sh/uv)) を使用します。
- localでpython 3.12を使用します。
- その他のバージョンを使用する場合、
[reviewdog_python.yml](../../../.github/workflows/reviewdog_python.yml)
中のバージョン指定を変更する必要があります。
- 本開発環境で使用したツール一覧

    | カテゴリー | ツール |
    | :---: | :---: |
    | Package & Project manager | [uv](https://github.com/astral-sh/uv) |
    | Linter & Formatter | [ruff](https://github.com/astral-sh/ruff) |
    | Type Checker | [mypy](https://github.com/python/mypy) |
    | Test | [pytest](https://github.com/pytest-dev/pytest) |
    | Docs generator | [Sphinx](https://www.sphinx-doc.org/) |

## How to start

以下の手順に従ってください。

### 0. 拡張機能のインストール

VSCodeの拡張機能の一覧が[.vscode/extensions.json](../../../.vscode/extensions.json)に記載されています。
以下の手順に従うと、この一覧に新たに拡張機能が追加されます。
最終的に一覧に記載されている拡張機能を、VSCodeのUIからインストールしてください。

### 1. リポジトリ内のディレクトリ構成を作成

[.settings/templates/python/makeenv.sh](makeenv.sh) を実行してください。

```bash
.settings/templates/python/makeenv.sh
```

### 2. `uv` をインストール

公式 [uv - Getting Started](https://docs.astral.sh/uv/#getting-started)
に従ってインストールしてください。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

もしくはすでにpythonをインストールしている場合は `pip` からもインストールできます。

```bash
pip install uv
```

インストールできたら、以下のコマンドをターミナルで実行してください。

```bash
uv init --package --python 3.12 # src-layoutでの仮想環境の作成 (python 3.12)
```

### 3. プロジェクト名の設定

プロジェクト名は別に、ツール名を決めてください。
`pyproject.toml` の `[project]` ブロックの `name` にツール名を記載してください。

### 4. 追加したツールの設定ファイルを追記

[.settings/templates/python/finishenv.sh](finishenv.sh) をターミナルで実行してください。

```bash
.settings/templates/python/finishenv.sh

```

### 4. ドキュメントの生成

以下をターミナルで実行してください。

```bash
sphinx-quickstart docs
> ソースディレクトリとビルドディレクトリを分ける（y / n） [n]: y # <-- y にする
> プロジェクト名: <MYPROJECTNAME> # <-- プロジェクト名を入力
> 著者名（複数可）: <YOURNAME> # <-- 著者名を入力
> プロジェクトのリリース []: <VERSION> # <-- バージョンを入力
> プロジェクトの言語 [en]: <LANGUAGE> # <-- 言語を入力 (ja とか)
```

## How to run

### 仮想環境の有効化

```bash
. .venv/bin/activate
```

### コードの実行

`uv` から実行できます。

```bash
uv run src/{example_new_repo}/main.py # main.pyを実行
```

### プリコミットチェック

VSCodeのタスク `py-pre-commit` を実行してください。
[ドキュメントの作成](#ドキュメントの生成)と[コードチェック](#コードチェックの実行)が実行されます。

### ドキュメントの生成

VSCodeのタスク `py-docs-gen` を実行してください。
`Sphinx` が実行され、`docs/build/html/index.html` が生成されます。

また `docs/source/*.rst` ファイルはVSCodeであれば、プレビュー表示が可能です。
右上の「プレビューを横に表示」ボタンを `Alt` と共に押してください。

- uvコマンドが見つからないエラーが出る場合

    [.vscode/tasks.json](../../../.vscode/tasks.json) 中に記述した `~/.cargo/bin/uv` が、
    `which uv` コマンドの出力と一致することを確認してください。

- sphinx-build が見つからないエラーが出る場合

    [.vscode/tasks.json](../../../.vscode/tasks.json) 中に記述した
    `"${workspaceFolder}/.venv/bin/sphinx-build"` が、
    `which sphinx-build` コマンドの出力と一致することを確認してください。

- `Unknown directive type "automodule".` というエラーが出る場合

    `docs/source/conf.py` 中の `extensions` に `'sphinx.ext.autodoc'` が含まれていることを確認してください。

- `document isn't included in any toctree` というエラーが出る場合

    `docs/source/index.rst` に `.. toctree::` ブロックに `modules` が含まれていることを確認してください。

### コードチェックの実行

`mypy` はコードを書けば自動で実行されます。

`Ctrl+s` によって `ruff` が実行されます。

`pytest` はVSCodeのタスク `py-code-check` で実行できますし、VSCodeの拡張機能UIからも実行できます。
`pytest` で算出したカバレッジは、[.pyコード中に色で表示されます](https://zenn.dev/tyoyo/articles/769df4b7eb9398)。
`pytest` に加え、 `ruff` と `mypy` も実行されます。

## Directory structure

構築されたディレクトリ構造は以下の通りです。

```bash
.                       # ルートディレクトリ (project_name)
├── .docs/              # 開発者用ドキュメント
├── .git/               # git
├── .github/            # GitHub用設定ファイル
├── .settings/          # 設定
├── .venv/              # 仮想環境
├── .vscode/            # VSCode用設定ファイル
├── docs/               # ドキュメント
├── examples/           # 使用例
├── local/              # ローカル (git管理外)
├── src/                # ソースコード
│   └── {package_name}  # パッケージ
├── tests/              # テスト
│   └── {package_name}  # パッケージ
├── .editorconfig       # editorconfig
├── .gitignore          # gitignore
├── .python-version     # pythonバージョン
├── LICENSE             # ライセンス
├── pyproject.toml      # 設定ファイル
├── README.md           # README.md
└── uv.lock             # ロックファイル
```

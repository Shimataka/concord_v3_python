# Rust開発環境

- 公式プロジェクト管理ツール [cargo](https://www.rust-lang.org/ja/tools/install/) を使用します。
- 本開発環境で使用したツール一覧

    | カテゴリー | ツール |
    | :---: | :---: |
    | Package & Project manager | [serayuzgur.crates](https://marketplace.cursorapi.com/items?itemName=serayuzgur.crates) |
    | Linter | [rust-lang.rust-analyzer](https://marketplace.cursorapi.com/items?itemName=rust-lang.rust-analyzer) |
    | Test UI | [hbenl.vscode-test-explorer](https://marketplace.cursorapi.com/items?itemName=hbenl.vscode-test-explorer) |
    | Test | [swellaby.vscode-rust-test-adapter](https://marketplace.cursorapi.com/items?itemName=swellaby.vscode-rust-test-adapter) |
    | Docs | [JScearcy.rust-doc-viewer](https://marketplace.cursorapi.com/items?itemName=JScearcy.rust-doc-viewer) |
    | Debug | [vadimcn.vscode-lldb](https://marketplace.cursorapi.com/items?itemName=vadimcn.vscode-lldb) |

## How to start

以下の手順に従ってください。

### 1. リポジトリ内のディレクトリ構成を作成

[.settings/templates/rust/makeenv.sh](makeenv.sh) を実行してください。

```bash
.settings/templates/rust/makeenv.sh
```

### 2. `cargo` をインストール

公式 [cargo - Rust をインストール](https://www.rust-lang.org/ja/tools/install/)
に従ってインストールしてください。

もしくは `curl` を使用してインストールできます。

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

インストールできたら以下のコマンドを実行し、プロジェクトを作成してください。

```bash
cargo new [project_name] # プロジェクトの作成
```

### 3. VSCodeの拡張機能をインストール

VSCodeをエディタとして使う場合、[.vscode/extensions.json](../../../.vscode/extensions.json)
に記載された拡張機能をインストールしてください。

## How to run

### プロジェクトのビルド

```bash
cargo build
```

### プロジェクトの実行

```bash
cargo run
```

### テストの実行

```bash
cargo test
```

または拡張機能 [swellaby.vscode-rust-test-adapter](https://marketplace.cursorapi.com/items?itemName=swellaby.vscode-rust-test-adapter) を使用してください。

### ドキュメントの生成

以下のコマンドにより、 `./target/doc` にドキュメントが生成されます。

```bash
cargo doc
```

または拡張機能 [JScearcy.rust-doc-viewer](https://marketplace.cursorapi.com/items?itemName=JScearcy.rust-doc-viewer) を使用してください。

## Directory structure

構築されたディレクトリ構造は以下の通りです。

```bash
.                       # ルートディレクトリ (project_name)
├── .docs/              # 開発者用ドキュメント
├── .git/               # git
├── .github/            # GitHub用設定ファイル
├── .settings/          # 設定
├── .vscode/            # VSCode用設定ファイル
├── docs/               # ドキュメント
├── examples/           # 使用例
├── local/              # ローカル
├── src/                # ソースコード
│   └── {package_name}  # パッケージ
├── target/             # バイナリなど
├── tests/              # テスト
├── .editorconfig       # editorconfig
├── .gitignore          # gitignore
├── Cargo.lock          # ロックファイル
├── Cargo.toml          # 設定ファイル
├── LICENSE             # ライセンス
├── README.md           # README.md
└── rustfmt.toml        # フォーマットファイル
```

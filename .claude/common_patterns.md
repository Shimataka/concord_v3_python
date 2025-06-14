# common_patterns

頻繁に利用するコマンドパターンや典型的な実装テンプレートなど

## 開発ワークフローでのTIPS

### Python開発

- **コード実行**: `uv run src/{package_name}`  (ディレクトリを指定しても実行可能)
- **コードチェック**: VSCodeタスク`py-code-check`を使用（pytest、ruff、mypyを実行）
- **ドキュメント**: VSCodeタスク`py-docs-gen`を使用（Sphinxドキュメントを生成）
- **Pre-commit**: VSCodeタスク`py-pre-commit`を使用

### Rust開発

- **ビルド**: `cargo build`
- **実行**: `cargo run`
- **テスト**: `cargo test`
- **ドキュメント**: `cargo doc`

## コミットメッセージ要件

このリポジトリはpre-commitフックとCIを通じて[Conventional Commits](https://www.conventionalcommits.org/ja/v1.0.0/)を強制します：

形式: `<type>: <description>`

有効なタイプ: `feat`, `fix`, `build`, `chore`, `ci`, `docs`, `perf`, `refactor`, `style`, `test`

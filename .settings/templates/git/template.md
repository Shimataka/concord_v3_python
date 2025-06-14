# Git環境

本環境においては、以下のルールを採用しています。

- [Conventional Commits](https://www.conventionalcommits.org/ja/v1.0.0/) を使用してコミットメッセージを管理します。このルールに従っているか、Gitのpre-commitフックによるチェックが入ります。このルールについては後述します。
- コミットメッセージはGitHubのCI/CDにおいて、[commitlint](https://commitlint.js.org/) によるチェックが入ります。[semantic-release](https://semantic-release.gitbook.io/semantic-release/) によりリリースノートが自動生成されるよう、ルールに従ってください。

## コミットメッセージのルール (Conventional Commits)

[Conventional Commits](https://www.conventionalcommits.org/ja/v1.0.0/) によるコミットメッセージの記述を行ってください。

実際には、より簡略化したルールを、ここでは採用しています。
具体的に、コミットメッセージは以下のようにしてください。

```bash
<type>: <description>
# <--blank line-->
[optional footer(s)]
```

- `<type>` には、以下のいずれかひとつを選択し指定してください。

| コミットタイプ `<type>:` | 説明 |
| :---: | --- |
| `feat:`     | 新機能 (Minor change) |
| `fix:`      | バグ修正 (Patch change) |
| `build:`    | ビルドシステムまたは外部コードの変更 |
| `chore:`    | ビルドプロセスや補助ツールの変更 |
| `ci:`       | CI/CDの変更 |
| `docs:`     | ドキュメントのみの変更 |
| `perf:`     | パフォーマンスの向上 |
| `refactor:` | コードのリファクタリング |
| `style:`    | コードの書式設定のみの変更 |
| `test:`     | テストのみの変更 |

- `<footer>` には、以下を指定してもよいですし、指定しなくてもよいです。

| フッター `<footer>` | 説明 |
| :---: | --- |
| `BREAKING CHANGE:` | 非互換な変更 |
| `Ref: #123` | チケット/イシューのID #123 |

### `<description>` について

- `<description>` には、コミットの説明を記載してください。

> 引用: [提言: コミットメッセージの一行目には要求仕様を書け](https://qiita.com/magicant/items/882b5142c4d5064933bc)
>
> そのコミットによってプログラムはどんな要件を満たすのかです。そしてプログラムの要件について述べる以上、メッセージは プログラムを主語とする動詞句 で書くべきです。
>
> 例えば、`Add a new feature` よりも `Allow login password longer than 20 characters` のようにしてください。

## Hooks

各種フックにより、コミットメッセージやブランチの命名などのチェックを行っています。

### フック一覧

| フック名 | 説明 |
| :---: | --- |
| pre-commit | コミット前にコミットメッセージのチェックを行います。 |

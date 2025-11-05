# Concord (version 3)

ConcordはDiscord用のBOTアプリケーションです。discord.pyベースで、ツール(Cog)をディレクトリから動的ロードできる構造になっています。初心者は手順通りに進めればすぐ起動でき、上級者はCLI/設定/ツール読み込みの仕様をベースに自由に拡張できます。

## インストール

```bash
pip install -e git+https://github.com/Shimataka/concord_v3_python.git
```

---

## 🚀 クイックスタート（初心者向け：順に辿れば起動）

### 1. Discord BOT準備

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリを作成
2. BOTトークンを取得し有効化
3. BOTをサーバーに招待（少なくとも `applications.commands` 権限）
4. 管理チャンネルを2つ用意してIDを控える
   - `dev_channel`: 起動メッセージやガイダンスを受け取る管理チャンネル
   - `log_channel`: アプリのログを受け取るチャンネル（BOT起動後にDiscordへもログ送信されます）

### 2. プロジェクト作成（最小構成）

- `main.py` を作成：

```python
import asyncio
from pathlib import Path
from concord import Agent

if __name__ == "__main__":
    config_and_log_dirpath = Path(__file__).parent  # configs/ と logs/ を置く場所
    agent = Agent(utils_dirpath=config_and_log_dirpath)
    asyncio.run(agent.run())
```

- `configs/mybot.ini` を作成：

```ini
[Discord.Bot]
name = mybot
description = This is a bot for the my server.

[Discord.API]
token = YOUR_DISCORD_BOT_TOKEN

[Discord.DefaultChannel]
dev_channel = YOUR_DEV_CHANNEL_ID
log_channel = YOUR_LOG_CHANNEL_ID
```

補足:

- `Agent(utils_dirpath=...)` を指定すると、その配下の `configs/` と `logs/` が利用されます（未指定時はパッケージ同梱の `src/concord/configs` を探索）。
- `Discord.DefaultChannel` に指定した2つのIDが必須です。指定チャンネルに起動メッセージとログが送られます。

### 3. 起動

```bash
python3 main.py --bot-name mybot
```

起動後、`dev_channel` に以下のようなメッセージが送信されます：

```markdown
Good morning, Master.
Good work today.
No commands available  # ツールが無い場合
```

### 4. 例をすぐ動かす（任意）

- 基本起動例：

```bash
python examples/ex00_basic_usage/main.py --bot-name testbot
```

- ツールを読み込む例：

```bash
python examples/ex01_load_test_tools/main.py --bot-name testbot \
  --tool-directory-paths examples/ex01_load_test_tools/applications
```

---

## 🔧 上級者向け：仕様と拡張ポイント（漏れなく）

### CLI パラメータ（`concord.cli.arguments.on_launch`）

- `--bot-name` (required, str): 使用する設定 `configs/{bot}.ini` の `{bot}` かつロガー名
- `--tool-directory-paths` (optional, str): ツール探索ディレクトリ（スペース区切り複数可）
  - 相対パスはカレントから解決され、絶対パスに正規化
  - ディレクトリ存在/可読性を検証。無い場合はエラー
  - 指定されたパスに重複がある場合は、一意に解決されます。
- `--is-debug` (optional, flag): ログレベルを DEBUG にし、詳細ログを出力

Agent 初期化時の挙動（抜粋）:

- ロガー: `name=--bot-name`, level=`DEBUG|INFO`, `logs/` にローテート出力
- Config: `configs/API.ini`, `configs/{bot}.ini` を読み込み（`utils_dirpath` 未指定時はデフォルトフォルダ）
- Discord Bot: `Intents.all()` で `Bot` を生成、`on_ready` を上書き
- 起動直後：
  - デフォルトの `OnConnecting` と `OnReady` Cog を追加
  - 指定したツールを動的にロード
  - Discord へのログ送信ハンドラを有効化（`log_channel`）
  - `dev_channel` に挨拶・利用可能コマンド一覧を送信

### 設定ファイル仕様（`concord.infrastructure.config.from_files`）

必須: `configs/{bot}.ini`

```ini
[Discord.Bot]
name = mybot
description = any text

[Discord.API]
token = YOUR_DISCORD_BOT_TOKEN

; 必須: BOTが開発者が使用するチャンネルを指定する (キー→ID)
[Discord.DefaultChannel]
dev_channel = 123456789012345678
log_channel = 234567890123456789

; 任意: ツール除外
[Discord.Tool]
exclusions = [ToolName1, ToolName2]

; 任意: 利便用チャンネル辞書（キー→ID）
[Discord.Channel]
general = 345678901234567890
announcements = 456789012345678901
```

ポイント:

- `Discord.Tool.exclusions`: 文字列リスト記法（空白/句読点区切りをパース）
- `Discord.Channel`: 任意。`Agent.cached_channels.get_channel_from_key(key="general")` のように参照可能
- `Agent.config.api.get_api_token(developer, key)`: `configs/API.ini` から任意のAPIキー取得に利用

`configs/API.ini` の例:

```ini
[dev1]
api1 = YOUR_API_KEY_1

[dev2]
api2 = YOUR_API_KEY_2
```

### ツール（Cog）の動的ロード仕様（`dynamic_import.import_classes_from_directory`）

- 検索対象は `--tool-directory-paths` で指定された各ディレクトリ（再帰で `**/*.py`）
- ファイル名が `__tool__.py` に一致するモジュールのみを対象
- モジュール内で `discord.ext.commands.Cog` を継承したクラスを全て収集
- 各クラスは `agent: Agent` を引数とする `__init__` を持つこと
- 読み込み後に `bot.add_cog(LoadedClass(agent=self))` される

最小ツール例（`my_tools/__tool__.py`）:

```python
from discord.ext.commands import Cog, Context, hybrid_command
from concord import Agent

class MyTool(Cog):
    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    @hybrid_command()
    async def hello(self, ctx: Context) -> None:  # type: ignore[reportUnknownReturnType]
        await ctx.send("Hello")
```

実行時に読み込む:

```bash
python main.py --bot-name mybot --tool-directory-paths my_tools
```

複数ディレクトリ指定:

```bash
python main.py --bot-name mybot \
  --tool-directory-paths "./tools_alpha ./tools_beta/subdir"
```

### チャンネルキャッシュと取得API（`CachedChannels`）

- `Agent.cached_channels.dev_channel` / `log_channel` は ID に基づいて遅延取得 + キャッシュ
- 任意チャンネル取得:
  - `get_channel_from_key(key: str)` → `configs/{bot}.ini` の `[Discord.Channel]` キーで参照
  - `get_channel_from_id_or_name(_id: int | None, channel_name: str | None)` → ID優先で解決

### ログとデバッグ

- `--is-debug` で詳細ログ（DEBUG）
- ファイル出力: `logs/{bot}.log`（`Agent(utils_dirpath=...)` 配下）
- 起動後に Discord 側 `log_channel` へもログ送出（`DiscordLogHandler`）

---

## 公式サンプル

- `examples/ex00_basic_usage/main.py` — 最小起動
- `examples/ex01_load_test_tools/main.py` — ツール読み込み（`applications/` 配下サンプル：`tool1`, `tool2`）

---

## トラブルシューティング（要点）

- 起動時に `--bot-name` は必須。未指定だとエラー
- `--tool-directory-paths` は存在ディレクトリのみ有効（相対はCWDから解決→絶対化）
- `configs/{bot}.ini` が見つからない/読めない場合は失敗（`Agent(utils_dirpath=...)` 配下を優先）
- `Discord.DefaultChannel` のIDが不正だと、起動後のチャンネル解決でエラー

---

## 参考リンク

- Discord.py ドキュメント: [https://discordpy.readthedocs.io/ja/latest/](https://discordpy.readthedocs.io/ja/latest/)
- スラッシュコマンド: [https://discordpy.readthedocs.io/ja/latest/ext/commands/commands.html](https://discordpy.readthedocs.io/ja/latest/ext/commands/commands.html)
- イベントリファレンス: [https://discordpy.readthedocs.io/ja/latest/api.html#event-reference](https://discordpy.readthedocs.io/ja/latest/api.html#event-reference)

# Concord (version 3)

ConcordはDiscord用のBOTアプリケーションです。AIによる会話機能とDiscordのボイスチャットを使用した音声機能を含んでおり、非常に拡張性の高い機能を簡単に実装できるようにコードが構築されています。

Concord is a BOT application for Discord. It includes conversation features with AI and sound features using Discord's voice chat, and the code is constructed to make it easy to implement highly extensible features.

## インストール

```bash
pip install -e git+https://github.com/Shimataka/concord_v3_python.git
```

## 🚀 クイックスタート（とにかく動かしたい人向け）

### 1. Discord BOTの設定

1. [Discord Developer Portal](https://discord.com/developers/applications)でアプリケーションを作成
2. BOTトークンを取得
3. サーバーに招待（`applications.commands`権限が必要）
4. 管理者用チャンネルIDを取得

### 2. 必要なファイルを作成

ここでは `mybot` というBOTを作成します。
他の名前にする場合は、以下の記述の `mybot` を変更してください。

**`main.py`** を作成：

```python
import asyncio
from pathlib import Path
from concord import Agent

if __name__ == "__main__":
    config_and_log_dirpath = Path(__file__).parent  # configとlogを保存するディレクトリ
    agent = Agent(utils_dirpath=config_and_log_dirpath)
    asyncio.run(agent.run())
```

**`configs/mybot.ini`** を作成：

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

> [!WARNING]
> **重要な設定**
>
> - `dev_channel`: BOTとメッセージを送受信する管理者用チャンネル
> - `log_channel`: BOTのログを表示するチャンネル
> - 両方とも管理者権限を持つユーザーがアクセスできるチャンネルである必要があります

### 3. 実行

```bash
python3 main.py --bot-name mybot
```

これで基本的なBOTが動作します！

dev_channelにIDを指定したチャンネルにメッセージが送信されます

```markdown
Good morning, Master.
Good work today.
No commands available  # ツールがない場合のメッセージ
```

---

## 🔧 詳細設定（凝った設定がしたい人向け）

### 高度な設定ファイル

**`configs/mybot.ini`** の完全版：

```ini
[Discord.Bot]
name = mybot
description = This is a bot for the my server.

[Discord.API]
token = YOUR_DISCORD_BOT_TOKEN

[Discord.DefaultChannel]
dev_channel = YOUR_DEV_CHANNEL_ID
log_channel = YOUR_LOG_CHANNEL_ID

[Discord.Tool]
exclusions = [ToolName1, ToolName2]  # 除外するツール(詳細は以下)

[Discord.Channel]
general = CHANNEL_ID_1
# Agent.cached_channels.get_channel_from_key(key="general")で取得できる
announcements = CHANNEL_ID_2
# Agent.cached_channels.get_channel_from_key(key="announcements")で取得できる
```

**`configs/API.ini`** （外部API使用時）：

```ini
[dev1]
api1 = YOUR_API_KEY_1
# Agent.config.api.get_api_token(developer="dev1", key="api1")で取得できる
[dev2]
api2 = YOUR_API_KEY_2
# Agent.config.api.get_api_token(developer="dev2", key="api2")で取得できる
```

### カスタムツールの追加

1. **ツールディレクトリを作成**：

    ```bash
    mkdir my_tools
    ```

2. **`my_tools/__tool__.py`** を作成：

    ```python
    import discord
    from discord.ext import commands

    class MyCustomTool(commands.Cog):
        def __init__(self, agent: Agent):
            self.agent = agent

        @commands.slash_command(name="hello")
        async def hello(self, ctx):
            await ctx.respond("Hello, World!")
    ```

3. **ツール付きで実行**：

    ```bash
    python3 main.py --bot-name mybot --tool-directory-paths my_tools
    ```

### デバッグモード

```bash
python3 main.py --bot-name mybot --is-debug
```

ログは `logs/mybot.log` に出力されます。

---

## 📚 参考情報

- [examples/ex00_basic_usage](examples/ex00_basic_usage/main.py) - 基本的なBOTのサンプル
- [examples/ex01_load_test_tools](examples/ex01_load_test_tools/main.py) - ツールのサンプル
- [Discord.py ドキュメント](https://discordpy.readthedocs.io/ja/latest/)
- [スラッシュコマンド](https://discordpy.readthedocs.io/ja/latest/ext/commands/commands.html)
- [イベントリファレンス](https://discordpy.readthedocs.io/ja/latest/api.html#event-reference)

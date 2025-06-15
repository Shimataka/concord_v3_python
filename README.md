# Concord (version 3)

ConcordはDiscord用のBOTアプリケーションです。AIによる会話機能とDiscordのボイスチャットを使用した音声機能を含んでおり、非常に拡張性の高い機能を簡単に実装できるようにコードが構築されています。

Concord is a BOT application for Discord. It includes conversation features with AI and sound features using Discord's voice chat, and the code is constructed to make it easy to implement highly extensible features.

## Getting Started

### How to install

- `concord/main.py`でBOTのインスタンスを作成します
- BOTの名前 (`bot_name="Dexneuf"`となっている箇所) は、自由に決めることができます
- この`bot_name`は、`concord/configs`に配置する設定ファイル`*.ini`と紐づけられます
- `concord/configs`に`<bot_name>.ini`を配置して、次のように記述してください

```python
# concord/configs/{bot_name}.ini
[Discord.API]
token = {Discord token}

[Discord.DefaultChannel]
dev_channel = {ID of a text channel}
log_channel = {ID of another (same will be OK) text channel}

[Discord.Tool]
exclusions = [{ExcludedTools1}, {ExcludedTools2}, ...]

[Discord.Channel]
{channel name1} = {channel id1}
{channel name2} = {channel id2}
...
```

> [!WARNING]
> DiscordからBOTに対して配布されたtokenと、管理者チャンネルのIDが2つ必要です。管理者用チャンネルは `dev_channel` と `log_channel` の2つです。`dev_channel` は、BOTとメッセージを送受信するチャンネルで、管理者権限でのコマンドの送信も行います。したがって、`dev_channel` は、管理者権限を持つユーザーがメッセージを送信できるチャンネルである必要があります。`log_channel` は、BOTが起動している間のログを見るためのチャンネルです。こちらはメッセージの送信は行いません。

`exclusions`オプションはBOTの登録をスキップするクラス名を記述するものです。ここに記述された文字列と同名のクラスは、BOTへの登録がされません。

さらに `concord/configs/API.ini` を配置することで、 `concord/tools` などで使用するAPI tokenをBOT経由でアクセスできます。

```python
# concord/configs/API.ini
[section_name1]  # lower case
option1 = {API token}
option2 = {API token}

[section_name2]  # lower case
option3 = {API token}
option4 = {API token}
```

## How to use the BOT

次のようなコマンドを実行するだけです。

```bash
> python3 concord/main.py --bot-name {bot_name}  # Normal mode
> python3 concord/main.py --bot-name {bot_name} --is-debug  # Debug mode
```

実行時のログは、`concord/logs/{bot_name}.log` に出力されます。通常モードとデバッグモードで、logファイル中の[記述量が変わります](https://discordpy.readthedocs.io/ja/latest/api.html#discord.utils.setup_logging)。

## Manual

### Tutorial

### ツール登録方法

BOTに[スラッシュコマンド](https://discordpy.readthedocs.io/ja/latest/ext/commands/commands.html)を実装します。`concord/tools` に `__tool__.py` を配置すると、そこに書かれたクラスのうち `discord.ext.commands.Cog` を継承したクラスは、BOTの起動時に自動で読み込みます。スラッシュコマンド以外にも、メッセージのポストなどの[イベント](https://discordpy.readthedocs.io/ja/latest/api.html#event-reference)に反応して実行する処理や、スケジューリングされた処理を行うことが可能です。定期実行したい場合は、[discord.pyのtaskヘルパー例](https://discordpy.readthedocs.io/ja/latest/ext/tasks/index.html)を参考にしてください。

### 実装済みのツール一覧

実装したツールの一覧をアルファベット順に表示。

| ツール名 | 機能 |
| :---: | :--- |

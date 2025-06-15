# プロジェクトコンテキスト

## 概要

- プロジェクト名: concord
- 技術スタック:
  - Python
  - discord.py
  - クリーンアーキテクチャ
- 目標: discordで動作するBOTを作成する。

## 制約条件

- ツールのディレクトリパスを `--tool-directory-paths` オプションで指定して、ツールを読み込む。
- ツールは、discord.pyのCogを継承したクラスである。
- ツールは、`__tool__.py`というファイル名から動的に読み込む。

## 技術選定理由

- Pythonはライブラリが豊富で、開発が容易
- discord.pyは、discordのAPIを簡単に利用できるライブラリ
- クリーンアーキテクチャは、コードの保守性を高めるためのアーキテクチャ

## Plugin System

- ツールは、`__tool__.py`というファイル名から動的に読み込む。
- ツールは、discord.pyのCogを継承したクラスである。
- ツールは、ツールディレクトリ内の`__tool__.py`ファイルから自動的に読み込まれる。
- ツールは、設定ファイルで除外リストをサポートしている。

## Configuration Files

Botは、`concord/configs/`ディレクトリに設定ファイルを配置する必要がある。

- `{bot_name}.ini`: Discord token, channels, tool exclusions
- `API.ini`: External API tokens (optional)

## Important patterns

- `pyresults`ライブラリを使用して、例外の代わりに関数エラー処理を行う。
- キャッシュを使用したDiscordチャンネルの遅延読み込み
- discord.pyのイベントシステムを活用したイベント駆動型アーキテクチャ
- ジェネリック制約を使用した型安全な動的インポート
- Discord統合を使用したロガーのファクトリパターン

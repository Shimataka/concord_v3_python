"""00_basic_usage

このサンプルでは、BOTの基本的な使用方法を示します。

このサンプルにおけるポイント:
    1. `Agent` をimportする
    2. `Agent` のインスタンスを作成し、引数としてconfigsやlogsを置いてもよいディレクトリを指定する
    3. `Agent` のrunメソッドを、asyncio.run()内で実行すると、BOTが起動して常駐する
        ```bash
        examples/ex00_basic_usage$ python main.py --bot-name testbot
        ```
"""

import asyncio
from pathlib import Path

from concord import Agent

if __name__ == "__main__":
    config_and_log_dirpath = Path(__file__).parent
    agent = Agent(utils_dirpath=config_and_log_dirpath)
    asyncio.run(agent.run())

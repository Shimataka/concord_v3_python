"""01_load_test_tools

このサンプルでは、BOTにツールを読み込ませる方法を示します。

このサンプルにおけるポイント:
    1. `Agent` をimportする
    2. `Agent` のインスタンスを作成し、引数としてconfigsやlogsを置いてもよいディレクトリを指定する
    3. `Agent` のrunメソッドを、asyncio.run()内で実行すると、BOTが起動して常駐する
    4. ツールを読み込ませるには、コマンドを実行する際に、ツールが置いてあるディレクトリを指定する
        ```bash
        examples/ex01_load_test_tools$ python main.py --bot-name testbot \
            --tool-directory-paths applications
        ```
"""

import asyncio
from pathlib import Path

from concord import Agent

if __name__ == "__main__":
    config_and_log_dirpath = Path(__file__).parent
    agent = Agent(utils_dirpath=config_and_log_dirpath)
    asyncio.run(agent.run())

import asyncio

from concord import Agent

if __name__ == "__main__":
    agent = Agent()
    asyncio.run(agent.run())

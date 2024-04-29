import asyncio
import argparse
import toml
from seeact.agent import SeeActAgent
async def run_agent():
    agent = SeeActAgent(default_task="terminate",openai_key="Your API KEY Here")
    await agent.start()
    while not agent.complete_flag:
        prediction_dict = await agent.predict()
        await agent.execute(prediction_dict)
    await agent.stop()

if __name__ == "__main__":
    asyncio.run(run_agent())

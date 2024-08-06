import asyncio
import os
from seeact.agent import SeeActAgent
import json

# Setup your API Key here, or pass through environment
# os.environ["OPENAI_API_KEY"] = "Your API KEY Here"
# os.environ["GEMINI_API_KEY"] = "Your API KEY Here"

batch = [
    "5b0eace3-c385-4f9e-8ce8-cdd9e58f1ea7"
]

async def run_agent(task_id, website, confirmed_task, grounding):
    agent = SeeActAgent(
        model="gpt-4o",
        default_task=confirmed_task,
        default_website=website,
        save_file_dir=f"{task_id}_{grounding}",
        grounding_strategy=grounding,
        max_auto_op=30,
        max_continuous_no_op=3,
    )
    await agent.start()
    while not agent.complete_flag:
        prediction_dict = await agent.predict()
        await agent.execute(prediction_dict)
    await agent.stop()

if __name__ == "__main__":
    with open("../data/online_tasks/merged_online_90_tasks.json", "r") as file:
        tasks = json.load(file)

    for task in tasks:
        if task["task_id"] in batch:
            print(f"Performing task: {task}")
            # asyncio.run(run_agent(grounding="text_choice_som", task_id=task["task_id"], website=task["website"], confirmed_task=task["confirmed_task"]))
            asyncio.run(run_agent(grounding="text_choice", task_id=task["task_id"], website=task["website"], confirmed_task=task["confirmed_task"]))

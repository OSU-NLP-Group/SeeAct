# -*- coding: utf-8 -*-
# Copyright (c) 2024 OSU Natural Language Processing Group
#
# Licensed under the OpenRAIL-S License;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.licenses.ai/ai-pubs-open-rails-vz1
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This script leverages the GPT-4V API and Playwright to create a web agent capable of autonomously performing tasks on webpages.
It utilizes Playwright to create browser and retrieve interactive elements, then apply [SeeAct Framework](https://osu-nlp-group.github.io/SeeAct/) to generate and ground the next operation.
The script is designed to automate complex web interactions, enhancing accessibility and efficiency in web navigation tasks.
"""

import argparse
import asyncio
import datetime
import json
import logging
import os
import warnings
from dataclasses import dataclass

import toml
import torch
from aioconsole import ainput, aprint
from playwright.async_api import async_playwright

from data_utils.format_prompt_utils import get_index_from_option_name
from data_utils.prompts import generate_prompt, format_options
from demo_utils.browser_helper import (normal_launch_async, normal_new_context_async,
                                       get_interactive_elements_with_playwright, select_option, saveconfig)
from demo_utils.format_prompt import format_choices, format_ranking_input, postprocess_action_lmm
from demo_utils.inference_engine import OpenaiEngine
from demo_utils.ranking_model import CrossEncoder, find_topk
from demo_utils.website_dict import website_dict

# Remove Huggingface internal warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=UserWarning)


@dataclass
class SessionControl:
    pages = []
    cdp_sessions = []
    active_page = None
    active_cdp_session = None
    context = None
    browser = None


session_control = SessionControl()


#
# async def init_cdp_session(page):
#     cdp_session = await page.context.new_cdp_session(page)
#     await cdp_session.send("DOM.enable")
#     await cdp_session.send("Overlay.enable")
#     await cdp_session.send("Accessibility.enable")
#     await cdp_session.send("Page.enable")
#     await cdp_session.send("Emulation.setFocusEmulationEnabled", {"enabled": True})
#     return cdp_session


async def page_on_close_handler(page):
    # print("Closed: ", page)
    if session_control.context:
        # if True:
        try:
            await session_control.active_page.title()
            # print("Current active page: ", session_control.active_page)
        except:
            await aprint("The active tab was closed. Will switch to the last page (or open a new default google page)")
            # print("All pages:")
            # print('-' * 10)
            # print(session_control.context.pages)
            # print('-' * 10)
            if session_control.context.pages:
                session_control.active_page = session_control.context.pages[-1]
                await session_control.active_page.bring_to_front()
                await aprint("Switched the active tab to: ", session_control.active_page.url)
            else:
                await session_control.context.new_page()
                try:
                    await session_control.active_page.goto("https://www.google.com/", wait_until="load")
                except Exception as e:
                    pass
                await aprint("Switched the active tab to: ", session_control.active_page.url)


async def page_on_navigatio_handler(frame):
    session_control.active_page = frame.page
    # print("Page navigated to:", frame.url)
    # print("The active tab is set to: ", frame.page.url)


async def page_on_crash_handler(page):
    await aprint("Page crashed:", page.url)
    await aprint("Try to reload")
    page.reload()


async def page_on_open_handler(page):
    # print("Opened: ",page)
    page.on("framenavigated", page_on_navigatio_handler)
    page.on("close", page_on_close_handler)
    page.on("crash", page_on_crash_handler)
    session_control.active_page = page
    # print("The active tab is set to: ", page.url)
    # print("All pages:")
    # print('-'*10)
    # print(session_control.context.pages)
    # print("active page: ",session_control.active_page)
    # print('-' * 10)


async def main(config, base_dir) -> None:
    # basic settings
    is_demo = config["basic"]["is_demo"]
    ranker_path = None
    try:
        ranker_path = config["basic"]["ranker_path"]
        if not os.path.exists(ranker_path):
            ranker_path = None
    except:
        pass

    save_file_dir = os.path.join(base_dir, config["basic"]["save_file_dir"]) if not os.path.isabs(
        config["basic"]["save_file_dir"]) else config["basic"]["save_file_dir"]
    save_file_dir = os.path.abspath(save_file_dir)
    default_task = config["basic"]["default_task"]
    default_website = config["basic"]["default_website"]

    # Experiment settings
    task_file_path = os.path.join(base_dir, config["experiment"]["task_file_path"]) if not os.path.isabs(
        config["experiment"]["task_file_path"]) else config["experiment"]["task_file_path"]
    overwrite = config["experiment"]["overwrite"]
    top_k = config["experiment"]["top_k"]
    fixed_choice_batch_size = config["experiment"]["fixed_choice_batch_size"]
    dynamic_choice_batch_size = config["experiment"]["dynamic_choice_batch_size"]
    max_continuous_no_op = config["experiment"]["max_continuous_no_op"]
    max_op = config["experiment"]["max_op"]
    highlight = config["experiment"]["highlight"]
    monitor = config["experiment"]["monitor"]
    dev_mode = config["experiment"]["dev_mode"]

    try:
        storage_state = config["basic"]["storage_state"]
    except:
        storage_state = None

    # openai settings
    openai_config = config["openai"]
    if openai_config["api_key"] == "Your API Key Here":
        raise Exception(
            f"Please set your GPT API key first. (in {os.path.join(base_dir, 'config', 'demo_mode.toml')} by default)")

    # playwright settings
    save_video = config["playwright"]["save_video"]
    viewport_size = config["playwright"]["viewport"]
    tracing = config["playwright"]["tracing"]
    locale = None
    try:
        locale = config["playwright"]["locale"]
    except:
        pass
    geolocation = None
    try:
        geolocation = config["playwright"]["geolocation"]
    except:
        pass
    trace_screenshots = config["playwright"]["trace"]["screenshots"]
    trace_snapshots = config["playwright"]["trace"]["snapshots"]
    trace_sources = config["playwright"]["trace"]["sources"]

    # Initialize Inference Engine based on OpenAI API
    generation_model = OpenaiEngine(**openai_config, )

    # Load ranking model for prune candidate elements
    ranking_model = None
    if ranker_path:
        ranking_model = CrossEncoder(ranker_path, device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                                     num_labels=1, max_length=512, )

    if not is_demo:
        with open(f'{task_file_path}', 'r', encoding='utf-8') as file:
            query_tasks = json.load(file)
    else:
        query_tasks = []
        task_dict = {}
        task_input = await ainput(
            f"Please input a task, and press Enter. \nOr directly press Enter to use the default task: {default_task}\nTask: ")
        if not task_input:
            task_input = default_task
        task_dict["confirmed_task"] = task_input
        website_input = await ainput(
            f"Please input the complete ulr of the starting website, and press Enter. The URL must be complete (for example, including http), to ensure the browser can successfully load the webpage. \nOr directly press Enter to use the default website: {default_website}\nWebsite: ")
        if not website_input:
            website_input = default_website
        task_dict["website"] = website_input
        # set the folder name as current time
        current_time = datetime.datetime.now()
        file_name = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        task_dict["task_id"] = file_name
        query_tasks.append(task_dict)

    for single_query_task in query_tasks:
        confirmed_task = single_query_task["confirmed_task"]
        confirmed_website = single_query_task["website"]
        try:
            confirmed_website_url = website_dict[confirmed_website]
        except:
            confirmed_website_url = confirmed_website
        task_id = single_query_task["task_id"]
        main_result_path = os.path.join(save_file_dir, task_id)

        if not os.path.exists(main_result_path):
            os.makedirs(main_result_path)
        else:
            await aprint(f"{main_result_path} already exists")
            if not overwrite:
                continue
        saveconfig(config, os.path.join(main_result_path, "config.toml"))

        # init logger
        # logger = await setup_logger(task_id, main_result_path)
        logger = logging.getLogger(f"{task_id}")
        logger.setLevel(logging.INFO)
        log_fh = logging.FileHandler(os.path.join(main_result_path, f'{task_id}.log'), encoding='utf-8')
        log_fh.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        log_format = logging.Formatter('%(asctime)s - %(message)s')
        terminal_format = logging.Formatter('%(message)s')
        log_fh.setFormatter(log_format)
        console_handler.setFormatter(terminal_format)
        logger.addHandler(log_fh)
        logger.addHandler(console_handler)

        logger.info(f"website: {confirmed_website_url}")
        logger.info(f"task: {confirmed_task}")
        logger.info(f"id: {task_id}")
        async with async_playwright() as playwright:
            session_control.browser = await normal_launch_async(playwright)
            session_control.context = await normal_new_context_async(session_control.browser,
                                                                     tracing=tracing,
                                                                     storage_state=storage_state,
                                                                     video_path=main_result_path if save_video else None,
                                                                     viewport=viewport_size,
                                                                     trace_screenshots=trace_screenshots,
                                                                     trace_snapshots=trace_snapshots,
                                                                     trace_sources=trace_sources,
                                                                     geolocation=geolocation,
                                                                     locale=locale)
            session_control.context.on("page", page_on_open_handler)
            await session_control.context.new_page()
            try:
                await session_control.active_page.goto(confirmed_website_url, wait_until="load")
            except Exception as e:
                logger.info("Failed to fully load the webpage before timeout")
                logger.info(e)
            await asyncio.sleep(3)

            taken_actions = []
            complete_flag = False
            monitor_signal = ""
            time_step = 0
            no_op_count = 0
            valid_op_count = 0

            while not complete_flag:
                if dev_mode:
                    logger.info(f"Page at the start: {session_control.active_page}")
                await session_control.active_page.bring_to_front()
                terminal_width = 10
                logger.info("=" * terminal_width)
                logger.info(f"Time step: {time_step}")
                logger.info('-' * 10)
                elements = await get_interactive_elements_with_playwright(session_control.active_page)

                if tracing:
                    await session_control.context.tracing.start_chunk(title=f'{task_id}-Time Step-{time_step}',
                                                                      name=f"{time_step}")
                logger.info(f"# all elements: {len(elements)}")
                if dev_mode:
                    for i in elements:
                        logger.info(i[1:])
                time_step += 1

                if len(elements) == 0:
                    if monitor:
                        logger.info(
                            f"----------There is no element in this page. Do you want to terminate or continue after"
                            f"human intervention? [i/e].\ni(Intervene): Reject this action, and pause for human "
                            f"intervention.\ne(Exit): Terminate the program and save results.")
                        monitor_input = await ainput()
                        logger.info("Monitor Command: " + monitor_input)
                        if monitor_input in ["i", "intervene", 'intervention']:
                            logger.info(
                                "Pause for human intervention. Press Enter to continue. You can also enter your message here, which will be included in the action history as a human message.")
                            human_intervention = await ainput()
                            if human_intervention:
                                human_intervention = f"Human intervention with a message: {human_intervention}"
                            else:
                                human_intervention = f"Human intervention"
                            taken_actions.append(human_intervention)
                            continue

                    logger.info("Terminate because there is no element in this page.")
                    logger.info("Action History:")
                    for action in taken_actions:
                        logger.info(action)
                    logger.info("")
                    if tracing:
                        logger.info("Save playwright trace file ")
                        await session_control.context.tracing.stop_chunk(
                            path=f"{os.path.join(main_result_path, 'playwright_traces', f'{time_step}.zip')}")

                    logger.info(f"Write results to json file: {os.path.join(main_result_path, 'result.json')}")
                    success_or_not = ""
                    if valid_op_count == 0:
                        success_or_not = "0"
                    final_json = {"confirmed_task": confirmed_task, "website": confirmed_website,
                                  "task_id": task_id, "success_or_not": success_or_not,
                                  "num_step": len(taken_actions), "action_history": taken_actions,
                                  "exit_by": "No elements"}

                    with open(os.path.join(main_result_path, 'result.json'), 'w', encoding='utf-8') as file:
                        json.dump(final_json, file, indent=4)
                    # logger.shutdown()
                    #
                    # if monitor:
                    #     logger.info("Wait for human inspection. Directly press Enter to exit")
                    #     monitor_input = await ainput()
                    logger.info("Close brownser context")
                    logger.removeHandler(log_fh)
                    logger.removeHandler(console_handler)

                    close_context = session_control.context
                    session_control.context = None
                    await close_context.close()
                    complete_flag = True
                    continue
                if ranker_path and len(elements) > top_k:
                    ranking_input = format_ranking_input(elements, confirmed_task, taken_actions)
                    logger.info("Start to rank")
                    pred_scores = ranking_model.predict(ranking_input, convert_to_numpy=True, show_progress_bar=False,
                                                        batch_size=100, )
                    topk_values, topk_indices = find_topk(pred_scores, k=min(top_k, len(elements)))
                    all_candidate_ids = list(topk_indices)
                    ranked_elements = [elements[i] for i in all_candidate_ids]
                else:

                    all_candidate_ids = range(len(elements))
                    ranked_elements = elements

                all_candidate_ids_with_location = []
                for element_id, element_detail in zip(all_candidate_ids, ranked_elements):
                    all_candidate_ids_with_location.append(
                        (element_id, round(element_detail[0][1]), round(element_detail[0][0])))

                all_candidate_ids_with_location.sort(key=lambda x: (x[1], x[2]))

                all_candidate_ids = [element_id[0] for element_id in all_candidate_ids_with_location]
                num_choices = len(all_candidate_ids)
                if ranker_path:
                    logger.info(f"# element candidates: {num_choices}")

                total_height = await session_control.active_page.evaluate('''() => {
                                                                return Math.max(
                                                                    document.documentElement.scrollHeight, 
                                                                    document.body.scrollHeight,
                                                                    document.documentElement.clientHeight
                                                                );
                                                            }''')
                if dynamic_choice_batch_size > 0:
                    step_length = min(num_choices,
                                      num_choices // max(round(total_height / dynamic_choice_batch_size), 1) + 1)
                else:
                    step_length = min(num_choices, fixed_choice_batch_size)
                logger.info(f"batch size: {step_length}")
                logger.info('-' * 10)

                total_width = session_control.active_page.viewport_size["width"]
                log_task = "You are asked to complete the following task: " + confirmed_task
                logger.info(log_task)
                previous_actions = taken_actions

                previous_action_text = "Previous Actions:\n"
                if previous_actions is None or previous_actions == []:
                    previous_actions = ["None"]
                for action_text in previous_actions:
                    previous_action_text += action_text
                    previous_action_text += "\n"

                log_previous_actions = previous_action_text
                logger.info(log_previous_actions[:-1])

                target_element = []

                new_action = ""
                target_action = "CLICK"
                target_value = ""
                query_count = 0
                got_one_answer = False

                for multichoice_i in range(0, num_choices, step_length):
                    logger.info("-" * 10)
                    logger.info(f"Start Multi-Choice QA - Batch {multichoice_i // step_length}")
                    input_image_path = os.path.join(main_result_path, 'image_inputs',
                                                    f'{time_step}_{multichoice_i // step_length}_crop.jpg')

                    height_start = all_candidate_ids_with_location[multichoice_i][1]
                    height_end = all_candidate_ids_with_location[min(multichoice_i + step_length, num_choices) - 1][1]

                    total_height = await session_control.active_page.evaluate('''() => {
                                                                    return Math.max(
                                                                        document.documentElement.scrollHeight, 
                                                                        document.body.scrollHeight,
                                                                        document.documentElement.clientHeight
                                                                    );
                                                                }''')
                    clip_start = min(total_height - 1144, max(0, height_start - 200))
                    clip_height = min(total_height - clip_start, max(height_end - height_start + 200, 1144))
                    clip = {"x": 0, "y": clip_start, "width": total_width, "height": clip_height}

                    if dev_mode:
                        logger.info(height_start)
                        logger.info(height_end)
                        logger.info(total_height)
                        logger.info(clip)

                    try:
                        await session_control.active_page.screenshot(path=input_image_path, clip=clip, full_page=True,
                                                                     type='jpeg', quality=100, timeout=20000)
                    except Exception as e_clip:
                        logger.info(f"Failed to get cropped screenshot because {e_clip}")

                    if dev_mode:
                        logger.info(multichoice_i)
                    if not os.path.exists(input_image_path):
                        if dev_mode:
                            logger.info("No screenshot")
                        continue
                    candidate_ids = all_candidate_ids[multichoice_i:multichoice_i + step_length]
                    choices = format_choices(elements, candidate_ids, confirmed_task, taken_actions)
                    query_count += 1
                    # Format prompts for LLM inference
                    prompt = generate_prompt(task=confirmed_task, previous=taken_actions, choices=choices,
                                             experiment_split="SeeAct")
                    if dev_mode:
                        for prompt_i in prompt:
                            logger.info(prompt_i)

                    output0 = generation_model.generate(prompt=prompt, image_path=input_image_path, turn_number=0)

                    terminal_width = 10
                    logger.info("-" * terminal_width)
                    logger.info("🤖Action Generation Output🤖")

                    # logger.info(output0)

                    for line in output0.split('\n'):
                        logger.info(line)

                    terminal_width = 10
                    logger.info("-" * (terminal_width))

                    choice_text = f"(Multichoice Question) - Batch {multichoice_i // step_length}" + "\n" + format_options(
                        choices)
                    choice_text = choice_text.replace("\n\n", "")

                    for line in choice_text.split('\n'):
                        logger.info(line)
                    # logger.info(choice_text)

                    output = generation_model.generate(prompt=prompt, image_path=input_image_path, turn_number=1,
                                                       ouput__0=output0)

                    terminal_width = 10
                    logger.info("-" * terminal_width)
                    logger.info("🤖Grounding Output🤖")

                    for line in output.split('\n'):
                        logger.info(line)
                    # logger.info(output)
                    pred_element, pred_action, pred_value = postprocess_action_lmm(output)
                    if len(pred_element) in [1, 2]:
                        element_id = get_index_from_option_name(pred_element)
                    else:
                        element_id = -1

                    # Process the elements
                    if (0 <= element_id < len(candidate_ids) and pred_action.strip() in ["CLICK", "SELECT", "TYPE",
                                                                                         "PRESS ENTER", "HOVER",
                                                                                         "TERMINATE"]):
                        target_element = elements[int(choices[element_id][0])]
                        target_element_text = choices[element_id][1]
                        target_action = pred_action
                        target_value = pred_value
                        new_action += "[" + target_element[2] + "]" + " "
                        new_action += target_element[1] + " -> " + target_action
                        if target_action.strip() in ["SELECT", "TYPE"]:
                            new_action += ": " + target_value
                        got_one_answer = True
                        break
                    elif pred_action.strip() in ["PRESS ENTER", "TERMINATE"]:
                        target_element = pred_action
                        target_element_text = target_element
                        target_action = pred_action
                        target_value = pred_value
                        new_action += target_action
                        if target_action.strip() in ["SELECT", "TYPE"]:
                            new_action += ": " + target_value
                        got_one_answer = True
                        break
                    else:
                        pass

                if got_one_answer:
                    terminal_width = 10
                    logger.info("-" * terminal_width)
                    logger.info("🤖Browser Operation🤖")
                    logger.info(f"Target Element: {target_element_text}", )
                    logger.info(f"Target Action: {target_action}", )
                    logger.info(f"Target Value: {target_value}", )

                    if monitor:
                        logger.info(
                            f"----------\nShould I execute the above action? [Y/n/i/e].\nY/n: Accept or reject this action.\ni(Intervene): Reject this action, and pause for human intervention.\ne(Exit): Terminate the program and save results.")
                        monitor_input = await ainput()
                        logger.info("Monitor Command: " + monitor_input)
                        if monitor_input in ["n", "N", "No", "no"]:
                            monitor_signal = "reject"
                            target_element = []
                        elif monitor_input in ["e", "exit", "Exit"]:
                            monitor_signal = "exit"
                        elif monitor_input in ["i", "intervene", 'intervention']:
                            monitor_signal = "pause"
                            target_element = []
                        else:
                            valid_op_count += 1
                else:
                    no_op_count += 1
                    target_element = []

                try:
                    if monitor_signal == 'exit':
                        raise Exception("human supervisor manually made it exit.")
                    if no_op_count >= max_continuous_no_op:
                        raise Exception(f"no executable operations for {max_continuous_no_op} times.")
                    elif time_step >= max_op:
                        raise Exception(f"the agent reached the step limit {max_op}.")
                    elif target_action == "TERMINATE":
                        raise Exception("The model determined a completion.")

                    # Perform browser action with PlayWright
                    # The code is complex to handle all kinds of cases in execution
                    # It's ugly, but it works, so far
                    selector = None
                    fail_to_execute = False
                    try:
                        if target_element == []:
                            pass
                        else:
                            if not target_element in ["PRESS ENTER", "TERMINATE"]:
                                selector = target_element[-2]
                                if dev_mode:
                                    logger.info(target_element)
                                try:
                                    await selector.scroll_into_view_if_needed(timeout=3000)
                                    if highlight:
                                        await selector.highlight()
                                        await asyncio.sleep(2.5)
                                except Exception as e:
                                    pass

                        if selector:
                            valid_op_count += 1
                            if target_action == "CLICK":
                                js_click = True
                                try:
                                    if target_element[-1] in ["select", "input"]:
                                        logger.info("Try performing a CLICK")
                                        await selector.evaluate("element => element.click()", timeout=10000)
                                        js_click = False
                                    else:
                                        await selector.click(timeout=10000)
                                except Exception as e:
                                    try:
                                        if not js_click:
                                            logger.info("Try performing a CLICK")
                                            await selector.evaluate("element => element.click()", timeout=10000)
                                        else:
                                            raise Exception(e)
                                    except Exception as ee:
                                        try:
                                            logger.info("Try performing a HOVER")
                                            await selector.hover(timeout=10000)
                                            new_action = new_action.replace("CLICK",
                                                                            f"Failed to CLICK because {e}, did a HOVER instead")
                                        except Exception as eee:
                                            new_action = new_action.replace("CLICK", f"Failed to CLICK because {e}")
                                            no_op_count += 1
                            elif target_action == "TYPE":
                                try:
                                    try:
                                        logger.info("Try performing a \"press_sequentially\"")
                                        await selector.clear(timeout=10000)
                                        await selector.fill("", timeout=10000)
                                        await selector.press_sequentially(target_value, timeout=10000)
                                    except Exception as e0:
                                        await selector.fill(target_value, timeout=10000)
                                except Exception as e:
                                    try:
                                        if target_element[-1] in ["select"]:
                                            logger.info("Try performing a SELECT")
                                            selected_value = await select_option(selector, target_value)
                                            new_action = new_action.replace("TYPE",
                                                                            f"Failed to TYPE \"{target_value}\" because {e}, did a SELECT {selected_value} instead")
                                        else:
                                            raise Exception(e)
                                    except Exception as ee:
                                        js_click = True
                                        try:
                                            if target_element[-1] in ["select", "input"]:
                                                logger.info("Try performing a CLICK")
                                                await selector.evaluate("element => element.click()", timeout=10000)
                                                js_click = False
                                            else:
                                                logger.info("Try performing a CLICK")
                                                await selector.click(timeout=10000)
                                            new_action = "[" + target_element[2] + "]" + " "
                                            new_action += target_element[
                                                              1] + " -> " + f"Failed to TYPE \"{target_value}\" because {e}, did a CLICK instead"
                                        except Exception as eee:
                                            try:
                                                if not js_click:
                                                    if dev_mode:
                                                        logger.info(eee)
                                                    logger.info("Try performing a CLICK")
                                                    await selector.evaluate("element => element.click()", timeout=10000)
                                                    new_action = "[" + target_element[2] + "]" + " "
                                                    new_action += target_element[
                                                                      1] + " -> " + f"Failed to TYPE \"{target_value}\" because {e}, did a CLICK instead"
                                                else:
                                                    raise Exception(eee)
                                            except Exception as eeee:
                                                try:
                                                    logger.info("Try performing a HOVER")
                                                    await selector.hover(timeout=10000)
                                                    new_action = "[" + target_element[2] + "]" + " "
                                                    new_action += target_element[
                                                                      1] + " -> " + f"Failed to TYPE \"{target_value}\" because {e}, did a HOVER instead"
                                                except Exception as eee:
                                                    new_action = "[" + target_element[2] + "]" + " "
                                                    new_action += target_element[
                                                                      1] + " -> " + f"Failed to TYPE \"{target_value}\" because {e}"
                                                    no_op_count += 1
                            elif target_action == "SELECT":
                                try:
                                    logger.info("Try performing a SELECT")
                                    selected_value = await select_option(selector, target_value)
                                    new_action = new_action.replace(f"{target_value}", f"{selected_value}")
                                except Exception as e:
                                    try:
                                        if target_element[-1] in ["input"]:
                                            try:
                                                logger.info("Try performing a \"press_sequentially\"")
                                                await selector.clear(timeout=10000)
                                                await selector.fill("", timeout=10000)
                                                await selector.press_sequentially(target_value, timeout=10000)
                                            except Exception as e0:
                                                await selector.fill(target_value, timeout=10000)
                                            new_action = new_action.replace("SELECT",
                                                                            f"Failed to SELECT \"{target_value}\" because {e}, did a TYPE instead")
                                        else:
                                            raise Exception(e)
                                    except Exception as ee:
                                        js_click = True
                                        try:
                                            if target_element[-1] in ["select", "input"]:
                                                logger.info("Try performing a CLICK")
                                                await selector.evaluate("element => element.click()", timeout=10000)
                                                js_click = False
                                            else:
                                                await selector.click(timeout=10000)
                                            new_action = "[" + target_element[2] + "]" + " "
                                            new_action += target_element[
                                                              1] + " -> " + f"Failed to SELECT \"{target_value}\" because {e}, did a CLICK instead"
                                        except Exception as eee:

                                            try:
                                                if not js_click:
                                                    logger.info("Try performing a CLICK")
                                                    await selector.evaluate("element => element.click()", timeout=10000)
                                                    new_action = "[" + target_element[2] + "]" + " "
                                                    new_action += target_element[
                                                                      1] + " -> " + f"Failed to SELECT \"{target_value}\" because {e}, did a CLICK instead"
                                                else:
                                                    raise Exception(eee)
                                            except Exception as eeee:
                                                try:
                                                    logger.info("Try performing a HOVER")
                                                    await selector.hover(timeout=10000)
                                                    new_action = "[" + target_element[2] + "]" + " "
                                                    new_action += target_element[
                                                                      1] + " -> " + f"Failed to SELECT \"{target_value}\" because {e}, did a HOVER instead"
                                                except Exception as eee:
                                                    new_action = "[" + target_element[2] + "]" + " "
                                                    new_action += target_element[
                                                                      1] + " -> " + f"Failed to SELECT \"{target_value}\" because {e}"
                                                    no_op_count += 1
                            elif target_action == "HOVER":
                                try:
                                    logger.info("Try performing a HOVER")
                                    await selector.hover(timeout=10000)
                                except Exception as e:
                                    try:
                                        await selector.click(timeout=10000)
                                        new_action = new_action.replace("HOVER",
                                                                        f"Failed to HOVER because {e}, did a CLICK instead")
                                    except:
                                        js_click = True
                                        try:
                                            if target_element[-1] in ["select", "input"]:
                                                logger.info("Try performing a CLICK")
                                                await selector.evaluate("element => element.click()", timeout=10000)
                                                js_click = False
                                            else:
                                                await selector.click(timeout=10000)
                                            new_action = "[" + target_element[2] + "]" + " "
                                            new_action += target_element[
                                                              1] + " -> " + f"Failed to HOVER because {e}, did a CLICK instead"
                                        except Exception as eee:
                                            try:
                                                if not js_click:
                                                    logger.info("Try performing a CLICK")
                                                    await selector.evaluate("element => element.click()", timeout=10000)
                                                    new_action = "[" + target_element[2] + "]" + " "
                                                    new_action += target_element[
                                                                      1] + " -> " + f"Failed to HOVER because {e}, did a CLICK instead"
                                                else:
                                                    raise Exception(eee)
                                            except Exception as eeee:
                                                new_action = "[" + target_element[2] + "]" + " "
                                                new_action += target_element[
                                                                  1] + " -> " + f"Failed to HOVER because {e}"
                                                no_op_count += 1
                            elif target_action == "PRESS ENTER":
                                try:
                                    logger.info("Try performing a PRESS ENTER")
                                    await selector.press('Enter')
                                except Exception as e:
                                    await selector.click(timeout=10000)
                                    await session_control.active_page.keyboard.press('Enter')
                        elif monitor_signal == "pause":
                            logger.info(
                                "Pause for human intervention. Press Enter to continue. You can also enter your message here, which will be included in the action history as a human message.")
                            human_intervention = await ainput()
                            if human_intervention:
                                human_intervention = f" Human message: {human_intervention}"
                            raise Exception(
                                f"the human supervisor rejected this operation and may have taken some actions.{human_intervention}")
                        elif monitor_signal == "reject":
                            raise Exception("the human supervisor rejected this operation.")
                        elif target_element == "PRESS ENTER":
                            logger.info("Try performing a PRESS ENTER")
                            await session_control.active_page.keyboard.press('Enter')
                        no_op_count = 0
                        try:
                            await session_control.active_page.wait_for_load_state('load')
                        except Exception as e:
                            pass
                    except Exception as e:
                        if target_action not in ["TYPE", "SELECT"]:
                            new_action = f"Failed to {target_action} {target_element_text} because {e}"

                        else:
                            new_action = f"Failed to {target_action} {target_value} for {target_element_text} because {e}"
                        fail_to_execute = True

                    if new_action == "" or fail_to_execute:
                        if new_action == "":
                            new_action = "No Operation"
                        if monitor_signal not in ["pause", "reject"]:
                            no_op_count += 1
                    taken_actions.append(new_action)
                    if not session_control.context.pages:
                        await session_control.context.new_page()
                        try:
                            await session_control.active_page.goto(confirmed_website_url, wait_until="load")
                        except Exception as e:
                            pass

                    if monitor_signal == 'pause':
                        pass
                    else:
                        await asyncio.sleep(3)
                    if dev_mode:
                        logger.info(f"current active page: {session_control.active_page}")

                        # await session_control.context.new_page()
                        # try:
                        #     await session_control.active_page.goto("https://www.bilibili.com/", wait_until="load")
                        # except Exception as e:
                        #     pass
                        logger.info("All pages")
                        logger.info(session_control.context.pages)
                        logger.info("-" * 10)
                    try:
                        await session_control.active_page.wait_for_load_state('load')
                    except Exception as e:
                        if dev_mode:
                            logger.info(e)
                    if tracing:
                        logger.info("Save playwright trace file")
                        await session_control.context.tracing.stop_chunk(
                            path=f"{os.path.join(main_result_path, 'playwright_traces', f'{time_step}.zip')}")
                except Exception as e:
                    logger.info("=" * 10)
                    logger.info(f"Decide to terminate because {e}")
                    logger.info("Action History:")

                    for action in taken_actions:
                        logger.info(action)
                    logger.info("")

                    if tracing:
                        logger.info("Save playwright trace file")
                        await session_control.context.tracing.stop_chunk(
                            path=f"{os.path.join(main_result_path, 'playwright_traces', f'{time_step}.zip')}")

                    success_or_not = ""
                    if valid_op_count == 0:
                        success_or_not = "0"
                    logger.info(f"Write results to json file: {os.path.join(main_result_path, 'result.json')}")
                    final_json = {"confirmed_task": confirmed_task, "website": confirmed_website,
                                  "task_id": task_id, "success_or_not": success_or_not,
                                  "num_step": len(taken_actions), "action_history": taken_actions, "exit_by": str(e)}

                    with open(os.path.join(main_result_path, 'result.json'), 'w', encoding='utf-8') as file:
                        json.dump(final_json, file, indent=4)

                    if monitor:
                        logger.info("Wait for human inspection. Directly press Enter to exit")
                        monitor_input = await ainput()

                    logger.info("Close brownser context")
                    logger.removeHandler(log_fh)
                    logger.removeHandler(console_handler)
                    close_context = session_control.context
                    session_control.context = None
                    await close_context.close()

                    complete_flag = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config_path", help="Path to the TOML configuration file.", type=str, metavar='config',
                        default=f"{os.path.join('config', 'demo_mode.toml')}")
    args = parser.parse_args()

    # Load configuration file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config = None
    try:
        with open(os.path.join(base_dir, args.config_path) if not os.path.isabs(args.config_path) else args.config_path,
                  'r') as toml_config_file:
            config = toml.load(toml_config_file)
            print(f"Configuration File Loaded - {os.path.join(base_dir, args.config_path)}")
    except FileNotFoundError:
        print(f"Error: File '{args.config_path}' not found.")
    except toml.TomlDecodeError:
        print(f"Error: File '{args.config_path}' is not a valid TOML file.")

    asyncio.run(main(config, base_dir))

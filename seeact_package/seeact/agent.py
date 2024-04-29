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

import logging
import os
import traceback
from datetime import datetime
import json
import toml
from playwright.async_api import async_playwright,Locator

from .data_utils.format_prompt_utils import get_index_from_option_name, generate_new_query_prompt, \
    generate_new_referring_prompt, format_options
from .demo_utils.browser_helper import normal_launch_async, normal_new_context_async, \
    get_interactive_elements_with_playwright, select_option, saveconfig
from .demo_utils.format_prompt import format_choices, postprocess_action_lmm
from .demo_utils.inference_engine import OpenAIEngine, load_openai_api_key


class SeeActAgent:
    def __init__(self,
                 config_path=None,
                 openai_key=None,
                 save_file_dir="seeact_agent_files",
                 default_task='Find the pdf of the paper "GPT-4V(ision) is a Generalist Web Agent, if Grounded"',
                 default_website="https://www.google.com/",
                 input_info=["screenshot"],
                 grounding_strategy="text_choice",
                 max_auto_op=50,
                 max_continuous_no_op=5,
                 highlight=False,
                 headless=False,
                 args=[],
                 browser_app="chrome",
                 persistant=False,
                 persistant_user_path="",
                 save_video=False,
                 viewport={
                     "width": 1280,
                     "height": 720
                 },
                 tracing=False,
                 trace={
                     "screenshots": True,
                     "snapshots": True,
                     "sources": True
                 },
                 rate_limit=-1,
                 model="gpt-4-turbo",
                 temperature=0.9

                 ):

        try:
            if config_path is not None:
                with open(config_path,
                          'r') as config:
                    print(f"Configuration File Loaded - {config_path}")
            else:
                config = {
                    "basic": {
                        "save_file_dir": save_file_dir,
                        "default_task": default_task,
                        "default_website": default_website
                    },
                    "agent": {
                        "input_info": input_info,
                        "grounding_strategy": grounding_strategy,
                        "max_auto_op": max_auto_op,
                        "max_continuous_no_op": max_continuous_no_op,
                        "highlight": highlight
                    },
                    "browser": {
                        "headless": headless,
                        "args": args,
                        "browser_app": browser_app,
                        "persistant": persistant,
                        "persistant_user_path": persistant_user_path,
                        "save_video": save_video,
                        "viewport": viewport,
                        "tracing": tracing,
                        "trace": trace
                    },
                    "openai": {
                        "api_key": load_openai_api_key() if not openai_key else openai_key,
                        "rate_limit": rate_limit,
                        "model": model,
                        "temperature": temperature
                    }
                }

        except FileNotFoundError:
            print(f"Error: File '{os.path.abspath(config_path)}' not found.")
        except toml.TomlDecodeError:
            print(f"Error: File '{os.path.abspath(config_path)}' is not a valid TOML file.")

        self.config = config
        self.complete_flag = False
        self.session_control = {
            'active_page': None,
            'context': None,
            'browser': None
        }
        if openai_key is not None:
            pass
        self.tasks = [self.config["basic"]["default_task"]]

        self.main_path = os.path.join(self.config["basic"]["save_file_dir"], datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.main_path, exist_ok=True)
        self.action_space = ["CLICK", "PRESS ENTER", "HOVER", "SCROLL UP", "SCROLL DOWN", "NEW TAB", "CLOSE TAB",
                             "GO BACK", "GO FORWARD",
                             "TERMINATE", "SELECT", "TYPE", "GOTO", "MEMORIZE"]  # Define the list of actions here

        self.no_value_op = ["CLICK", "PRESS ENTER", "HOVER", "SCROLL UP", "SCROLL DOWN", "NEW TAB", "CLOSE TAB",
                            "PRESS HOME", "PRESS END", "PRESS PAGEUP", "PRESS PAGEDOWN"
                                                                       "GO BACK",
                            "GO FORWARD",
                            "TERMINATE", "NONE"]

        self.with_value_op = ["SELECT", "TYPE", "GOTO", "MEMORIZE", "SAY"]

        self.no_element_op = ["PRESS ENTER", "SCROLL UP", "SCROLL DOWN", "NEW TAB", "CLOSE TAB", "GO BACK", "GOTO",
                              "PRESS HOME", "PRESS END", "PRESS PAGEUP", "PRESS PAGEDOWN",
                              "GO FORWARD",
                              "TERMINATE", "NONE", "MEMORIZE", "SAY"]

        # Initialize the primary logger and the developer logger
        self.logger = self._setup_logger(redirect_to_dev_log=False)
        # self.dev_logger = self._setup_dev_logger()

        # # Redirect primary logger messages to dev_logger as well
        # for handler in self.logger.handlers:
        #     self.dev_logger.addHandler(handler)

        self.openai_engine = OpenAIEngine(**self.config['openai'])
        self.taken_actions = []
        self.prompts = self._initialize_prompts()
        self.time_step = 0
        self.valid_op = 0
        # self.error=0
        self.continuous_no_op = 0
        self.predictions=[]

    def _initialize_prompts(self):
        """Initialize prompt information including dynamic action space."""
        action_format = f"ACTION: Choose an action from allowed actions."  # Dynamically generate action_format based on self.action_space

        return {
            "system_prompt": '''You are assisting humans doing web navigation tasks step by step. At each stage, you can see the webpage by a screenshot and know the previous actions before the current step decided by yourself that have been executed for this task through recorded history. You need to decide on the first following action to take.''',

            "action_space": '''
Here are the descriptions of all allowed actions:

No Value Operations:
- CLICK: Click on a webpage element using the mouse.
- HOVER: Move the mouse over a webpage element without clicking.
- PRESS ENTER: Press the Enter key, typically to submit a form or confirm an input.
- SCROLL UP: Scroll the webpage upwards by half of the window height.
- SCROLL DOWN: Scroll the webpage downwards by half of the window height.
- PRESS HOME: Scroll to the top of the webpage.
- PRESS END: Scroll to the bottom of the webpage.
- PRESS PAGEUP: Scroll up by one window height.
- PRESS PAGEDOWN: Scroll down by one window height.
- CLOSE TAB: Close the current tab in the browser.
- NEW TAB: Open a new tab in the browser.
- GO BACK: Navigate to the previous page in the browser history.
- GO FORWARD: Navigate to the next page in the browser history.
- TERMINATE: End the current task, typically used when the task is considered complete or requires potentially harmful actions.
- NONE: Indicates that no action is necessary at this stage. Used to skip an action or wait.

With Value Operations:
- SELECT: Choose an option from a dropdown menu or <select> element. The value indicates the option to select.
- TYPE: Enter text into a text area or text box. The value is the text to be typed.
- GOTO: Navigate to a specific URL. The value is the URL to navigate to.
- SAY: Output answers or other information you want to tell the user.
- MEMORIZE: Keep some content into action history to memorize it.
''',

            "question_description": '''The screenshot below shows the webpage you see. Think step by step before outlining the next action step at the current stage. Clearly outline which element in the webpage users will operate with as the first next target element, its detailed location, and the corresponding operation.

To be successful, it is important to follow the following rules: 
1. You should only issue a valid action given the current observation. 
2. You should only issue one action at a time
3. For handling the select dropdown elements on the webpage, it's not necessary for you to provide completely accurate options right now. The full list of options for these elements will be supplied later.
4. Unlike humans, for typing (e.g., in text areas, text boxes) and selecting (e.g., from dropdown menus or <select> elements), you should try directly typing the input or selecting the choice, bypassing the need for an initial click. 
5. You should not attempt to create accounts, log in or do the final submission. 
6. Terminate when you deem the task complete or if it requires potentially harmful actions.''',

            "referring_description": f"""(Reiteration)
First, reiterate your next target element, its detailed location, and the corresponding operation.

(Multichoice Question)
Below is a multi-choice question, where the choices are elements in the webpage. All elements are arranged in the order based on their height on the webpage, from top to bottom (and from left to right). This arrangement in addition to the normalized coordinates can be used to locate them. From the screenshot, find out where and what each one is on the webpage, taking into account both their text content and HTML details. Then, determine whether one matches your target element if your action involves an element. Please examine the choices one by one. Choose the matching one. If multiple options match your answer, choose the most likely one by re-examining the screenshot, the choices, and your further reasoning.""",

            "element_format": '''(Final Answer)
Finally, conclude your answer using the format below. Ensure your answer is strictly adhering to the format provided below. Please do not leave any explanation in your answers of the final standardized format part, and this final part should be clear and certain. The element choice, action, and value should be in three separate lines.

Format:

ELEMENT: The uppercase letter of your choice.''',

            "action_format": action_format,  # Use the dynamically generated action_format

            "value_format": '''VALUE: Provide additional input based on ACTION. (If it doesn't involve a value, write "None"'''
        }

    def update_action_space(self, new_actions):
        """Update the action space and regenerate the action_format prompt."""
        if isinstance(new_actions, list) and all(isinstance(item, str) for item in new_actions):
            self.action_space = new_actions
            self.prompts["action_format"] = f"ACTION: Choose an action from {{{', '.join(self.action_space)}}}."
        else:
            print("Invalid action space provided. It must be a list of strings.")

    def _setup_logger(self, redirect_to_dev_log=False):
        """Set up a logger to log to both file and console within the main_path."""
        logger_name = 'SeeActAgent'
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:  # Avoid adding handlers multiple times
            # Create a file handler for writing logs to a file
            log_filename = 'agent.log'
            f_handler = logging.FileHandler(os.path.join(self.main_path, log_filename))
            f_handler.setLevel(logging.INFO)

            # Create a console handler for printing logs to the terminal
            c_handler = logging.StreamHandler()
            c_handler.setLevel(logging.INFO)

            # Create formatters for file and console handlers
            file_formatter = logging.Formatter('%(asctime)s - %(message)s')
            console_formatter = logging.Formatter('%(message)s')

            # Set formatters for file and console handlers
            f_handler.setFormatter(file_formatter)
            c_handler.setFormatter(console_formatter)

            # Add the handlers to the logger
            logger.addHandler(f_handler)
            if not redirect_to_dev_log:  # Only add console handler if not redirecting to dev log
                logger.addHandler(c_handler)

        return logger

    # def _setup_dev_logger(self):
    #     """Set up a developer logger to log only to a file within the main_path."""
    #     dev_logger_name = 'SeeActAgentDev'
    #     dev_logger = logging.getLogger(dev_logger_name)
    #     dev_logger.setLevel(logging.INFO)
    #     if not dev_logger.handlers:  # Avoid adding handlers multiple times
    #         # Create a file handler for writing logs to a dev log file
    #         dev_log_filename = 'dev_agent.log'
    #         f_handler = logging.FileHandler(os.path.join(self.main_path, dev_log_filename))
    #         f_handler.setLevel(logging.INFO)
    #
    #         # Create a formatter and add it to the handler
    #         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #         f_handler.setFormatter(formatter)
    #
    #         # Add the file handler to the dev logger
    #         dev_logger.addHandler(f_handler)
    #
    #     return dev_logger

    async def page_on_close_handler(self):
        # Corrected to use 'self' for accessing class attributes
        if self.session_control['context']:
            try:
                await self.session_control['active_page'].title()
            except:
                self.logger.info(
                    "The active tab was closed. Will switch to the last page (or open a new default google page)")
                if self.session_control['context'].pages:
                    self.session_control['active_page'] = self.session_control['context'].pages[-1]
                    await self.session_control['active_page'].bring_to_front()
                    self.logger.info(f"Switched the active tab to: {self.session_control['active_page'].url}")
                else:
                    self.session_control['active_page'] = await self.session_control['context'].new_page()
                    try:
                        await self.session_control['active_page'].goto("https://www.google.com/", wait_until="load")
                    except Exception as e:
                        self.logger.info(f"Failed to navigate to Google: {e}")
                    self.logger.info(f"Switched the active tab to: {self.session_control['active_page'].url}")

    def save_action_history(self, filename="action_history.txt"):
        """Save the history of taken actions to a file in the main path."""
        history_path = os.path.join(self.main_path, filename)
        with open(history_path, 'w') as f:
            for action in self.taken_actions:
                f.write(action + '\n')
        self.logger.info(f"Action history saved to: {history_path}")

    async def page_on_navigation_handler(self, frame):
        # Corrected to use 'self' for accessing class attributes
        self.session_control['active_page'] = frame.page

    async def page_on_crash_handler(self, page):
        # Corrected logging method
        self.logger.info(f"Page crashed: {page.url}")
        self.logger.info("Try to reload")
        await page.reload()

    async def page_on_open_handler(self, page):
        # Added 'self' to the handler functions to reference the current instance of the class
        page.on("framenavigated", self.page_on_navigation_handler)
        page.on("close", self.page_on_close_handler)
        page.on("crash", self.page_on_crash_handler)
        self.session_control['active_page'] = page
        # Additional event listeners can be added here

    async def start(self, headless=None, args=None, website=None):
        self.playwright = await async_playwright().start()
        self.session_control['browser'] = await normal_launch_async(self.playwright,
                                                                    headless=self.config['browser'][
                                                                        'headless'] if headless is None else headless,
                                                                    args=self.config['browser'][
                                                                        'args'] if args is None else args)
        self.session_control['context'] = await normal_new_context_async(self.session_control['browser'],
                                                                         viewport=self.config['browser'][
                                                                             'viewport'])

        self.session_control['context'].on("page", self.page_on_open_handler)
        await self.session_control['context'].new_page()

        try:
            await self.session_control['active_page'].goto(
                self.config['basic']['default_website'] if website is None else website,
                wait_until="load")
            self.logger.info(f"Loaded website: {self.config['basic']['default_website']}")
        except Exception as e:
            self.logger.info("Failed to fully load the webpage before timeout")
            self.logger.info(e)

            # await asyncio.sleep(2)

    def update_prompt_part(self, part_name, new_text):
        """Update the specified part of the prompt information."""
        if part_name in self.prompts:
            self.prompts[part_name] = new_text
            return True
        else:
            print(f"Prompt part '{part_name}' not found.")
            return False

    def generate_prompt(self, task=None, previous=None, choices=None):

        """Generate a prompt based on the current task, previous actions, and choices."""
        # assert task is not None, "Please input the task."

        prompt_list = []

        system_prompt_input = self.prompts["system_prompt"]
        action_space_input = self.prompts["action_space"]
        question_description_input = self.prompts["question_description"]
        referring_input = self.prompts["referring_description"]
        element_format_input = self.prompts["element_format"]
        action_format_input = self.prompts["action_format"]
        value_format_input = self.prompts["value_format"]

        # print(previous)

        previous_ = self.taken_actions if self.taken_actions else None

        # print(previous_)

        prompt_list.extend(
            generate_new_query_prompt(system_prompt=system_prompt_input + "\n" + action_space_input,
                                      task=self.tasks[-1], previous_actions=previous_,
                                      question_description=question_description_input))
        prompt_list.append(
            generate_new_referring_prompt(referring_description=referring_input, element_format=element_format_input,
                                          action_format=action_format_input, value_format=value_format_input,
                                          choices=choices))

        return prompt_list

    async def perform_action(self, target_element=None, action_name=None, value=None, element_repr=""):
        if target_element is not None:
            selector = target_element['selector']
            element_repr =target_element['description']
        else:
            selector = None

        page = self.session_control['active_page']



        if action_name == "CLICK" and selector:
            await selector.click(timeout=2000)
            self.logger.info(f"Clicked on element: {element_repr}")
        elif action_name == "HOVER" and selector:
            await selector.hover(timeout=2000)
            self.logger.info(f"Hovered over element: {element_repr}")
        elif action_name == "TYPE" and selector:
            await selector.fill(value)
            await selector.fill(value)
            self.logger.info(f"Typed '{value}' into element: {element_repr}")
        elif action_name == "SCROLL UP":
            await page.evaluate(f"window.scrollBy(0, -{self.config['browser']['viewport']['height'] // 2});")
            self.logger.info("Scrolled up")
        elif action_name == "SCROLL DOWN":
            await page.evaluate(f"window.scrollBy(0, {self.config['browser']['viewport']['height'] // 2});")
            self.logger.info("Scrolled down")
        elif action_name == "PRESS HOME":
            await page.keyboard.press('Home')
            self.logger.info("Pressed Home key")
        elif action_name == "PRESS END":
            await page.keyboard.press('End')
            self.logger.info("Pressed End key")
        elif action_name == "PRESS PAGEUP":
            await page.keyboard.press('PageUp')
            self.logger.info("Pressed PageUp key")
        elif action_name == "PRESS PAGEDOWN":
            await page.keyboard.press('PageDown')
            self.logger.info("Pressed PageDown key")
        elif action_name == "NEW TAB":
            new_page = await self.session_control['context'].new_page()
            # self.session_control['pages'].append(new_page)
            self.logger.info("Opened a new tab")
        elif action_name == "CLOSE TAB":
            await page.close()
            self.logger.info("Closed the current tab")
        elif action_name == "GO BACK":
            await page.go_back()
            self.logger.info("Navigated back")
        elif action_name == "GO FORWARD":
            await page.go_forward()
            self.logger.info("Navigated forward")
        elif action_name == "GOTO" and value:
            await page.goto(value, wait_until="load")
            self.logger.info(f"Navigated to {value}")
        elif action_name == "PRESS ENTER" and selector:
            await selector.press('Enter')
            self.logger.info(f"Pressed Enter on element: {element_repr}")
        elif action_name == "PRESS ENTER":
            await page.keyboard.press('Enter')
            self.logger.info(f"Pressed Enter on element: {element_repr}")
        elif action_name == "SELECT" and selector:
            await select_option(selector, value)
            self.logger.info(f"Selected option '{value}' from element: {element_repr}")
        elif action_name == "TERMINATE":
            self.complete_flag = True
            self.logger.info("Task has been marked as complete. Terminating...")
        elif action_name in ["NONE"]:
            self.logger.info("No action necessary at this stage. Skipped")
        elif action_name in ["SAY"]:
            self.logger.info(f"Say {value} to the user")
        elif action_name in ["MEMORIZE"]:
            self.logger.info(f"Keep {value} to the action history.")
        else:
            raise Exception(f"Unsupported or improperly specified action: {action_name}")
        if action_name in self.no_element_op and target_element is None:
            new_action = action_name
        else:
            new_action = "[" + target_element['tag_with_role'] + "]" + " "
            new_action += target_element['description'] + " -> " + action_name
        if action_name in self.with_value_op:
            new_action += ": " + value

        # self.dev_logger.info(new_action)
        return new_action

    async def predict(self):

        """
        Generate a prediction for the next action based on the webpage elements and previous actions.
        """

        self.time_step += 1

        try:
            await self.session_control["active_page"].wait_for_load_state('load')
        except Exception as e:
            pass

        elements = await get_interactive_elements_with_playwright(self.session_control['active_page'],
                                                                  self.config['browser']['viewport'])

        '''
             0: center_point =(x,y)
             1: description
             2: tag_with_role: tag_head with role and type # TODO: Consider adding more
             3. box
             4. selector
             5. tag
             '''

        elements = sorted(elements, key=lambda el: (
            el["center_point"][1], el["center_point"][0]))  # Sorting by y and then x coordinate

        # Generate choices for the prompt

        # , self.config['basic']['default_task'], self.taken_actions
        choices = format_choices(elements)

        # print("\n\n",choices)
        prompt = self.generate_prompt(task=self.tasks[-1], previous=self.taken_actions, choices=choices)
        # print("\n\n",prompt)

        # Logging prompt for debugging

        # Capture a screenshot for the current state of the webpage, if required by the model
        screenshot_path = os.path.join(self.main_path, 'screenshots', f'screen_{self.time_step}.png')
        try:
            await self.session_control['active_page'].screenshot(path=screenshot_path)
        except Exception as e:
            self.logger.info(f"Failed to take screenshot: {e}")

        terminal_width = 10
        self.logger.info(f"Step - {self.time_step}\n{'-'*terminal_width}\nAction Generation ➡️")
        # for prompt_part in prompt:
        self.logger.info("TASK: "+self.tasks[-1])
        self.logger.info("Previous:")
        for action in self.taken_actions:
            self.logger.info(action)

        output0 = self.openai_engine.generate(prompt=prompt, image_path=screenshot_path, turn_number=0)

        terminal_width = 10
        self.logger.info("-" * terminal_width)
        self.logger.info("🤖 Action Generation Output 🤖")

        for line in output0.split('\n'):
            self.logger.info(line)

        terminal_width = 10
        self.logger.info("-" * (terminal_width))

        choice_text = f"Action Grounding ➡️" + "\n" + format_options(
            choices)
        choice_text = choice_text.replace("\n\n", "")

        for line in choice_text.split('\n'):
            self.logger.info(line)

        output = self.openai_engine.generate(prompt=prompt, image_path=screenshot_path, turn_number=1,
                                             ouput_0=output0)
        self.logger.info("🤖 Action Grounding Output 🤖")
        for line in output.split('\n'):
            self.logger.info(line)

        pred_element_label, pred_action, pred_value = postprocess_action_lmm(output)

        if len(pred_element_label) in [1, 2]:
            element_id = get_index_from_option_name(pred_element_label)
        else:
            element_id = None
        if element_id is not None and element_id < len(elements):
            pred_element = elements[element_id]
        else:
            pred_element = None
        # Log the prediction result
        self.logger.debug(f"Retrieved Answer")
        self.logger.debug(f"Predicted Element: {pred_element}")
        self.logger.debug(f"Action: {pred_action}")
        self.logger.debug(f"Value: {pred_value}")

        prediction={"action_generation": output0, "action_grounding": output, "element": pred_element,
                "action": pred_action, "value": pred_value}

        self.predictions.append(prediction)

        return {"action_generation": output0, "action_grounding": output, "element": pred_element,
                "action": pred_action, "value": pred_value}

        # return output0,output,pred_element, pred_action, pred_value

    async def execute(self, prediction_dict):
        """
        Execute the predicted action on the webpage.
        """

        pred_element = prediction_dict["element"]
        pred_action = prediction_dict["action"]
        pred_value = prediction_dict["value"]
        try:
            if (pred_action not in self.no_element_op) and pred_element == None:
                # self.dev_logger.info
                self.logger.info("DEBUG: WHAT IS PRED ACTION???:" + pred_action)
                # self.dev_logger.info("DEBUG WHAT IS self.no_element_op???:"+ self.no_element_op)
                pred_action = "NONE"
            new_action = await self.perform_action(pred_element, pred_action, pred_value)
            self.taken_actions.append(new_action)
            if pred_action != "NONE":
                self.valid_op += 1
                self.continuous_no_op = 0
            else:
                self.continuous_no_op += 1
            return 0
        except Exception as e:

            new_action = f"Failed to perform {pred_action} on {pred_element['description']} with value '{pred_value}': {e}"


            traceback_info = traceback.format_exc()
            error_message = f"Error executing action {pred_action}: {str(e)}"
            print(traceback_info)
            # exit()
            error_message_with_traceback = f"{error_message}\n\nTraceback:\n{traceback_info}"

            self.logger.info(new_action)
            self.taken_actions.append(new_action)
            self.continuous_no_op += 1
            return 1

    async def stop(self):

        try:
            close_context = self.session_control['context']
            self.session_control['context'] = None
            await close_context.close()
            self.logger.info("Browser context closed.")
        except Exception as e:
            self.logger.info(e)

        final_json = {"task": self.tasks, "website": self.config["basic"]["default_website"],
                      "num_step": len(self.taken_actions), "action_history": self.taken_actions}

        def locator_serializer(obj):
            """Convert non-serializable objects to a serializable format."""
            if isinstance(obj, Locator):
                # Assuming Locator has attributes 'frame' and 'selector' you want to serialize
                return str(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        # Using the custom default function in json.dump
        with open(os.path.join(self.main_path, 'all_predictions.json'), 'w', encoding='utf-8') as f:
            json.dump(self.predictions, f, default=locator_serializer, indent=4)


        with open(os.path.join(self.main_path, 'result.json'), 'w', encoding='utf-8') as file:
            json.dump(final_json, file, indent=4)
        self.logger.info("Agent stopped.")

        saveconfig(self.config, os.path.join(self.main_path, 'config.toml'))

    def clear_action_history(self):
        """
        Clears the history of actions taken by the agent.
        """
        self.taken_actions.clear()
        self.logger.info("Cleared action history.")

    def reset_comlete_flag(self, flag=False):
        self.complete_flag = flag

    def change_task(self, new_task, clear_history=False):
        """
        Changes the task requirement for the agent.

        Parameters:
        - new_task: The new task requirement as a string.
        """
        if new_task and isinstance(new_task, str):

            self.logger.info(f"Changed task from {self.tasks[-1]} to: {new_task}")
            self.tasks.append(new_task)
            # Optionally clear action history when changing task
            if clear_history:
                self.clear_action_history()
            else:
                self.taken_actions.append(f"Changed task from {self.tasks[-2]} to: {new_task}")

        else:
            self.logger.info("Invalid new task. It must be a non-empty string.")

        # Optionally, you can save the taken_actions to a file or database for record-keeping

    # ADD no op count and op count, add limit to op

    # decompose run to predict and execute.

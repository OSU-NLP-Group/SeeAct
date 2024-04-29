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

from .format_prompt_utils import generate_new_referring_prompt, generate_new_query_prompt

##### SeeAct Online Prompts

seeact_online_sys_prompt = '''Imagine that you are imitating humans doing web navigation for a task step by step. At each stage, you can see the webpage like humans by a screenshot and know the previous actions before the current step decided by yourself through recorded history. You need to decide on the first following action to take. You can click on an element with the mouse, select an option, type text or press Enter with the keyboard. (For your understanding, they are like the click(), select_option() type() and keyboard.press('Enter') functions in playwright respectively) One next step means one operation within the four. Unlike humans, for typing (e.g., in text areas, text boxes) and selecting (e.g., from dropdown menus or <select> elements), you should try directly typing the input or selecting the choice, bypassing the need for an initial click. You should not attempt to create accounts, log in or do the final submission. Terminate when you deem the task complete or if it requires potentially harmful actions.'''

seeact_online_question_description_new_exp4 = '''The screenshot below shows the webpage you see. Follow the following guidance to think step by step before outlining the next action step at the current stage:

(Current Webpage Identification)
Firstly, think about what the current webpage is.

(Previous Action Analysis)
Secondly, combined with the screenshot, analyze each step of the previous action history and their intention one by one. Particularly, pay more attention to the last step, which may be more related to what you should do now as the next step. Specifically, if the last action involved a TYPE, always evaluate whether it necessitates a confirmation step, because typically a single TYPE action does not make effect. (often, simply pressing 'Enter', assuming the default element involved in the last action, unless other clear elements are present for operation).

(Screenshot Details Analysis)
Closely examine the screenshot to check the status of every part of the webpage to understand what you can operate with and what has been set or completed. You should closely examine the screenshot details to see what steps have been completed by previous actions even though you are given the textual previous actions. Because the textual history may not clearly and sufficiently record some effects of previous actions, you should closely evaluate the status of every part of the webpage to understand what you have done.

(Next Action Based on Webpage and Analysis)
Then, based on your analysis, in conjunction with human web browsing habits and the logic of web design, decide on the following action. And clearly outline which element in the webpage users will operate with as the first next target element, its detailed location, and the corresponding operation.

To be successful, it is important to follow the following rules: 
1. You should only issue a valid action given the current observation. 
2. You should only issue one action at a time
3. For handling the select dropdown elements on the webpage, it's not necessary for you to provide completely accurate options right now. The full list of options for these elements will be supplied later.'''

seeact_online_action_format = "ACTION: Choose an action from {CLICK, SELECT, TYPE, PRESS ENTER, TERMINATE, NONE}."

seeact_online_value_format = "VALUE: Provide additional input based on ACTION.\n\nThe VALUE means:\nIf ACTION == TYPE, specify the " \
               "text to be typed.\nIf ACTION == SELECT, indicate the option to be chosen. Revise the selection value to align with the available options within the element.\nIf ACTION == CLICK, PRESS ENTER, TERMINATE or NONE, " \
               "write \"None\"."

seeact_choice_prompt_dict = {
    "system_prompt": seeact_online_sys_prompt,

    "question_description": seeact_online_question_description_new_exp4,

    "referring_description": f"""(Reiteration)
First, reiterate your next target element, its detailed location, and the corresponding operation.

(Multichoice Question)
Below is a multi-choice question, where the choices are elements in the webpage. All elements are arranged in the order based on their height on the webpage, from top to bottom (and from left to right). This arrangement can be used to locate them. From the screenshot, find out where and what each one is on the webpage, taking into account both their text content and HTML details. Then, determine whether one matches your target element. Please examine the choices one by one. Choose the matching one. If multiple options match your answer, choose the most likely one by re-examining the screenshot, the choices, and your further reasoning.""",

    "element_format": """(Final Answer)
Finally, conclude your answer using the format below. Ensure your answer is strictly adhering to the format provided below. Please do not leave any explanation in your answers of the final standardized format part, and this final part should be clear and certain. The element choice, action, and value should be in three separate lines.

Format:

ELEMENT: The uppercase letter of your choice. (No need for PRESS ENTER)""",

    "action_format": f"{seeact_online_action_format}",

    "value_format": f"{seeact_online_value_format}"
}


def generate_prompt(experiment_split, task=None, previous=None, choices=None):
    assert experiment_split != None, "Please specify the experiment split."
    assert task != None, "Please input the task."
    assert previous != None, "Please input the previous actions."

    if False:
        raise Exception("Please change experiment type to seeact")
    elif experiment_split in ["seeact_online","online","seeact","SeeAct"]:
        system_prompt_input = seeact_choice_prompt_dict["system_prompt"]
        question_description_input = seeact_choice_prompt_dict["question_description"]
        referring_input = seeact_choice_prompt_dict["referring_description"]
        element_format_input = seeact_choice_prompt_dict["element_format"]
        action_format_input = seeact_choice_prompt_dict["action_format"]
        value_format_input = seeact_choice_prompt_dict["value_format"]
        prompt_list = []

        prompt_list.extend(
            generate_new_query_prompt(system_prompt=system_prompt_input, task=task, previous_actions=previous,
                                      question_description=question_description_input))
        prompt_list.append(
            generate_new_referring_prompt(referring_description=referring_input, element_format=element_format_input,
                                          action_format=action_format_input, value_format=value_format_input,
                                          choices=choices))
        return prompt_list


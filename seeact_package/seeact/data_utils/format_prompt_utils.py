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

import string

def generate_new_query_prompt(system_prompt="", task="", previous_actions=None, question_description=""):
    """
    Generate the first phase prompt to ask model to generate general descriptions about {environment, high-level plans, next step action}
    Each experiment will have a similar prompt in this phase
    This prompt is used to generate models' thoughts without disrupt of formatting/referring prompts
    """
    sys_role=""+system_prompt
    query_text = ""

    # System Prompt
    query_text += "You are asked to complete the following task: "

    # Task Description
    query_text += task
    query_text += "\n\n"

    # Previous Actions
    previous_action_text = "Previous Actions:\n"
    if previous_actions is None:
        previous_actions = []
    for action_text in previous_actions:
        previous_action_text += action_text
        previous_action_text += "\n"
    query_text += previous_action_text
    query_text += "\n"

    # Question Description
    query_text += question_description
    return [sys_role,query_text]



def generate_new_referring_prompt(referring_description="", element_format="", action_format="", value_format="",
                              choices=None,split="4"):
    referring_prompt = ""

    # Add description about how to format output
    if referring_description != "":
        referring_prompt += referring_description
        referring_prompt += "\n\n"

    # Add element prediction format and choices


    # Prepare Option texts
    # For exp {1, 2, 4}, generate option
    # For element_atttribute, set options field at None
    if choices:
        choice_text = format_options(choices)
        referring_prompt += choice_text

    if element_format != "":
        referring_prompt += element_format
        referring_prompt += "\n\n"

    # Format Action Prediction
    if action_format != "":
        referring_prompt += action_format
        referring_prompt += "\n\n"

    # Format Value Prediction
    if value_format != "":
        referring_prompt += value_format
        referring_prompt += ""

    return referring_prompt

def format_options(choices):
    option_text = ""
    abcd = ''
    non_abcd = ''

    multi_choice = ''
    for multichoice_idx, choice in enumerate(choices):
        multi_choice += f"{generate_option_name(multichoice_idx)}. {choice}\n"
        abcd += f"{generate_option_name(multichoice_idx)}, "

        non_abcd = generate_option_name(multichoice_idx + 1)

    multi_choice += f"{non_abcd}. None of the other options match the correct element or the action doesn't involve an element."
    # option_text += abcd
    option_text += f"If none of these elements match your target element or your target action doesn't involve an element, please select {non_abcd}.\n"
    option_text += (multi_choice + '\n\n')
    return option_text


def generate_option_name(index):
    if index < 26:
        return string.ascii_uppercase[index]
    else:
        first_letter_index = (index - 26) // 26
        second_letter_index = (index - 26) % 26
        first_letter = string.ascii_uppercase[first_letter_index]
        second_letter = string.ascii_uppercase[second_letter_index]
        return f"{first_letter}{second_letter}"

def get_index_from_option_name(name):
    if len(name) == 1:
        return string.ascii_uppercase.index(name)
    elif len(name) == 2:
        first_letter_index = string.ascii_uppercase.index(name[0])
        second_letter_index = string.ascii_uppercase.index(name[1])
        return 26 + first_letter_index * 26 + second_letter_index
    else:
        raise Exception("The string should be either 1 or 2 characters long")



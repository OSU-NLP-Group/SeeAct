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
import lxml
from .dom_utils import get_tree_repr, data_prune_tree
def data_format_input_multichoice(
        sample, candidate_ids, gt=-1, previous_k=5, keep_html_brackets=False
):
    # Parse html into a dom tree
    dom_tree = lxml.etree.fromstring(sample["cleaned_html"])
    dom_tree, node_to_keep = data_prune_tree(dom_tree, candidate_ids)
    tree_repr, id_mapping = get_tree_repr(
        dom_tree, id_mapping={}, keep_html_brackets=keep_html_brackets
    )
    candidate_nodes = dom_tree.xpath("//*[@backend_node_id]")
    choices = []
    for idx, node in enumerate(candidate_nodes):
        temp = get_tree_repr(
            node,
            id_mapping=id_mapping,
            keep_html_brackets=keep_html_brackets,
        )
        choices.append(
            [
                node.attrib["backend_node_id"],
                " ".join(
                    get_tree_repr(
                        node,
                        id_mapping=id_mapping,
                        keep_html_brackets=keep_html_brackets,
                    )[0].split()[:10]
                ),
            ]
        )
    gt = id_mapping.get(gt, -1)
    seq_input = (
        "Based on the HTML webpage above, try to complete the following task:\n"
        f"Task: {sample['confirmed_task']}\n"
        f"Previous actions:\n"
    )
    if len(sample["previous_actions"]) > 0:
        for action in sample["previous_actions"][-previous_k:]:
            seq_input += f"{action}\n"
    else:
        seq_input += "None\n"
    seq_input += (
        "What should be the next action? Please select from the following choices "
        "(If the correct action is not in the page above, please select A. 'None of the above'):\n\n"
        "A. None of the above\n"
    )
    for idx, choice in enumerate(choices):
        # convert to ascii A, B, C, D, ...
        seq_input += f"{chr(66 + idx)}. {choice[1]}\n"
    if gt == -1:
        seq_target = "A."
    else:
        gt += 1
        current_action_op = sample["operation"]["op"]
        current_action_value = sample["operation"]["value"]
        seq_target = f"{chr(65 + gt)}.\n" f"Action: {current_action_op}\n"
        if current_action_op != "CLICK":
            seq_target += f"Value: {current_action_value}"
    return tree_repr, seq_input, seq_target, choices, node_to_keep


def generate_query_prompt(system_prompt="", task="", previous_actions=None, question_description=""):
    """
    Generate the first phase prompt to ask model to generate general descriptions about {environment, high-level plans, next step action}
    Each experiment will have a similar prompt in this phase
    This prompt is used to generate models' thoughts without disrupt of formatting/referring prompts
    """
    query_text = ""

    # System Prompt
    query_text += system_prompt

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
    return query_text


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

def generate_referring_prompt(referring_description="", element_format="", action_format="", value_format="",
                              choices=None):
    referring_prompt = ""

    # Add description about how to format output
    if referring_description != "":
        referring_prompt += referring_description
        referring_prompt += "\n\n"

    # Add element prediction format and choices
    if element_format != "":
        referring_prompt += element_format
        referring_prompt += "\n\n"

    # Prepare Option texts
    # For exp {1, 2, 4}, generate option
    # For element_atttribute, set options field at None
    if choices:
        choice_text = format_options(choices)
        referring_prompt += choice_text

    # Format Action Prediction
    if action_format != "":
        referring_prompt += action_format
        referring_prompt += "\n\n"

    # Format Value Prediction
    if value_format != "":
        referring_prompt += value_format
        referring_prompt += ""

    return referring_prompt


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
        multi_choice += f"{generate_option_name(multichoice_idx)}. {choice[1]}\n"
        abcd += f"{generate_option_name(multichoice_idx)}, "

        non_abcd = generate_option_name(multichoice_idx + 1)

    multi_choice += f"{non_abcd}. None of the other options match the correct element"
    # option_text += abcd
    option_text += f"If none of these elements match your target element, please select {non_abcd}. None of the other options match the correct element.\n"

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



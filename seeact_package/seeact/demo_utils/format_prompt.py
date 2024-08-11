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
import re
import shlex

def format_choices(elements):
    converted_elements = []
    elements_w_descriptions = []
    for element in elements:
        if "description" in element and "=" in element["description"] and "'" not in element["description"] and "\"" not in element["description"]:
            description_dict = [] 
            for sub in shlex.split(element["description"]): 
                if '=' in sub:
                    description_dict.append(map(str.strip, sub.split('=', 1)))
            element.update(dict(description_dict))
        elements_w_descriptions.append(element)

    converted_elements = []
    for i, element in enumerate(elements_w_descriptions):
        converted = ""
        if element['tag']!="select":
            converted += f'{element["center_point"]} <{element["tag_with_role"]}">'
            converted += (
                element["description"]
                if len(element["description"].split()) < 30
                else " ".join(element["description"].split()[:30]) + "..."
            )
            converted += f"</{element['tag']}>"
        else:
            converted += f'{element["center_point"]} <{element["tag_with_role"]}>'
            converted += (
                element["description"]
            )
            converted += f"</{element['tag']}>"
        converted_elements.append(converted)

    return converted_elements

def postprocess_action_lmm(text):
    text = text.strip()
    text = text.replace(
        "The uppercase letter of your choice. Choose one of the following elements if it matches the target element based on your analysis:\n\n",
        "")
    text = text.replace(
        "The uppercase letter of your choice. Choose one of the following elements if it matches the target element based on your analysis:\n",
        "")
    text = text.replace(
        "The uppercase letter of your choice. Choose one of the following elements if it matches the target element based on your analysis:",
        "")
    text = text.replace("The uppercase letter of your choice based on your analysis is:\n\n", "")
    text = text.replace("The uppercase letter of your choice based on your analysis is:\n", "")
    text = text.replace("The uppercase letter of your choice based on your analysis is:", "")
    text = text.replace("The uppercase letter of my choice is \n\n", "")
    text = text.replace("The uppercase letter of my choice is \n", "")
    text = text.replace("The uppercase letter of my choice is ", "")
    text = text.replace("The uppercase letter of your choice is \n\n", "")
    text = text.replace("The uppercase letter of your choice is \n", "")
    text = text.replace("The uppercase letter of your choice is ", "")
    text = text.replace("The uppercase letter of your choice.\n\n", "")
    text = text.replace("The uppercase letter of your choice.\n", "")
    text = text.replace("The uppercase letter of your choice.", "")
    text = text.replace("The uppercase letter of your choice based on my analysis is:\n\n", "")
    text = text.replace("The uppercase letter of your choice based on my analysis is:\n", "")
    text = text.replace("The uppercase letter of your choice based on my analysis is:", "")
    text = text.replace("The correct choice based on the analysis would be:\n\n", "")
    text = text.replace("The correct choice based on the analysis would be:\n", "")
    text = text.replace("The correct choice based on the analysis would be :", "")
    text = text.replace("The correct choice based on the analysis would be ", "")
    text = text.replace(
        "The uppercase letter of your choice. Choose one of the following elements if it matches the target element based on your analysis:\n\n",
        "")
    text = text.replace(
        "The uppercase letter of your choice. Choose one of the following elements if it matches the target element based on your analysis:\n",
        "")
    text = text.replace(
        "The uppercase letter of your choice. Choose one of the following elements if it matches the target element based on your analysis:",
        "")
    text = text.replace("The uppercase letter of your choice.\n\n", "")
    text = text.replace("The uppercase letter of your choice.\n", "")
    text = text.replace("The uppercase letter of your choice based on the analysis is:\n\n", "")
    text = text.replace("The uppercase letter of your choice based on the analysis is:\n", "")
    text = text.replace("The uppercase letter of your choice based on the analysis is:", "")
    text = text.replace("The uppercase letter of your choice based on the analysis is ", "")
    text = text.replace("The uppercase letter of my choice based on the analysis is:\n\n", "")
    text = text.replace("The uppercase letter of my choice based on the analysis is:\n", "")
    text = text.replace("The uppercase letter of my choice based on the analysis is:", "")
    text = text.replace("The uppercase letter of my choice based on the analysis is ", "")
    text = text.replace("The correct element to select would be:\n\n", "")
    text = text.replace("The correct element to select would be:\n", "")
    text = text.replace("The correct element to select would be:", "")
    text = text.replace("The correct element to select would be ", "")
    text = text.replace("The uppercase letter of my choice is:\n\n", "")
    text = text.replace("The uppercase letter of my choice is:\n", "")
    text = text.replace("The uppercase letter of my choice is:", "")
    text = text.replace("The uppercase letter of my choice is ", "")
    text = text.replace("Choose an action from {CLICK, TYPE, SELECT}.\n\n", "")
    text = text.replace("Choose an action from {CLICK, TYPE, SELECT}.\n", "")
    text = text.replace("Choose an action from {CLICK, TYPE, SELECT}.", "")
    text = text.replace("Provide additional input based on ACTION.\n\n", "")
    text = text.replace("Provide additional input based on ACTION.\n", "")
    text = text.replace("Provide additional input based on ACTION.", "")
    selected_option = re.findall(r"ELEMENT: ([A-Z]{2}|[A-Z])", text)

    if selected_option:
        selected_option = (
            selected_option[0]
        )
    else:
        selected_option = "Invalid"

    action = re.search(
        r"ACTION: (CLICK|SELECT|TYPE|HOVER|PRESS ENTER|SCROLL UP|SCROLL DOWN|PRESS HOME|PRESS END|PRESS PAGEUP|PRESS PAGEDOWN|NEW TAB|CLOSE TAB|GO BACK|GO FORWARD|TERMINATE|NONE|GOTO|SAY|MEMORIZE)",
        text
    )


    if action:
        action = action.group(1)
        start = text.find(f"ACTION: {action}")
        for probing_length in range(15, 160, 10):
            selected_option_from_action = re.findall(
                r"ELEMENT: ([A-Z]{2}|[A-Z])",
                text[max(start - probing_length, 0):start])
            # print("text span:",text[max(start-probing_length,0):start])
            # print("finded group:",selected_option__)
            if selected_option_from_action:
                selected_option = selected_option_from_action[0]
                break
    else:
        action = "None"

    value = re.search(r"VALUE: (.*)$", text, re.MULTILINE)
    value = value.group(1) if value is not None else ""
    return selected_option, action.strip(), process_string(process_string(value.strip()))

def process_string(input_string):
    if input_string.startswith('"') and input_string.endswith('"'):
        input_string = input_string[1:-1]
    if input_string.endswith('.'):
        input_string = input_string[:-1]
    return input_string










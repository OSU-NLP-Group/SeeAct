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
import asyncio
from difflib import SequenceMatcher
from playwright.sync_api import Playwright, expect, sync_playwright
# from playwright.async_api import async_playwright
from pathlib import Path
import toml
import os

async def normal_launch_async(playwright: Playwright,headless=False,args=None):
    browser = await playwright.chromium.launch(
        traces_dir=None,
        headless=False,
        args=args,
        # ignore_default_args=ignore_args,
        # chromium_sandbox=False,
    )
    return browser



async def normal_new_context_async(
        browser,
        storage_state=None,
        har_path=None,
        video_path=None,
        tracing=False,
        trace_screenshots=False,
        trace_snapshots=False,
        trace_sources=False,
        locale=None,
        geolocation=None,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        viewport: dict = {"width": 1280, "height": 720},
):
    context = await browser.new_context(
        storage_state=storage_state,
        user_agent=user_agent,
        viewport=viewport,
        locale=locale,
        record_har_path=har_path,
        record_video_dir=video_path,
        geolocation=geolocation,
    )

    if tracing:
        await context.tracing.start(screenshots=trace_screenshots, snapshots=trace_snapshots, sources=trace_sources)
    return context

#
# def persistent_launch(playwright: Playwright, user_data_dir: str = ""):
#     context = playwright.chromium.launch_persistent_context(
#         user_data_dir=user_data_dir,
#         headless=False,
#         args=["--no-default-browser-check",
#               "--no_sandbox",
#               "--disable-blink-features=AutomationControlled",
#               ],
#         ignore_default_args=ignore_args,
#         user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
#         viewport={"width": 1280, "height": 720},
#         bypass_csp=True,
#         slow_mo=1000,
#         chromium_sandbox=True,
#         channel="chrome-dev"
#     )
#     return context

#
# async def persistent_launch_async(playwright: Playwright, user_data_dir: str = "", record_video_dir="video"):
#     context = await playwright.chromium.launch_persistent_context(
#         user_data_dir=user_data_dir,
#         headless=False,
#         args=[
#             "--disable-blink-features=AutomationControlled",
#         ],
#         ignore_default_args=ignore_args,
#         user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
#         # viewport={"width": 1280, "height": 720},
#         record_video_dir=record_video_dir,
#         channel="chrome-dev"
#         # slow_mo=1000,
#     )
#     return context



def remove_extra_eol(text):
    # Replace EOL symbols
    text = text.replace('\n', ' ')
    return re.sub(r'\s{2,}', ' ', text)


def get_first_line(s):
    first_line = s.split('\n')[0]
    tokens = first_line.split()
    if len(tokens) > 8:
        return ' '.join(tokens[:8]) + '...'
    else:
        return first_line

async def get_element_description(element, tag_name, role_value, type_value):
    '''
         Asynchronously generates a descriptive text for a web element based on its tag type.
         Handles various HTML elements like 'select', 'input', and 'textarea', extracting attributes and content relevant to accessibility and interaction.
    '''
    # text_content = await element.inner_text(timeout=0)
    # text = (text_content or '').strip()
    #
    # print(text)
    salient_attributes = [
        "alt",
        "aria-describedby",
        "aria-label",
        "aria-role",
        "input-checked",
        # "input-value",
        "label",
        "name",
        "option_selected",
        "placeholder",
        "readonly",
        "text-value",
        "title",
        "value",
    ]

    parent_value = "parent_node: "
    parent_locator = element.locator('xpath=..')
    num_parents = await parent_locator.count()
    if num_parents > 0:
        # only will be zero or one parent node
        parent_text = (await parent_locator.inner_text(timeout=0) or "").strip()
        if parent_text:
            parent_value += parent_text
    parent_value = remove_extra_eol(get_first_line(parent_value)).strip()
    if parent_value == "parent_node:":
        parent_value = ""
    else:
        parent_value += " "

    if tag_name == "select":
        text1 = "Selected Options: "
        text3 = " - Options: "

        text2 = await element.evaluate(
            "select => select.options[select.selectedIndex].textContent", timeout=0
        )

        if text2:
            options = await element.evaluate("select => Array.from(select.options).map(option => option.text)",
                                             timeout=0)
            text4 = " | ".join(options)

            if not text4:
                text4 = await element.text_content(timeout=0)
                if not text4:
                    text4 = await element.inner_text(timeout=0)


            return parent_value+text1 + remove_extra_eol(text2.strip()) + text3 + text4

    input_value = ""

    none_input_type = ["submit", "reset", "checkbox", "radio", "button", "file"]

    if tag_name == "input" or tag_name == "textarea":
        if role_value not in none_input_type and type_value not in none_input_type:
            text1 = "input value="
            text2 = await element.input_value(timeout=0)
            if text2:
                input_value = text1 + "\"" + text2 + "\"" + " "

    text_content = await element.text_content(timeout=0)
    text = (text_content or '').strip()

    # print(text)
    if text:
        text = remove_extra_eol(text)
        if len(text) > 80:
            text_content_in = await element.inner_text(timeout=0)
            text_in = (text_content_in or '').strip()
            if text_in:
                return input_value + remove_extra_eol(text_in)
        else:
            return input_value + text

    # get salient_attributes
    text1 = ""
    for attr in salient_attributes:
        attribute_value = await element.get_attribute(attr, timeout=0)
        if attribute_value:
            text1 += f"{attr}=" + "\"" + attribute_value.strip() + "\"" + " "

    text = (parent_value + text1).strip()
    if text:
        return input_value + remove_extra_eol(text.strip())


    # try to get from the first child node
    first_child_locator = element.locator('xpath=./child::*[1]')

    num_childs = await first_child_locator.count()
    if num_childs>0:
        for attr in salient_attributes:
            attribute_value = await first_child_locator.get_attribute(attr, timeout=0)
            if attribute_value:
                text1 += f"{attr}=" + "\"" + attribute_value.strip() + "\"" + " "

        text = (parent_value + text1).strip()
        if text:
            return input_value + remove_extra_eol(text.strip())

    return None


async def get_element_data(element, tag_name,viewport_size,seen_elements=[]):
    try:
        tag_name_list = ['a', 'button',
                         'input',
                         'select', 'textarea', 'adc-tab']


        if await element.is_hidden(timeout=0) or await element.is_disabled(timeout=0):
            return None



        rect = await element.bounding_box() or {'x': -1, 'y': -1, 'width': 0, 'height': 0}


        if rect['x']<0 or rect['y']<0 or rect['width']<=4 or rect['height']<=4 or rect['y']+rect['height']>viewport_size["height"] or rect['x']+ rect['width']>viewport_size["width"]:
            return None

        box_raw = [rect['x'], rect['y'], rect['width'], rect['height']]
        box_model = [rect['x'], rect['y'], rect['x'] + rect['width'], rect['y'] + rect['height']]
        center_point = (round((box_model[0] + box_model[2]) / 2 / viewport_size["width"], 3),
                        round((box_model[1] + box_model[3]) / 2 / viewport_size["height"], 3))

        if center_point in seen_elements:
            return None

        # await aprint(element,tag_name)

        if tag_name in tag_name_list:
            tag_head = tag_name
            real_tag_name = tag_name
        else:
            real_tag_name = await element.evaluate("element => element.tagName.toLowerCase()", timeout=0)
            if real_tag_name in tag_name_list:
                # already detected
                return None
            else:
                tag_head = real_tag_name

        text_element = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', "div","em","center","strong","b","i","small","mark","abbr","cite","q","blockquote","span","nobr"]

        if real_tag_name in text_element:
            return None

        role_value = await element.get_attribute('role', timeout=0)
        type_value = await element.get_attribute('type', timeout=0)
        # await aprint("start to get element description",element,tag_name )
        description = await get_element_description(element, real_tag_name, role_value, type_value)
        # print(description)
        if not description:
            return None

        if role_value:
            tag_head += " role=" + "\"" + role_value + "\""
        if type_value:
            tag_head += " type=" + "\"" + type_value + "\""

        '''
                     0: center_point =(x,y)
                     1: description
                     2: tag_with_role: tag_head with role and type # TODO: Consider adding more
                     3. box
                     4. selector
                     5. tag
                     '''
        selector = element
        return {
            "center_point":center_point,
            "description":description,
            "tag_with_role":tag_head,
            "box_raw":box_raw,
            "box":box_model,
            "selector":selector,
            "tag":real_tag_name
        }
        # return [center_point, description, tag_head, box_model, selector, real_tag_name]
    except Exception as e:
        # print(e)
        return None


async def get_interactive_elements_with_playwright(page,viewport_size):
    interactive_elements_selectors = [
        'a', 'button',
        'input',
        'select', 'textarea',
    ]

    seen_elements = set()
    tasks = []


    for selector in interactive_elements_selectors:
        locator = page.locator(selector)
        element_count = await locator.count()
        for index in range(element_count):
            element = locator.nth(index)
            tag_name = selector
            task = get_element_data(element, tag_name,viewport_size)

            tasks.append(task)

    results = await asyncio.gather(*tasks)

    interactive_elements = []
    for i in results:
        if i:
            if i["center_point"] in seen_elements:
                continue
            else:
                seen_elements.add(i["center_point"])
                interactive_elements.append(i)

    interactive_elements_selectors = [
        '*'
    ]
    tasks = []

    for selector in interactive_elements_selectors:
        locator = page.locator(selector)
        element_count = await locator.count()
        for index in range(element_count):
            element = locator.nth(index)
            tag_name = selector
            task = get_element_data(element, tag_name, viewport_size,seen_elements)

            tasks.append(task)

    results = await asyncio.gather(*tasks)


    for i in results:
        if i:
            if i["center_point"] in seen_elements:
                continue
            else:
                seen_elements.add(i["center_point"])
                interactive_elements.append(i)

    return interactive_elements


async def select_option(selector, value):
    best_option = [-1, "", -1]
    for i in range(await selector.locator("option").count()):
        option = await selector.locator("option").nth(i).inner_text()
        similarity = SequenceMatcher(None, option, value).ratio()
        if similarity > best_option[2]:
            best_option = [i, option, similarity]
    await selector.select_option(index=best_option[0], timeout=10000)
    return remove_extra_eol(best_option[1]).strip()


def saveconfig(config, save_file):
    """
    config is a dictionary.
    save_path: saving path include file name.
    """


    if isinstance(save_file, str):
        save_file = Path(save_file)
    if isinstance(config, dict):
        with open(save_file, 'w') as f:
            config_without_key = config
            config_without_key["openai"]["api_key"] = "Your API key here"
            toml.dump(config_without_key, f)
    else:
        os.system(" ".join(["cp", str(config), str(save_file)]))

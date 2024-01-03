import lxml
import re
from utils.dom_utils import get_tree_repr, prune_tree

prompt_dict = {
    "default_prompt" : """/*
You are interacting with a web page. You will be given a list of elements that you can interact with. The actions you can take for each element are listed below.
<button>: click
<checkbox>: click
<radio>: click
<combobox>: value = "X"
<textbox>: value = "X"
<listbox>: value = "X"
<menu>: click
<tree>: click
<a>: click
You can take one action each time and will be given a new list of elements. You can also choose to stop interacting with the page at any time.
*/

/*
Now you are at http://yelp.com. Here is the list of elements that you can interact with:
<a>Help</a>
<button>Toggle Menu</button>
<a>Yelp for Business</a>
<a>Write a Review</a>
<a>Yelp</a>
<textbox>Find</textbox>
<textbox>Near</textbox>
<button>Search</button>
<a>Messages</a>
<button>Notifications</button>
<a>Restaurants</a>
<a>Home Services</a>
<a>Auto Services</a>
<a>More</a>
<button>Select slide</button>
<a>Auto repair</a>
<button>Select slide 0</button>
<button>Select slide 1</button>
<a>RepairSmith</a>
<button>Dismiss card 0</button>
<button>Dismiss card 1</button>
<a>Brassica</a>
<a>Fox In the Snow Cafe</a>
<radio>1 star rating</radio>
<radio>2 star rating</radio>
<radio>3 star rating</radio>
*/

//OBJECTIVE: find chinese restaurants in san francisco

//The list of actions you have taken:

//What is your next action?
document.querySelector('textbox:contains("Find")').value = "chinese";

"""
}

llm_prompt = [
    {
        "role": "system",
        "content": "You are a helpful assistant that is great at website design, navigation, and executing tasks for the user."
    },
    {
        "role": "user",
        "content": "'''\n<html> <div> <div> <a tock home page /> <button id=0 book a reservation. toggle open> <span> Book a reservation </span> </button> <button book a reservation. toggle open> </button> </div> <div> <select id=1 type> <option reservations true> Dine in </option> <option pickup> Pickup </option> <option delivery> Delivery </option> <option events> Events </option> <option wineries> Wineries </option> <option all> Everything </option> </select> <div id=2> <p> Celebrating and supporting leading women shaking up the industry. </p> <span> Explore now </span> </div> </div> </div> </html>\n'''\n\nBased on the HTML webpage above, try to complete the following task:\nTask: Check for pickup restaurant available in Boston, NY on March 18, 5pm with just one guest\nPrevious actions:\nNone\nWhat should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):\n\nA. None of the above\nB. <button id=0 book a reservation. toggle open> <span> Book a\nC. <select id=1 type> <option reservations true> Dine in </option> <option\nD. <div id=2> <p> Celebrating and supporting leading women shaking up"
    },
    {
        "role": "assistant",
        "content": "Answer: C.\nAction: SELECT\nValue: Pickup"
    },
    {
        "role": "user",
        "content": "'''\n<html> <div> <main main> <section tabpanel> <div> <ul tablist> <li tab heading level 3 search and> </li> <li id=0 tab heading level 3 search and> <span> Hotel </span> </li> <li tab heading level 3 search and> </li> <li tab heading level 3 search and> </li> </ul> <div tabpanel> <div id=1> <div> <span> Dates* </span> <button button clear dates /> </div> <div> <label> Travelers </label> <div> <p> 1 Adult </p> <button button> 1 Adult </button> <div dialog> <button button travel with a pet. this> <span> Travel with a pet </span> </button> <div> <button button clear all fields> Clear all </button> <button button> </button> </div> </div> </div> </div> </div> </div> </div> </section> </main> <footer contentinfo> <div> <h3> Stay Connected </h3> <ul id=2> <a mobile tools> </a> <a open united's tiktok feed in> </a> <a open united's facebook page in> </a> <a open united's twitter feed in> </a> <a open united's youtube page in> </a> <a open united's instagram feed in> </a> <a open united's linkedin profile in> </a> </ul> </div> </footer> </div> </html>\n'''\n\nBased on the HTML webpage above, try to complete the following task:\nTask: Compare the fare types to book a 1-adult ticket from Springfiels, IL to Austin, TX for April 29th 2023\nPrevious actions:\n[combobox]  Enter your departing city, airport name, or airpor... -> TYPE: SPRINGFIELD\n[button]  Springfield, IL, US (SPI) -> CLICK\n[combobox]  Enter your destination city, airport name, or airp... -> TYPE: AUSTIN\n[button]  Austin, TX, US (AUS) -> CLICK\nWhat should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):\n\nA. None of the above\nB. <li id=0 tab heading level 3 search and> <span> Hotel\nC. <div id=1> <div> <span> Dates* </span> <button button clear dates\nD. <ul id=2> <a mobile tools> </a> <a open united's tiktok"
    },
    {
        "role": "assistant",
        "content": "Answer: A."
    },
    {
        "role": "user",
        "content": "'''\n<html> <div> <nav main menu> <ul> <li> <div button> Car Sales </div> <div id=0> <div> <div> <div> Buy A Car </div> <div> Plan Your Purchase </div> </div> <div> <h4> Its Tax Refund Time. Treat Yourself to an Upgrade. </h4> <p> With a variety of options, invest your refund in what you really want - a quality, used vehicle from Enterprise. </p> <a> View Inventory </a> </div> </div> </div> </li> <div id=1> Enterprise Fleet Management </div> </ul> </nav> <div region> <button id=2 selected pick-up date 03/19/2023> <span> <span> 19 </span> <div> <span> Mar </span> <span> 2023 </span> </div> </span> </button> </div> </div> </html>\n'''\n\nBased on the HTML webpage above, try to complete the following task:\nTask: Find a mini van at Brooklyn City from April 5th to April 8th for a 22 year old renter.\nPrevious actions:\n[searchbox]  Pick-up & Return Location (ZIP, City or Airport) (... -> TYPE: Brooklyn\n[option]  Brooklyn, NY, US Select -> CLICK\nWhat should be the next action? Please select from the following choices (If the correct action is not in the page above, please select A. 'None of the above'):\n\nA. None of the above\nB. <div id=0> <div> <div> <div> Buy A Car </div> <div>\nC. <div id=1> Enterprise Fleet Management </div>\nD. <button id=2 selected pick-up date 03/19/2023> <span> <span> 19 </span>"
    },
    {
        "role": "assistant",
        "content": "Answer: D.\nAction: CLICK"
    },
    {
        "role": "user",
        "content": ""
    }
]



def original_prompt(elements, selected_website, objective, taken_actions):
    prompt = (
            prompt_dict['default_prompt']
            + f"/*\nNow you are at {selected_website[0]}. Here is the list of elements you can interact with:\n"
    )
    prompt += (
            "\n".join(
                [
                    # f'[name="{element[1] if len(element[1].split())<10 else " ".join(element[1].split()[:10])+"..."}" id={i} {element[2].upper()}]'
                    f'<{element[2]} id="{i}">'
                    + (
                        element[1]
                        if len(element[1].split()) < 10
                        else " ".join(element[1].split()[:10]) + "..."
                    )
                    + f"</{element[2]}>"
                    for i, element in enumerate(elements)
                ]
            )
            + "\n*/\n"
    )
    prompt += f"//OBJECTIVE: {objective}\n"
    prompt += (
            "//The list of actions you have taken:\n"
            + "\n".join(taken_actions)
            + "\n\n"
    )
    prompt += "//What is your next action? Select with the element type, id and text content.\ndocument.querySelector('"

    return prompt

def format_ranking_input(elements, task, previous_actions):
    converted_elements = [
                    f'<{element[2]} id="{i}">'
                    + (
                        element[1]
                        if len(element[1].split()) < 30
                        else " ".join(element[1].split()[:30]) + "..."
                    )
                    + f"</{element[2]}>"
                    for i, element in enumerate(elements)
                ]

    query = (
        f'task is: {task}\n'
        f'Previous actions: {"; ".join(previous_actions[-3:])}'
    )

    model_input = [[query, doc] for doc in converted_elements]
    return model_input


def format_llm_input_with_explain(elements, candidate_ids, objective, taken_actions, previous_k=5):
    prompt_template = llm_prompt

    converted_elements = [
        f'<{element[2]} id="{i}">'
        + (
            element[1]
            if len(element[1].split()) < 10
            else " ".join(element[1].split()[:10]) + "..."
        )
        + f"</{element[2]}>"
        for i, element in enumerate(elements)
    ]

    # Generate context of the website
    html_context = ""
    html_context += ("\n".join(converted_elements) + "\n*/\n")

    # Task description
    seq_input = (
        "Based on the HTML webpage above, try to complete the following task:\n"
        f"Task: {objective}\n"
        f"Previous actions:\n"
    )
    # Add previous actions
    if len(taken_actions) > 0:
        for action in taken_actions[-previous_k:]:
            seq_input += f"{action}\n"
    else:
        seq_input += "None\n"

    seq_input += (
        "On the webpage, you'll find five essential DOM elements required to complete the forthcoming task. Please "
        "analyze the function of each element and offer instructions on its use. Address each of the listed elements "
        "individually."
    )
    choices = [[str(i), converted_elements[i]] for i in candidate_ids]
    for idx, choice in enumerate(choices):
        # convert to ascii A, B, C, D, ...
        seq_input += f"{chr(65 + idx)}. {choice[1]}\n"
    # # Actions to generate
    # seq_input += (
    #     "What should be the next action?Please select from the following choices"
    #     "(If the correct action is not in the page above, please select A. 'None of the above'):\n\n"
    #     "A. None of the above\n"
    # )
    # choices = [[str(i), converted_elements[i]] for i in candidate_ids]
    # for idx, choice in enumerate(choices):
    #     # convert to ascii A, B, C, D, ...
    #     seq_input += f"{chr(66 + idx)}. {choice[1]}\n"

    # Fit into prompt template
    prompt_template[-1][
        "content"
    ] = f"'''\n{html_context}\n'''\n\n{seq_input}"

    return prompt_template, choices


def format_llm_input(elements, candidate_ids, objective, taken_actions, previous_k=5):
    prompt_template = llm_prompt

    converted_elements = [
                    f'<{element[2]} id="{i}">'
                    + (
                        element[1]
                        if len(element[1].split()) < 60
                        else " ".join(element[1].split()[:60]) + "..."
                    )
                    + f"</{element[-1]}>"

                    if element[2]!="select" else f'<{element[2]} id="{i}">'
                    + (
                        element[1]
                    )
                    + f"</{element[-1]}>"



                    for i, element in enumerate(elements)
                ]

    # Generate context of the website
    html_context = ""
    html_context += ("\n".join(converted_elements)+ "\n*/\n")

    # Task description
    seq_input = (
        "Based on the HTML webpage above, try to complete the following task:\n"
        f"Task: {objective}\n"
        f"Previous actions:\n"
    )
    # Add previous actions
    if len(taken_actions) > 0:
        for action in taken_actions[-previous_k:]:
            seq_input += f"{action}\n"
    else:
        seq_input += "None\n"

    # Actions to generate
    seq_input += (
        "What should be the next action? Please select from the following choices "
        "(If the correct action is not in the page above, please select A. 'None of the above'):\n\n"
        "A. None of the above\n"
    )
    choices = [[str(i), converted_elements[i]] for i in candidate_ids]
    for idx, choice in enumerate(choices):
        # convert to ascii A, B, C, D, ...
        seq_input += f"{chr(66 + idx)}. {choice[1]}\n"

    # Fit into prompt template
    prompt_template[-1][
        "content"
    ] = f"'''\n{html_context}\n'''\n\n{seq_input}"

    return prompt_template, choices

def postprocess_action_llm(text):
    # C.
    # Action: SELECT
    # Value: Queen
    text = text.strip()
    selected_option = re.search(r"Answer: (A|B|C|D|E|F)", text)
    simplified_answer=False
    if selected_option is not None:
        selected_option = (
            selected_option.group(1)
        )
    elif "Answer" not in text and text[0] in ["A","B","C", "D","E","F"]:
        print("Simplifed format answer, retrieved by first letter")
        selected_option=text[0]
    else:
        selected_option = "A"


    action = re.search(r"Action: (CLICK|SELECT|TYPE)", text)


    action = action.group(1) if action is not None else "CLICK"
    value = re.search(r"Value: (.*)$", text, re.MULTILINE)
    value = value.group(1) if value is not None else ""
    if action == "TYPE" and value == "":
        value=re.search(r"TYPE: (.*)$", text, re.MULTILINE)
        value = value.group(1) if value is not None else ""
    elif action == "SELECT" and value == "":
        value=re.search(r"SELECT: (.*)$", text, re.MULTILINE)
        value = value.group(1) if value is not None else ""
    return selected_option, action.strip(), value.strip()


def process_string(input_string):
    if input_string.startswith('"') and input_string.endswith('"'):
        input_string = input_string[1:-1]

    if input_string.endswith('.'):
        input_string = input_string[:-1]
    return input_string











import os

exp2_prompt_dict = {
    "system_prompt": """Imagine that you are imitating human doing web navigation for a task step by step. At each stage, you can see the webpage like human by a given screenshot, and know the previous actions that has done. You can click an element with the mouse, select an option, or type some texts with the keyboard.\n\nYou are asked to complete the following task: """,

    "question_description": """Below the screenshot is the webpage you see. Follow the following guidance to think step by step before clearly outlining the next action step at current stage that user would like to take(Not all the subsequent actions):\n\nFirstly, think about what is the current webpage.  In the provided webpage screenshot, there are red bounding boxes highlighting specific elements. Each bounding box is labeled with a number in the top-left corner, displayed in white font against a black background, ranging from 0 to 19. Use these numbered labels to refer to the specific element you want to interact with for the next step. Please pay attention to them because the elements covered in bounding boxes are very likely to be the element you need to interact with. \n\nSecondly, look into details of the screenshot and the previous action history. Think about what have done by each of the previous actions and the intention of each of them one by one. Particularly, pay more attention to the last step, which has more information about what you should do now. When an action in previous action history is unclear, look into details of the screenshot to see what has been operated while not listed, in conjunction with human's web browsing habits, to understand what is that action and what have done at that step.\n\nThen, based on your analysis about the webpage and what have done, think about which element in the webpage will users operate with as the next target element to complete the task, where the element is located, and what is the corresponding operation.""",

    "referring_description": """Finally, conclude a single next step with a standardized summary using the format below. Ensure that every action is documented precisely, adhering to the definitions provided.\nFORMAT:""",

    "element_format": """ELEMENT: Please give the element your next action will be performed. Please do this by generating the label of the bounding box that covers the element you need to operate. If there is no valid element, please generate “NA”.""",

    "action_format": """ACTION: Choose an action from {CLICK, TYPE, SELECT}.""",

    "value_format": """VALUE: Provide additional input based on ACTION:\n\nThe VALUE means:\nIf ACTION == TYPE, specify the text to be typed.\nIf ACTION == SELECT, indicate the option to be chosen.\nIf ACTION == CLICK, write "None”."""
}

exp3_prompt_dict = {
    "system_prompt": """Imagine that you are imitating human doing web navigation for a task step by step. At each stage, you can see the webpage like human by a given screenshot, and know the previous actions that has done. You can click an element with the mouse, select an option, or type some texts with the keyboard.\n\nYou are asked to complete the following task: """,

    "question_description": """Below the screenshot is the webpage you see. Follow the following guidance to think step by step before clearly outlining the next action step at current stage that user would like to take(Not all the subsequent actions):\n\nFirstly, think about what is the current webpage.\n\nSecondly, look into details of the screenshot and the previous action history. Think about what have done by each of the previous actions and the intention of each of them one by one. Particularly, pay more attention to the last step, which has more information about what you should do now. When an action in previous action history is unclear, look into details of the screenshot to see what has been operated while not listed, in conjunction with human's web browsing habits, to understand what is that action and what have done at that step.\n\nThen, based on your analysis about the webpage and what have done, think about which element in the webpage will users operate with as the next target element to complete the task, where the element is located, and what is the corresponding operation.""",

    "referring_description": """Finally, conclude with a standardized summary using the format below. Ensure that every action is documented precisely, adhering to the definitions provided.\nFORMAT:""",

    "element_format": """ELEMENT: Please describe which element you need to operate with. Describe it as detailed as possible, including what it is and where it is.\n\nELEMENT TYPE: Please specify its type from these options: BUTTON, TEXTBOX, SELECTBOX, or LINK.\n\nELEMENT TEXT: Please provide the exact text displayed on the element. Do not invent or modify the text; reproduce it as-is from the screenshot.""",

    "action_format": """ACTION: Choose an action from {CLICK, TYPE, SELECT}.""",

    "value_format": """VALUE: Provide additional input based on ACTION:\nIf ACTION == TYPE, specify the text to be typed.\nIf ACTION == SELECT, indicate the option to be chosen.\nIf ACTION == CLICK, write "None"."""
}

exp4_prompt_dict = {
    "system_prompt": """Imagine that you are imitating human doing web navigation for a task step by step. At each stage, you can see the webpage like human by a given screenshot, and know the previous actions that has done. You can click an element with the mouse, select an option, or type some texts with the keyboard.\n\nYou are asked to complete the following task: """,

    "question_description": """Below the screenshot is the webpage you see. Follow the following guidance to think step by step before clearly outlining the next action step at current stage that user would like to take(Not all the subsequent actions):\n\nFirstly, think about what is the current webpage.\n\nSecondly, look into details of the screenshot and the previous action history. Think about what have done by each of the previous actions and the intention of each of them one by one. Particularly, pay more attention to the last step, which has more information about what you should do now. When an action in previous action history is unclear, look into details of the screenshot to see what has been operated while not listed, in conjunction with human's web browsing habits, to understand what is that action and what have done at that step.\n\nThen, based on your analysis about the webpage and what have done, think about which element in the webpage will users operate with as the next target element to complete the task, where the element is located, and what is the corresponding operation.""",

    "referring_description": """Firstly reiterate your target element and operation. \n\nThen think about this:\nyou will be given a multi-choice question, where the choices are elements(randomly selected) in the webpage . Find out where and what is each of them in the webpage from the screenshot. Then determine whether one of them matches the your target next element to operate with and make a choice. Check the choices one by one. If there are more than once choices match your answer, choose the most likely through your further reasoning.\nWhen identifying the target element, do not be distracted by the options in multiple-choice questions. If none of them certainly match your answer, do not guess or assume one of them is.\n\nFinally, conclude with a standardized summary using the format below. Ensure that every action is documented precisely, adhering to the definitions provided.\nFORMAT:""",

    "element_format": """ELEMENT: Choose one of the following elements if it matches the target element:""",

    "action_format": """ACTION: Choose an action from {CLICK, TYPE, SELECT}.""",

    "value_format": """VALUE: Provide additional input based on ACTION:\n\nThe VALUE means:\nIf ACTION == TYPE, specify the text to be typed.\nIf ACTION == SELECT, indicate the option to be chosen.\nIf ACTION == CLICK, write "None"."""
}


def retrieve_prompt(experiment_split):
    if experiment_split == 2:
        return exp2_prompt_dict
    elif experiment_split == 3:
        return  exp3_prompt_dict
    elif experiment_split == 4:
        return exp4_prompt_dict
    else:
        print("NO experiment split", experiment_split)

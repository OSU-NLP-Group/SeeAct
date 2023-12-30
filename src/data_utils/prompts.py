from .format_prompt_utils import data_format_input_multichoice, \
    format_options, generate_option_name, generate_new_referring_prompt, generate_new_query_prompt

sys_prompt = '''Imagine that you are imitating humans doing web navigation for a task step by step. At each stage, you can see the webpage like humans by a screenshot and know the previous actions before the current step decided by yourself through recorded history. You need to decide on the first following action to take. You can click an element with the mouse, select an option, or type text with the keyboard. (For your understanding, they are like the click(), select_option() and type() functions in playwright respectively) One next step means one operation within the three.'''

action_format = "ACTION: Choose an action from {CLICK, TYPE, SELECT}."

value_format = "VALUE: Provide additional input based on ACTION.\n\nThe VALUE means:\nIf ACTION == TYPE, specify the " \
               "text to be typed.\nIf ACTION == SELECT, specify the option to be chosen.\nIf ACTION == CLICK, " \
               "write \"None\"."

question_description_new_exp4 = '''The screenshot below shows the webpage you see. Follow the following guidance to think step by step before outlining the next action step at the current stage:

(Current Webpage Identification)
Firstly, think about what the current webpage is.

(Previous Action Analysis)
Secondly, combined with the screenshot, analyze each step of the previous action history and their intention one by one. Particularly, pay more attention to the last step, which may be more related to what you should do now as the next step.

(Screenshot Details Analysis)
Closely examine the screenshot to check the status of every part of the webpage to understand what you can operate with and what has been set or completed. You should closely examine the screenshot details to see what steps have been completed by previous actions even though you are given the textual previous actions. Because the textual history may not clearly and sufficiently record some effects of previous actions, you should closely evaluate the status of every part of the webpage to understand what you have done.

(Next Action Based on Webpage and Analysis)
Then, based on your analysis, in conjunction with human web browsing habits and the logic of web design, decide on the following action. And clearly outline which element in the webpage users will operate with as the first next target element, its detailed location, and the corresponding operation.

To be successful, it is important to follow the following rules: 
1. You should only issue a valid action given the current observation. 
2. You should only issue one action at a time'''

question_description_new_exp2 = '''The screenshot below shows the webpage you see. In the screenshot, some red bounding boxes and white-on-black uppercase letters at the bottom left corner of the bounding boxes have been manually added. You should ignore them for now. Follow the following guidance to think step by step before outlining the next action step at the current stage:

(Current Webpage Identification)
Firstly, think about what the current webpage is.

(Previous Action Analysis)
Secondly, combined with the screenshot, analyze each step of the previous action history and their intention one by one. Particularly, pay more attention to the last step, which may be more related to what you should do now as the next step.

(Screenshot Details Analysis)
Closely examine the screenshot to check the status of every part of the webpage to understand what you can operate with and what has been set or completed. You should closely examine the screenshot details to see what steps have been completed by previous actions even though you are given the textual previous actions. Because the textual history may not clearly and sufficiently record some effects of previous actions, you should closely evaluate the status of every part of the webpage to understand what you have done.

(Next Action Based on Webpage and Analysis)
Then, based on your analysis, in conjunction with human web browsing habits and the logic of web design, decide on the following action. And clearly outline which element in the webpage users will operate with as the first next target element, its detailed location, and the corresponding operation.

To be successful, it is important to follow the following rules: 
1. You should only issue a valid action given the current observation. 
2. You should only issue one action at a time.'''

question_description_new_exp3 = '''The screenshot below shows the webpage you see. Follow the following guidance to think step by step before outlining the next action step at the current stage:

(Current Webpage Identification)
Firstly, think about what the current webpage is.

(Previous Action Analysis)
Secondly, combined with the screenshot, analyze each step of the previous action history and their intention one by one. Particularly, pay more attention to the last step, which may be more related to what you should do now as the next step.

(Screenshot Details Analysis)
Closely examine the screenshot to check the status of every part of the webpage to understand what you can operate with and what has been set or completed. You should closely examine the screenshot details to see what steps have been completed by previous actions even though you are given the textual previous actions. Because the textual history may not clearly and sufficiently record some effects of previous actions, you should closely evaluate the status of every part of the webpage to understand what you have done.

(Next Action Based on Webpage and Analysis)
Then, based on your analysis, in conjunction with human web browsing habits and the logic of web design, decide on the following action. And clearly outline which element in the webpage users will operate with as the first next target element, its detailed location, and the corresponding operation. Please also closely examine the screenshot to adequately describe its position relative to nearby elements and its textual or visual content (if it has). If you find multiple elements similar to your target element, use a more precise description to ensure people can distinguish your target element from them through your answer.

To be successful, it is important to follow the following rules: 
1. You should only issue a valid action given the current observation. 
2. You should only issue one action at a time.'''

exp4_prompt_dict = {
    "system_prompt": sys_prompt,

    "question_description": question_description_new_exp4,

    "referring_description": f"""(Reiteration)
First, reiterate your next target element, its detailed location, and the corresponding operation.

(Multichoice Question)
Below is a multi-choice question, where the choices are elements in the webpage. From the screenshot, find out where and what each one is on the webpage. Then, determine whether one matches your target element. Please examine the choices one by one. Choose the matching one. If multiple options match your answer, choose the most likely one by re-examining the screenshot, the choices, and your further reasoning.""",

    "element_format": """(Final Answer)
Finally, conclude your answer using the format below. Ensure your answer is strictly adhering to the format provided below. Please do not leave any explanation in your answers of the final standardized format part, and this final part should be clear and certain. The element choice, action, and value should be in three separate lines.

Format:

ELEMENT: The uppercase letter of your choice.""",

    "action_format": f"{action_format}",

    "value_format": f"{value_format}"
}

exp2_prompt_dict = {
    "system_prompt": sys_prompt,

    "question_description": question_description_new_exp2,

    "referring_description": f"""(Reiteration)
First, reiterate your next target element, its detailed location, and the corresponding operation.

(Verification with the Screenshot)
Then, please closely re-examine the screenshot to find whether your target element is marked by a red bounding box and has a white uppercase letter on a black background at the bottom left corner of the bounding box, which is positioned closely next to the bounding box. If yes, use that letter for your final answer. If not, please do not make them up. If it is not marked, please output "NA" as your target element in the following final answer part.""",

    "element_format": """(Final Answer)
Finally, conclude your answer using the format below. Ensure your answer is strictly adhering to the format provided below. Please do not leave any explanation in your answers of the final standardized format part, and this final part should be clear and certain. The element choice, action, and value should be in three separate lines.

Format:

ELEMENT: The uppercase letter of your choice.""",

    "action_format": f"{action_format}",

    "value_format": f"{value_format}"
}

exp3_prompt_dict = {
    "system_prompt": sys_prompt,

    "question_description": question_description_new_exp3,

    "referring_description": f"""""",

    "element_format": """(Final Answer)
Finally, conclude your answer using the format below. Ensure your answer is strictly adhering to the format provided below. Please do not leave any explanation in your answers of the final standardized format part, and this final part should be clear and certain. The element, element type, element text, action and value should be in five separate lines.

Format:

ELEMENT: Please describe which element you need to operate with. Describe it as detailed as possible, including what it is and where it is.

ELEMENT TYPE: Please specify its type from these options: BUTTON, TEXTBOX, SELECTBOX, or LINK.

ELEMENT TEXT: Please provide the exact text displayed on the element. Do not invent or modify the text; reproduce it as-is from the screenshot.""",

    "action_format": f"{action_format}",

    "value_format": f"{value_format}"
}


def generate_prompt(experiment_split, task=None, previous=None, choices=None):
    assert experiment_split != None, "Please specify the experiment split."
    assert task != None, "Please input the task."
    assert previous != None, "Please input the previous actions."

    prompt_list = []
    system_prompt_input = None
    question_description_input = None
    referring_input = None
    element_format_input = None
    action_format_input = None
    value_format_input = None

    if experiment_split in ["4api"]:
        system_prompt_input = exp4_prompt_dict["system_prompt"]
        question_description_input = exp4_prompt_dict["question_description"]
        referring_input = exp4_prompt_dict["referring_description"]
        element_format_input = exp4_prompt_dict["element_format"]
        action_format_input = exp4_prompt_dict["action_format"]
        value_format_input = exp4_prompt_dict["value_format"]

        prompt_list.extend(
            generate_new_query_prompt(system_prompt=system_prompt_input, task=task, previous_actions=previous,
                                      question_description=question_description_input))
        prompt_list.append(
            generate_new_referring_prompt(referring_description=referring_input, element_format=element_format_input,
                                          action_format=action_format_input, value_format=value_format_input,
                                          choices=choices))
        return prompt_list

    elif experiment_split in ["3api"]:
        system_prompt_input = exp3_prompt_dict["system_prompt"]
        question_description_input = exp3_prompt_dict["question_description"]
        referring_input = exp3_prompt_dict["referring_description"]
        element_format_input = exp3_prompt_dict["element_format"]
        action_format_input = exp3_prompt_dict["action_format"]
        value_format_input = exp3_prompt_dict["value_format"]

        prompt_list.extend(
            generate_new_query_prompt(system_prompt=system_prompt_input, task=task, previous_actions=previous,
                                      question_description=question_description_input))
        prompt_list.append(
            generate_new_referring_prompt(referring_description=referring_input, element_format=element_format_input,
                                          action_format=action_format_input, value_format=value_format_input,
                                          split="3api"
                                          ))
        return prompt_list

    elif experiment_split in ["2api"]:
        system_prompt_input = exp2_prompt_dict["system_prompt"]
        question_description_input = exp2_prompt_dict["question_description"]
        referring_input = exp2_prompt_dict["referring_description"]
        element_format_input = exp2_prompt_dict["element_format"]
        action_format_input = exp2_prompt_dict["action_format"]
        value_format_input = exp2_prompt_dict["value_format"]

        prompt_list.extend(
            generate_new_query_prompt(system_prompt=system_prompt_input, task=task, previous_actions=previous,
                                      question_description=question_description_input))
        prompt_list.append(
            generate_new_referring_prompt(referring_description=referring_input, element_format=element_format_input,
                                          action_format=action_format_input, value_format=value_format_input,
                                          choices=None))
        return prompt_list

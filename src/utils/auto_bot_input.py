
import os

def get_question_input():
    """
    Read autobot input template file and return the content of the template
    """
    if not os.path.exists(file_path):
        raise Exception("auto bot template file does not exist")

    question_input = None
    with open("autobot_input_template.txt", "r+") as file:
        question_input = file.read()
    return question_input

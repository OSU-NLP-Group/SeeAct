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

import json
import os
import jsonlines
import base64
import numpy as np
import cv2
import copy
from tqdm import tqdm
import argparse
import supervision as sv
import torch
import pickle as pkl

from src.data_utils.image_utils import convert_elements2detections
from src.data_utils.image_utils import extract_topk_elements, extract_elements_by_ids
from src.data_utils.image_utils import batch_elements_by_locality, batch_elements_by_locality_16_16_17
from src.data_utils.format_prompt_utils import data_format_input_multichoice

def run(args):

    with open(args.selected_set_task_id_path, 'rb') as f:
        selected_set_task_id_dict = pkl.load(f)

    selected_task_ids = selected_set_task_id_dict[args.split]

    # Path to the raw_dump containing screenshot source data
    screenshot_dump_path = args.screenshot_dump_path

    # Set the image output directory
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Path to dumped query data (Taken from Mind2Web experiment sample before sending into LLM inference)
    query_source_path = args.query_source_path
    with open(query_source_path, 'r') as f:
        all_queries = json.load(f)

    # Enumerate each task in query data and generate screenshots
    for i, task in tqdm(enumerate(all_queries)):
        if len(task) == 2:
            continue
        task_action_id = task[0]
        task_id, action_id = task_action_id.strip().split("_")
        if task_id not in selected_task_ids:
            continue

        # Load Image source data
        single_screenshot_path = os.path.join(screenshot_dump_path, task_id, "processed/screenshot.json")
        if os.path.exists(single_screenshot_path):
            with open(single_screenshot_path) as f:
                scrshots_task = json.load(f)
        else:
            print("No Folder: ", single_screenshot_path)
            continue

        # Output Path
        task_dir = os.path.join(output_dir, task_action_id)
        if not os.path.exists(task_dir):
            os.mkdir(task_dir)

        image_dir = os.path.join(output_dir, task_action_id, "images")
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)

        actid2scrshots_task = {}
        for scrshot in scrshots_task:
            tsd_act_uid = scrshot["action_uid"]
            actid2scrshots_task[tsd_act_uid] = scrshot
        scrshot = actid2scrshots_task[action_id]

        inference_batches = task[1]
        sample = task[2]

        # Prepare Image
        bef_tsd = scrshot["before"]["screenshot"]
        bef_tsd = np.frombuffer(base64.b64decode(bef_tsd), np.uint8)
        bef_img = cv2.imdecode(bef_tsd, cv2.IMREAD_COLOR)

        # Collect all elements
        all_elements = []
        positive_elements = sample['pos_candidates']
        negative_elements = sample['neg_candidates']
        all_elements.extend(positive_elements)
        all_elements.extend(negative_elements)

        # Prepare top-50 elements and batch into 3 batches with 20 choices
        top_50_elements = extract_topk_elements(all_elements, k=50)
        if args.num_choice == -1:
            choice_batches = batch_elements_by_locality_16_16_17(top_50_elements)
        else:
            choice_batches = batch_elements_by_locality(top_50_elements, num_choices=args.num_choice)


        to_run = []
        for batch_idx, candidate_elements in enumerate(choice_batches):
            temp = copy.deepcopy(sample)

            # Prepare question, choices, etc.
            candidate_element_ids = [item['backend_node_id'] for item in candidate_elements]
            seq_context, seq_in, _, choices, node_to_keep = data_format_input_multichoice(
                temp, candidate_element_ids, -1, keep_html_brackets=True
            )
            temp['context_html'] = seq_context
            temp['context_node_ids'] = copy.deepcopy(list(node_to_keep))
            temp['question'] = seq_in
            # Reorder Choices
            temp['choices'] = choices
            temp['image_path'] = os.path.join("", task_action_id, "images")

            # Choices will be reordered after data_format_input_multichoice, need to reorder candidate_element_ids
            # Align candidate_element_ids with choices
            candidate_element_ids = [item[0] for item in choices]
            # Align candidate_elements with choices
            candidate_elements = extract_elements_by_ids(all_elements, ids=candidate_element_ids)

            # Prepare Images
            candidate_detections = convert_elements2detections(candidate_elements)
            candidate_labels = [chr(i+65) for i in range(len(candidate_detections))]

            annotated_image = bef_img.copy()
            # Cropping
            annotated_image = sv.crop_image(image=annotated_image, xyxy=np.array(
                [
                    0,
                    max(0, min(candidate_detections.xyxy[:, 1])-1024),
                    annotated_image.shape[1],
                    min(annotated_image.shape[0], max(candidate_detections.xyxy[:, 3])+1024)
                ]
            ))
            bef_fn = os.path.join(image_dir, "{}.jpg".format(batch_idx))
            try:
                cv2.imwrite(bef_fn, annotated_image)
            except:
                continue
            to_run.append(temp)
        pred_path = os.path.join(task_dir, "queries.jsonl")
        with jsonlines.open(pred_path, mode='w') as writer:
            writer.write_all(to_run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_choice', type=int, default=-1)
    parser.add_argument('--split', type=str, default="test_website")
    parser.add_argument('--selected_set_task_id_path', type=str, default="../data/seeact_source_data/30_selected.pkl")
    parser.add_argument('--screenshot_dump_path', type=str, default="../data/screenshot_source/")
    parser.add_argument('--output_dir', type=str, default="../data/30_selected_tasks/exp4_whole")
    parser.add_argument('--query_source_path', type=str,
                        default="../data/seeact_source_data/test_website_outputs_top50.json")
    my_args = parser.parse_args()
    run(my_args)









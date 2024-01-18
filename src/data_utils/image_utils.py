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


import supervision as sv
import torch
import json
import copy

def convert_elements2detections(candidate_elements):
    """
    Extract element coordinates
    Parse candidate elements coordinates and convert into sv Detection objects
    """
    boxes = []
    for box_id, element in enumerate(candidate_elements):
        bounding_box_rect = json.loads(element['attributes'])['bounding_box_rect'].strip().split(',')
        x1 = float(bounding_box_rect[0])
        y1 = float(bounding_box_rect[1])
        w = float(bounding_box_rect[2])
        h = float(bounding_box_rect[3])
        boxes.append([x1, y1, x1 + w, y1 + h])
    # Format bounding box into transformers output format to convert into supervision detection
    transformer_results = {
        "boxes": torch.tensor(boxes),
        "scores": torch.tensor([0.5 for item in boxes]),
        "labels": torch.tensor([1 for item in boxes])
    }
    detections = sv.Detections.from_transformers(transformer_results)
    return detections


def extract_topk_elements(all_elements, k):
    topk_elements = []
    for element in all_elements:
        rank = element['rank']
        score = element['score']
        if rank < k:
            topk_elements.append(copy.deepcopy(element))
    return topk_elements


def extract_elements_by_ids(all_elements, ids):
    """
    Extract elements specified by the list of element_id
    To prevent order change, we will keep the return element the same order as the ids input
    """
    output = []
    for element in all_elements:
        element_id = element['backend_node_id']
        if element_id in ids:
            output.append(element)

    # Order output element to be identical with ids input
    element_dict = {}
    for element in all_elements:
        element_id = element['backend_node_id']
        element_dict[element_id] = element
    ordered_output = []
    for element_id in ids:
        ordered_output.append(element_dict[element_id])

    return ordered_output


def batch_elements_by_locality(elements, num_choices):
    # Sort elements by y1 location (ascending order)
    sorted_elements = sorted(elements, key=lambda x: float(
        json.loads(x['attributes'])['bounding_box_rect'].strip().split(',')[1]))

    batches = []
    while len(sorted_elements) > 1:
        batch = sorted_elements[: num_choices]
        sorted_elements = sorted_elements[num_choices:]
        batches.append(batch)

    return batches

def batch_elements_by_locality_16_16_17(elements):
    # Sort elements by y1 location (ascending order)
    sorted_elements = sorted(elements, key=lambda x: float(
        json.loads(x['attributes'])['bounding_box_rect'].strip().split(',')[1]))

    batches = []
    # First batch: 16
    batch = sorted_elements[: 16]
    sorted_elements = sorted_elements[16:]
    batches.append(batch)

    # Second batch: 17
    batch = sorted_elements[: 17]
    sorted_elements = sorted_elements[17:]
    batches.append(batch)

    # Third batch: 17
    batch = sorted_elements[: 17]
    sorted_elements = sorted_elements[17:]
    batches.append(batch)

    return batches


def split_elements_by_locality_final_round(elements):
    # Sort elements by y1 location (ascending order)
    sorted_elements = sorted(elements, key=lambda x: float(
        json.loads(x['attributes'])['bounding_box_rect'].strip().split(',')[1]))

    y1_axis = [float(json.loads(item['attributes'])['bounding_box_rect'].strip().split(',')[1]) for item in sorted_elements]
    batches = []
    window_elements = []
    for idx in range(len(y1_axis)):
        if not window_elements:
            window_elements.append(y1_axis[idx])
            continue
        else:
            current_y = y1_axis[idx]
            if current_y - window_elements[-1]<2000:
                window_elements.append(current_y)
            else:
                batches.append(window_elements)
                window_elements = [current_y]
    batches.append(window_elements)

    cropping_locations = []
    idx = 0
    for item in batches:
        cropping_locations.append([idx, idx+len(item)])
        idx += len(item)
    return cropping_locations


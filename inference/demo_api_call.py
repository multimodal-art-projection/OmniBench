import pandas as pd
# import base64
# import requests
import os
import json
import tqdm
import argparse
import re
from tqdm import tqdm
from inference.models.closed_source_model import GPT4oInferencer, Claude35Inferencer, GPT4VInference, \
            Gemini15ProInference, GPT4TurboInference, GPT4oMiniInference, GPT35turboInference, GPT4o_0806_Inferencer, GPT4TurboVisionInference, RekaInferencer
from answer_parsing import parse_multi_choice_response
from multiprocessing import Pool



def split_string_by_options(input_string):
    pattern = r'(A\..*?)(B\..*?)(C\..*?)(D\..*)'
    matches = re.findall(pattern, input_string, re.DOTALL)
    return [match.strip() for match in matches[0]]


def load_existing_outputs(output_file):
    """ Load existing outputs from the specified output JSON file. """
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_results = [json.loads(line) for line in f]
        return {result["index"] for result in existing_results}
    return set()


# Factory function to create inferencers based on model name
def create_inferencer(model_name):
    inferencer_classes = {
        'gpt4o': GPT4oInferencer,
        'gpt4o0806': GPT4o_0806_Inferencer,
        'claude35': Claude35Inferencer,
        'gpt4v': GPT4VInference,
        'gemini_15_pro': Gemini15ProInference,
        'gpt4turbo': GPT4TurboInference,
        'gpt3': GPT35turboInference,
        'gpt4omini': GPT4oMiniInference,
        'gpt4turbovision': GPT4TurboVisionInference,
        "reka": RekaInferencer,
        # Add more model inferencer mappings here
    }
    return inferencer_classes[model_name]()


def create_prompt(args, question, options, audio_transcript, image_caption):
    # assert not args.no_image or not args.no_audio
    if not args.audio_transcript and not args.image_caption and not args.no_image and not args.no_audio:
        prompt = f"Please answer the following question based on the given image and audio:\n{question}.\nPlease choose only one answer from the following options:\n{options}."
    elif not args.audio_transcript and not args.image_caption and args.no_image and not args.no_audio:
        prompt = f"Please answer the following question based on the given audio:\n{question}.\nPlease choose only one answer from the following options:\n{options}."
    elif not args.audio_transcript and not args.image_caption and not args.no_image and args.no_audio:
        prompt = f"Please answer the following question based on the given image:\n{question}.\nPlease choose only one answer from the following options:\n{options}."
    elif not args.audio_transcript and args.image_caption and not args.no_image and not args.no_audio:
        prompt = f"Please answer the following question based on the given caption of an image and an audio:\n{image_caption} {question}.\nPlease choose only one answer from the following options:\n{options}."
    elif args.audio_transcript and not args.image_caption and not args.no_image and not args.no_audio:
        prompt = f"Please answer the following question based on the given an image and transcript of an audio:\n{audio_transcript} {question}.\nPlease choose only one answer from the following options:\n{options}."
    elif args.audio_transcript and args.image_caption and not args.no_image and not args.no_audio:
        prompt = f"Please answer the following question based on the given caption of an image and transcript of an audio:{audio_transcript} \n{image_caption} {question}.\nPlease choose only one answer from the following options:\n{options}."
    elif args.image_caption and not args.no_image and args.no_audio:
        prompt = f"Please answer the following question based on the given caption of an image:\n{image_caption} {question}.\nPlease choose only one answer from the following options:\n{options}."
    elif args.audio_transcript and args.no_image and not args.no_audio:
        prompt = f"Please answer the following question based on the given transcript of an audio:\n{audio_transcript} {question}.\nPlease choose only one answer from the following options:\n{options}."
    else:
        raise NotImplementedError
    return prompt

def process_row(args_list):

    row, index, args, index2ans, all_choices = args_list
    inferencer = create_inferencer(args.model_name_or_path)
    if args.model_name_or_path in ['gemini_official', 'reka']:
        inferencer.load_model()
    question = row['question']
    options = row['option']
    audio_transcript = f"Audio Content: {row['audio content']}" if args.audio_transcript else ""
    image_caption = f"Image Content: {row['image content']}" if args.image_caption else ""
    
    prompt = create_prompt(args, question, options, audio_transcript, image_caption) 
    
    response = None
    image_path = row['image_path']
    audio_path = row['audio_path']


    if args.model_name_or_path not in ["gemini_15_pro", "reka"]:
        if args.no_image and not args.image_caption:
            response = inferencer.infer('', prompt, 'Null', 0)
        else:
            response = inferencer.infer('', prompt, image_path, 0)
    else:
        #you should convert audio_path and 
        if args.no_image or args.image_caption:
            response = inferencer.infer('', prompt, None, audio_path, 0)
        else:
            response = inferencer.infer('', prompt, image_path, audio_path, 0)

    if not response:
        return None
    
    parsed_response = parse_multi_choice_response(response, all_choices, index2ans)
    correct_answer = parse_multi_choice_response(row['correct answer'], all_choices, index2ans)

    results_dict = {
        "index": index,
        "audio_type": row['audio type'], 
        "question": question,
        "options": options,
        "response": response,
        "parsed_response": parsed_response,
        "correct_answer": correct_answer,
        "is_correct": parsed_response == correct_answer
    }
    # Directly write results to the output JSON file
    with open(args.output_file, "a") as output_review_file:
        output_review_file.write(json.dumps(results_dict, ensure_ascii=False) + "\n")

    return results_dict
    

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name-or-path", choices=['', 'gpt4o', 'claude35', 
                                                 'gpt4v', 'gemini_15_pro', 
                                                 'gpt4omini', 'gpt4o0806', 'gpt4turbovision', "reka"], type=str, default="gpt4turbovision")
    parser.add_argument("--no-image", action="store_true")
    parser.add_argument("--no-audio", action="store_true")
    parser.add_argument("--audio-transcript", action="store_true")
    parser.add_argument("--image-caption", action="store_true")
    parser.add_argument('--input-file', default="batch-5_1142_20240817.xlsx", type=str, help='api base url')
    parser.add_argument('--output-file', default="results/UnifiedIO2_large/batch-5_1142_20240817.json", type=str, help='the path to save the output json file')

    args = parser.parse_args()

    model_name = args.model_name_or_path

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    
    p = args.input_file  
    tmp_path = f'{args.output_file}.temp_result.pickle'
    df = pd.read_excel(p)
    df['image_path'] = df['image_path'].apply(lambda x: f'mm_data/image/{x}') 
    df['audio_path'] = df['audio_path'].apply(lambda x: f'mm_data/audio/{x}')    
    processed_indices = load_existing_outputs(args.output_file)  # Load existing results

    if os.path.exists(tmp_path):
        results = pd.read_pickle(tmp_path)
        print(f'Loaded cache result from {tmp_path}')
    else:
        results = [None for _ in range(df.shape[0])]

    all_choices = ['A', 'B', 'C', 'D']
    

    # Prepare for multiprocessing
    args_list = []
    for index in range(df.shape[0]):
        options = df.loc[index, 'option']
        all_options = split_string_by_options(options)
        if index not in processed_indices:  # Check if the index has already been processed
            index2ans = {chr(ord("A") + i): "" for i in range(4)}
            for j in range(len(all_choices)):
               index2ans[all_choices[j]] = all_options[j].replace(f"{all_choices[j]}.", "").strip()
            args_list.append((df.loc[index], index, args, index2ans, all_choices))


    with Pool(processes=12) as pool:  # You can adjust the number of processes as needed
        results = list(tqdm(pool.imap(process_row, args_list), total=len(args_list)))

    # Calculate accuracy
    correct_count = sum(result['is_correct'] for result in results if result)
    accuracy = correct_count / len(results)
    print(f"{args.output_file} Accuracy: {accuracy:.4f}, {correct_count}/{len(results)}")


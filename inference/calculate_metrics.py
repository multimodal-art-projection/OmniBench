import json
import argparse
import sys
sys.path.append("./inference")

from answer_parsing import parse_multi_choice_response

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', default="dataset/batch-5_1142_20240817.jsonl", type=str, help='the original file')
    parser.add_argument('--inference-file', default="inference_output.json", type=str, help='the output from models')
    args = parser.parse_args()

    # load jsonl file with json
    with open(args.input_file, 'r') as f:
        data = f.readlines()
    data = [json.loads(line.strip()) for line in data]

    with open(args.inference_file, 'r') as f:
        results = json.load(f)

    n_correct_response = 0
    n_invalid_response = 0
    n_wrong_response = 0
    stats_by_audio_type = {
        "music": {
            "n_correct_response": 0,
            "n_invalid_response": 0,
            "n_wrong_response": 0,
        },
        "speech": {
            "n_correct_response": 0,
            "n_invalid_response": 0,
            "n_wrong_response": 0,
        },
        "sound event": {
            "n_correct_response": 0,
            "n_invalid_response": 0,
            "n_wrong_response": 0,
        },
    }
    n_audio_type = {
        "music": 0,
        "speech": 0,
        "sound event": 0,
    }
    # for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
    for index, row in enumerate(data):
        question = row['question']
        audio_type = row['audio type'].strip().lower()
        n_audio_type[audio_type] += 1

        if results[index]['question'] == "":
            n_invalid_response += 1
            stats_by_audio_type[audio_type]['n_invalid_response'] += 1
            continue

        options = row["options"]
        all_choices = []
        index2ans = {}

        for i in range(4):
            current_option = chr(ord("A") + i)
            index2ans[current_option] = options[i]
            all_choices.append(current_option)
        
        response = results[index]['response']

        parsed_response = parse_multi_choice_response(response, options, index2ans, default_answer='N/A')
        correct_answer = parse_multi_choice_response(row['answer'], all_choices, index2ans, default_answer='N/A')
        
        assert correct_answer != 'N/A', f"Correct answer is not found in question {index} the options: {row['correct answer']}"
        # if parsed_response == 'N/A':
        #     n_invalid_response += 1
        #     stats_by_audio_type[audio_type]['n_invalid_response'] += 1
        #     continue
        if results[index]["is_correct"]: #parsed_response == correct_answer:
            n_correct_response += 1
            stats_by_audio_type[audio_type]['n_correct_response'] += 1
        else:
            n_wrong_response += 1
            stats_by_audio_type[audio_type]['n_wrong_response'] += 1
    print("="*40)
    print(f'Total number of questions: {len(data)}')
    print(f"Correct response: {n_correct_response}; Invalid response: {n_invalid_response}, Wrong response: {n_wrong_response}")
    print(f"{args.inference_file}\nAccuracy, Invalid Rate")
    print(f"{n_correct_response/len(data):.4f}, {n_invalid_response/len(data):.4f}")
    print("Stats by audio type:")
    for audio_type, stats in stats_by_audio_type.items():
        print(f"{audio_type} total: {n_audio_type[audio_type]}")
        print('Correct, Invalid, Wrong Response Rate:')
        print(f"{audio_type}: {stats['n_correct_response']/n_audio_type[audio_type]:.4f}, {stats['n_invalid_response']/n_audio_type[audio_type]:.4f}, {stats['n_wrong_response']/n_audio_type[audio_type]:.4f}")
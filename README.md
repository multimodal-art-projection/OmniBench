# OmniBench

[**🌐 Homepage**](https://m-a-p.ai/OmniBench/) | [**🏆 Leaderboard**](https://m-a-p.ai/OmniBench/#leaderboard) | [**📖 Arxiv Paper**](https://arxiv.org/) | [**🤗 Dataset**](https://huggingface.co/datasets/m-a-p/OmniBench)

The project introduces **OmniBench**, a novel benchmark designed to rigorously evaluate models' ability to recognize, interpret, and reason across **visual**, **acoustic**, and **textual** inputs simultaneously. We define models capable of such tri-modal processing as omni-language models (OLMs).

## Mini Leaderboard

This table shows the omni-language models in the full evaluation setting in OmniBench, with the "Image & Audio", "Audio", and "Image" as input contexts and accuracy as metric. More results could be found at the [live leaderboard](https://m-a-p.ai/OmniBench/#leaderboard).

| **Input Context**   | **Image & Audio**    | **Audio**           | **Image**           |
|---------------------|----------------------|---------------------|---------------------|
| MIO-SFT (13B)       | 11.12%               | 11.82%              | 13.57%              |
| AnyGPT (7B)         | 2.71%                | 2.36%               | 1.23%               |
| video-SALMONN (13B) | 11.30%               | 11.56%              | 11.38%              |
| UnifiedIO2-large (1.1B) | 22.68%           | 24.69%              | 24.52%              |
| UnifiedIO2-xlarge (3.2B) | 20.40%          | 24.78%              | 24.34%              |
| UnifiedIO2-xxlarge (6.8B) | 23.29%         | 27.06%              | 25.04%              |
| Gemini-1.5-Pro      | 47.56%               | 38.53%              | 34.68%              |
| Reka-core-20240501  | 36.10%               | 35.07%              | 34.39%              |

## Inference

### Evaluation Example with OpenAI Style API Call

```shell
python inference/demo_api_call.py --output-file your_model_inference_output.json
```

Run the ablation setting without image (audio+text) or without audio (image+text).
```shell
python inference/demo_api_call.py --no-image --output-file your_model_inference_output.no-image.json
python inference/demo_api_call.py --no-audio --output-file your_model_inference_output.no-image.json
```

### Parsing and Evaluation

```shell
python inference/calculate_metrics.py --input-file dataset/batch-5_1142_20240817.jsonl --inference-file your_model_inference_output.jsonl
```

## Dataset

The dataset consists of the following keys:
- `"index"`: an integer suggests the question id.
- `"task type"`: a string suggests one of the 7 task types.
- `"audio type"`: a string suggests one of the 3 audio types (speech, sound event and music).
- `"question"`: a string suggests the question.
- `"options"`: a list of four strings for multi-choice questions.
- `"answer"`: a string suggesting the correct response, must appear in `"options"`.
- `"audio_path"`: the basename of the audio file, need to prepend `mm_data/audio` before using.
- `"image_path"`: the basename of the image file, need to prepend `mm_data/image` before using.
- `"audio"` (for HF version only): contains the numpy array for the wavfile.
- `"image"` (for HF version only): contains the `PIL.Image()` object for the image.
- `"audio content"`: the human-annotated audio transcripts, used in text alternative experiments.
- `"image content"`: the VLM-generated caption for the image, used in text alternative experiments.

### Download from Huggingface

```python
from datasets import load_dataset

dataset = load_dataset("m-a-p/OmniBench")

# check on the data samples
print(dataset)
print(dataset['train'][0])
```

### Download from Github

The local version data is placed at `dataset/batch-5_1142_20240817.jsonl`. You will need to use `git lfs` to pull the folder `mm_data` for the images and audios.

## Reference

```bib
TBD
```
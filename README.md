# OmniBench

[**🌐 Homepage**](https://m-a-p.ai/OmniBench/) | [**🏆 Leaderboard**](https://m-a-p.ai/OmniBench/#leaderboard) | [**📖 Arxiv Paper**](https://arxiv.org/)

The project introduces **OmniBench**, a novel benchmark designed to rigorously evaluate models' ability to recognize, interpret, and reason across **visual**, **acoustic**, and **textual** inputs simultaneously. We define models capable of such tri-modal processing as omni-language models (OLMs).

## Mini Leaderboard

This table shows the omni-language models in the full evaluation setting in OmniBench, with the "Image & Audio", "Audio", and "Image" as input contexts and accuracy as metric. 
More results could be found at the [live leaderboard](https://m-a-p.ai/OmniBench/#leaderboard).

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


## Dataset

The data is placed at `dataset/batch-5_1142_20240817.jsonl`, with the following keys:
- `"index"`: an integer suggests the question id.
- `"task type"`: a string suggests one of the 7 task types.
- `"audio type"`: a string suggests one of the 3 audio types (speech, sound event and music).
- `"question"`: a string suggests the question.
- `"options"`: a list of four strings for multi-choice questions.
- `"answer"`: a string suggesting the correct response, must appear in `"options"`.
- `"audio_path"`: the basename of the audio file, need to prepend `mm_data/audio` before using.
- `"image_path"`: the basename of the image file, need to prepend `mm_data/image` before using.
- `"audio content"`: the human-annotated audio transcripts, used in text alternative experiments.
- `"image content"`: the VLM-generated caption for the image, used in text alternative experiments.

## Reference

```bib
TBD
```
# OmniBench

[**🌐 Homepage**](https://m-a-p.ai/OmniBench/) | [**🏆 Leaderboard**](https://m-a-p.ai/OmniBench/#leaderboard) | [**📖 Arxiv Paper**](https://arxiv.org/)

The project introduces **OmniBench**, a novel benchmark designed to rigorously evaluate models' ability to recognize, interpret, and reason across **visual**, **acoustic**, and **textual** inputs simultaneously. We define models capable of such tri-modal processing as omni-language models (OLMs).


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
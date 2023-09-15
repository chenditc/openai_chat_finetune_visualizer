# Prepare Finetune Data

## Dump Data from openai api
Record the messages and save it to finetune_data.jsonl

Format see: https://platform.openai.com/docs/guides/fine-tuning/example-format

## Validate finetune data
`python finetune_data_validation.py --data_path ./finetune_data.jsonl `

This is improved from Open AI jupyter notebook: https://github.com/openai/openai-cookbook/blob/main/examples/Chat_finetuning_data_prep.ipynb

## Manually improve finetune data
If you want to improve your finetune data by manually change some text, you can use the Gradio-based UI:
`python visualize_finetune_data.py`

## Convert the finetune data to openai eval format
If you plan to use https://github.com/openai/evals/tree/main to evaluate your finetune result, you can convert the finetune data to eval format using:
`python convert_finetune_data_to_eval_format.py --finetune_data_path ./finetune_data.jsonl --eval_file_path eval.jsonl`
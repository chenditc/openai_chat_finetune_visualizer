# Prepare Finetune Data
To prepare for finetune, we need:
1. Collect data for finetune
2. Prepare the data for the finetune format, manually label / change data if needed.
3. Evaluate the perf of different base model on this data

I build sevaral scripts for this purpose.

## Dump Data from openai api
The simplest way to collect data for finetune is to use GPT4 as our labeler, use the GPT4's response as our baseline and manually improve on it.

To record the messages and save it to finetune_data.jsonl, format see: https://platform.openai.com/docs/guides/fine-tuning/example-format

You can use this wrapper function to call openai:
```
def record_gpt_input_output(input_messages, response, prompt_type, output_dir="gpt_output"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"{prompt_type}.jsonl"
    output_message = {"messages": input_messages + [{"role": "assistant", "content": response}]}
    with open(output_file, "a") as f:
        print(f"Wrting to {output_file}")
        f.write(json.dumps(output_message) + "\n")

def run_gpt_response(input_prompt, 
                     examples, 
                     max_token,
                     prompt_type=None):
    final_input = [{
        "role":"user",
        "content": input_prompt
    }]

    openai.api_type = "azure"
    openai.api_base = GPT_API_BASE
    openai.api_version = "2023-03-15-preview"
    openai.api_key = AZURE_OPENAI_API_KEY

    gpt_input = [{"role":"system","content":system_prompt}] + examples + final_input

    response = openai.ChatCompletion.create(
        engine=GPT_ENGINE,
        messages = gpt_input,
        temperature=0.1,
        max_tokens=max_token,
        top_p=1,
        stream=True,
        stop=None)

    full_response = collect_gpt_response(response)

    if prompt_type is not None:
        record_gpt_input_output(gpt_input, full_response, prompt_type)

    return full_response
```

## Validate finetune data
`python finetune_data_validation.py --data_path ./finetune_data.jsonl `

This is improved from Open AI jupyter notebook: https://github.com/openai/openai-cookbook/blob/main/examples/Chat_finetuning_data_prep.ipynb

## Manually improve finetune data
If you want to improve your finetune data by manually change some text, you can use the Gradio-based UI:
`python visualize_finetune_data.py`

## Convert the finetune data to openai eval format
If you plan to use https://github.com/openai/evals/tree/main to evaluate your finetune result, you can convert the finetune data to eval format using:
`python convert_finetune_data_to_eval_format.py --finetune_data_path ./finetune_data.jsonl --eval_file_path eval.jsonl`
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
```python
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

You can change both the prompt and the response, and click save to save it back to jsonl file.

![image](https://github.com/chenditc/openai_chat_gpt_finetune_tools/assets/3244845/1dde2a9f-4386-4ef2-83a5-bbc7df9ad54b)


## Convert the finetune data to openai eval format
If you plan to use https://github.com/openai/evals/tree/main to evaluate your finetune result, you can convert the finetune data to eval format using:
`python convert_finetune_data_to_eval_format.py --finetune_data_path ./finetune_data.jsonl --eval_file_path eval.jsonl`

## Use OpenAI eval to evaluate the data for different format
1. Install Open AI evals follow https://github.com/openai/evals/blob/main/README.md#Setup
2. prepare local registry:
```bash
mkdir registry
mkdir registry/evals
mkdir registry/data
mkdir registry/modelgraded/
```
3. Put your data under `registry/data`
```bash
# For example, my use case is error categorization.
mkdir registry/data/error_categorization
mv eval.jsonl registry/data/error_categorization/samples.jsonl
```
4. Put your model graded evaluation config in `registry/modelgraded`
5. Put your eval config config in `registry/evals`
6. Run the eval for one example to rule out any config issue:
```bash
oaieval gpt-3.5-turbo-16k error_categorization --registry ./registry --max_samples 1 --debug
```
7. Run the eval for different model and save the evaluation result for future comparision.

## Implement different Lang Chain completion function to use for eval
### Azure Open AI
See example in `registry/completion_fns/langchain_llms.yaml`, to use Azure Open AI completion fn, you also need to set the endpoint and apikey as environment variable.
DO NOT CHECK IN YOUR APIKEY!

```bash
export OPENAI_API_BASE="https://xxxx.openai.azure.com/"
export OPENAI_API_KEY=xxxx
```

To use Azure open ai model to evaluate, change the completion function to the new name:
```
oaieval azure-gpt-4-32k error_categorization --registry ./registry --max_samples 1 --debug
```

### LLAMA2

## Sample using one model and evaluate using another model
You can use one completion function to sample the response from LLM and then evaluate the result using another model. You will need to pass in two completion function, [the first one will be use as the sampling function](https://github.com/openai/evals/blob/bd3b4d0afa7785f0374c46c32a32dd4c55105c28/evals/eval.py#L78), [the last one will be use as model graded function](https://github.com/openai/evals/blob/bd3b4d0afa7785f0374c46c32a32dd4c55105c28/evals/elsuite/modelgraded/classify.py#L29)

```
oaieval azure-gpt-35-16k,azure-gpt-4-32k error_categorization --registry ./registry --max_samples 1 --debug
```

## Eval Result
Use azure gpt4 0613 for evalution. Here are results:

1. azure gpt 3.5 16k 0613
[2023-09-16 12:29:03,763] [oaieval.py:239] Final report:
[2023-09-16 12:29:03,764] [oaieval.py:241] counts/SCORE8: 16
[2023-09-16 12:29:03,764] [oaieval.py:241] counts/SCORE10: 63
[2023-09-16 12:29:03,764] [oaieval.py:241] counts/SCORE0: 29
[2023-09-16 12:29:03,764] [oaieval.py:241] counts/SCORE2: 10
[2023-09-16 12:29:03,764] [oaieval.py:241] counts/SCORE3: 22
[2023-09-16 12:29:03,764] [oaieval.py:241] counts/SCORE5: 20
[2023-09-16 12:29:03,764] [oaieval.py:241] counts/SCORE7: 6
[2023-09-16 12:29:03,764] [oaieval.py:241] score: 5.9397590361445785

2. azure gpt 4 32k 0613
[2023-09-16 12:26:34,197] [oaieval.py:239] Final report:
[2023-09-16 12:26:34,198] [oaieval.py:241] counts/SCORE10: 79
[2023-09-16 12:26:34,199] [oaieval.py:241] counts/SCORE7: 5
[2023-09-16 12:26:34,200] [oaieval.py:241] counts/SCORE0: 45
[2023-09-16 12:26:34,201] [oaieval.py:241] counts/SCORE8: 10
[2023-09-16 12:26:34,201] [oaieval.py:241] counts/SCORE2: 3
[2023-09-16 12:26:34,201] [oaieval.py:241] counts/SCORE5: 21
[2023-09-16 12:26:34,201] [oaieval.py:241] counts/__invalid__: 1
[2023-09-16 12:26:34,201] [oaieval.py:241] counts/SCORE6: 1
[2023-09-16 12:26:34,201] [oaieval.py:241] counts/SCORE9: 1
[2023-09-16 12:26:34,201] [oaieval.py:241] score: 6.210843373493976

3. azure gpt 4 32k 0313
[2023-09-16 12:22:42,294] [oaieval.py:239] Final report:
[2023-09-16 12:22:42,296] [oaieval.py:241] counts/SCORE10: 137
[2023-09-16 12:22:42,296] [oaieval.py:241] counts/SCORE8: 7
[2023-09-16 12:22:42,296] [oaieval.py:241] counts/SCORE0: 1
[2023-09-16 12:22:42,296] [oaieval.py:241] counts/SCORE5: 11
[2023-09-16 12:22:42,296] [oaieval.py:241] counts/SCORE7: 3
[2023-09-16 12:22:42,296] [oaieval.py:241] counts/SCORE3: 5
[2023-09-16 12:22:42,296] [oaieval.py:241] counts/__invalid__: 2
[2023-09-16 12:22:42,296] [oaieval.py:241] score: 9.13855421686747

4. azure gpt 3.5 4k 0301
[2023-09-16 15:05:54,148] [oaieval.py:239] Final report:
[2023-09-16 15:05:54,151] [oaieval.py:241] counts/SCORE10: 72
[2023-09-16 15:05:54,153] [oaieval.py:241] counts/SCORE5: 29
[2023-09-16 15:05:54,153] [oaieval.py:241] counts/SCORE7: 23
[2023-09-16 15:05:54,153] [oaieval.py:241] counts/SCORE8: 7
[2023-09-16 15:05:54,153] [oaieval.py:241] counts/SCORE2: 13
[2023-09-16 15:05:54,153] [oaieval.py:241] counts/SCORE3: 9
[2023-09-16 15:05:54,153] [oaieval.py:241] counts/SCORE4: 1
[2023-09-16 15:05:54,153] [oaieval.py:241] counts/SCORE0: 12
[2023-09-16 15:05:54,153] [oaieval.py:241] score: 6.86144578313253

5. azure gpt 4 8k 0613
[2023-09-16 15:09:56,094] [oaieval.py:239] Final report:
[2023-09-16 15:09:56,094] [oaieval.py:241] counts/SCORE0: 48
[2023-09-16 15:09:56,094] [oaieval.py:241] counts/SCORE10: 87
[2023-09-16 15:09:56,094] [oaieval.py:241] counts/SCORE6: 3
[2023-09-16 15:09:56,094] [oaieval.py:241] counts/SCORE5: 17
[2023-09-16 15:09:56,094] [oaieval.py:241] counts/SCORE8: 9
[2023-09-16 15:09:56,094] [oaieval.py:241] counts/SCORE7: 1
[2023-09-16 15:09:56,094] [oaieval.py:241] counts/SCORE9: 1
[2023-09-16 15:09:56,094] [oaieval.py:241] score: 6.391566265060241

6. open ai gpt 3.5 16k latest
[2023-09-16 15:18:29,678] [oaieval.py:239] Final report:
[2023-09-16 15:18:29,678] [oaieval.py:241] counts/SCORE10: 66
[2023-09-16 15:18:29,679] [oaieval.py:241] counts/SCORE0: 24
[2023-09-16 15:18:29,680] [oaieval.py:241] counts/SCORE3: 21
[2023-09-16 15:18:29,680] [oaieval.py:241] counts/SCORE5: 18
[2023-09-16 15:18:29,680] [oaieval.py:241] counts/SCORE8: 13
[2023-09-16 15:18:29,681] [oaieval.py:241] counts/SCORE2: 13
[2023-09-16 15:18:29,681] [oaieval.py:241] counts/SCORE7: 10
[2023-09-16 15:18:29,681] [oaieval.py:241] counts/SCORE4: 1
[2023-09-16 15:18:29,681] [oaieval.py:241] score: 6.126506024096385

# Finetune 

## Use Open AI service for finetune 
Submit the finetune file and create finetune job
```bash
$ python submit_finetune_job.py ./finetune_data.jsonl
Uploading file ./finetune_data.jsonl
Fine tune file info: {
  "object": "file",
  "id": "file-F016DlAvgy9OeWSW61GXnnOr",
  "purpose": "fine-tune",
  "filename": "file",
  "bytes": 1177668,
  "created_at": 1694924971,
  "status": "uploaded",
  "status_details": null
}
Waiting for file to be processed
{
  "object": "file",
  "id": "file-xxx",
  "purpose": "fine-tune",
  "filename": "file",
  "bytes": 1177668,
  "created_at": 1694924971,
  "status": "uploaded",
  "status_details": null
}
```

Wait for finetune job to complete:
```bash
python waiting_finetune_job.py
Trained 911 seconds
 {
  "object": "fine_tuning.job",
  "id": "ftjob-xxx",
  "model": "gpt-3.5-turbo-0613",
  "created_at": 1694923368,
  "finished_at": 1694924268,
  "fine_tuned_model": "ft:gpt-3.5-turbo-0613:personal::7zdWAcr9",
  "organization_id": "org-om8aNZzKGGHU1ILO6osvYUQY",
  "result_files": [
    "file-HfNO3qGePlf0XVoTjtzaSOZa"
  ],
  "status": "succeeded",
  "validation_file": null,
  "training_file": "file-ELIMV4SWH5kGkItNXSnJv9xX",
  "hyperparameters": {
    "n_epochs": 3
  },
  "trained_tokens": 970065,
  "error": null
}
```

## Eval finetuned model

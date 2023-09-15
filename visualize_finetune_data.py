import gradio as gr
import json
import fire

dataset = []
dirty_count = 0
    
def save_data(file_path, index, user_prompt, assistant_response):
    current_index = int(index)
    save_prompt_to_dataset(current_index, user_prompt, assistant_response)
    global dirty_count
    with open(file_path, "w") as f:
        for data in dataset:
            f.write(json.dumps(data) + "\n")
    dirty_count = 0
    return "Modified Row: 0"
    
def load_data(file_path):
    global dataset
    global dirty_count
    dataset = []
    with open(file_path, "r") as f:
        for line in f.readlines():
            dataset.append(json.loads(line))
    dirty_count = 0
    return "Modified Row: 0", "0", *get_prompt_in_example(0)

def next_example(index, user_prompt, assistant_response):
    current_index = int(index)
    save_prompt_to_dataset(current_index, user_prompt, assistant_response)
    next_index = int(index) + 1
    return f"Modified Row: {dirty_count}", str(next_index), *get_prompt_in_example(next_index)

def delete_example(index, user_prompt, assistant_response):
    global dataset
    global dirty_count
    current_index = int(index)
    dataset.pop(current_index)
    dirty_count += 1

    if current_index == len(dataset):
        current_index = len(dataset) - 1

    return f"Modified Row: {dirty_count}", str(current_index), *get_prompt_in_example(current_index)

def go_to_example(index):
    current_index = int(index)
    return f"Modified Row: {dirty_count}", str(current_index), *get_prompt_in_example(current_index)
    
def get_prompt_in_example(index):
    if index >= len(dataset) or len(dataset) == 0:
        return "Dataset is empty", "Dataset is empty"
    example = dataset[index]
    return example["messages"][-2]["content"], example["messages"][-1]["content"]

def save_prompt_to_dataset(index, user_prompt, assistant_response):
    global dataset
    global dirty_count
    if (dataset[index]["messages"][-2]["content"] != user_prompt):
        print("Changed user prompt") 
        dirty_count += 1
    elif (dataset[index]["messages"][-1]["content"] != assistant_response):
        print("Changed assistant response")
        dirty_count += 1
    dataset[index]["messages"][-2]["content"] = user_prompt
    dataset[index]["messages"][-1]["content"] = assistant_response

def main(default_file_path = "./finetune_data.jsonl"):
    with gr.Blocks() as demo:
        with gr.Column(variant="panel"):
            with gr.Row(variant="compact"):
                file_path_text = gr.Textbox(
                    value=default_file_path,
                    label="finetune data path",
                    show_label=False,
                    container=False,
                    max_lines=1,
                    placeholder="finetune data path",
                )
                
                load_btn = gr.Button("Load").style(full_width=False)

                save_btn = gr.Button("Save").style(full_width=False)
                

            with gr.Row(variant="compact"):
                dataset_index = gr.Textbox(
                    value="0",
                    label="dataset index",
                    show_label=False,
                    container=False,
                    max_lines=1,
                    placeholder="",
                )
                modified_count_text = gr.Textbox(
                    value="Modified Row: 0",
                    label="Modified count",
                    show_label=True,
                    container=False,
                    max_lines=1,
                    placeholder="",
                )
                go_btn = gr.Button("Go").style(full_width=False)
                delete_btn = gr.Button("Delete Current").style(full_width=False)
                next_btn = gr.Button("Next").style(full_width=False)

            with gr.Row(variant="compact"):
                user_prompt = gr.Textbox(
                    value="",
                    label="prompt text",
                    interactive=True,
                    show_label=True,
                    container=False,
                    lines=50,
                    placeholder="",
                )

                with gr.Column(variant="panel"):
                    assistant_response = gr.Textbox(
                        value="",
                        label="assistant response text",
                        interactive=True,
                        show_label=True,
                        container=False,
                        lines=50,
                        placeholder="",
                    )
        
            load_btn.click(load_data, file_path_text, [modified_count_text, dataset_index, user_prompt, assistant_response])
            save_btn.click(save_data, [file_path_text, dataset_index, user_prompt, assistant_response], [modified_count_text])
            go_btn.click(go_to_example, [dataset_index], [modified_count_text, dataset_index, user_prompt, assistant_response])
            delete_btn.click(delete_example, [dataset_index], [modified_count_text, dataset_index, user_prompt, assistant_response])
            next_btn.click(next_example, [dataset_index, user_prompt, assistant_response], [modified_count_text, dataset_index, user_prompt, assistant_response])
            
        demo.launch()

if __name__ == "__main__":
    fire.Fire(main)
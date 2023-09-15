import fire
import json

def finetune_data_to_eval_format(finetune_data_path, eval_file_path):
    eval_set = []
    with open(finetune_data_path, "r") as f:
        for line in f.readlines():
            finetune_data = json.loads(line)
            eval_data = {
                "input": finetune_data["messages"][:-1],
                "ideal": finetune_data["messages"][-1]["content"]
            }
            eval_set.append(eval_data)

    with open(eval_file_path, "w") as f:
        for data in eval_set:
            f.write(json.dumps(data) + "\n")

if __name__ == "__main__":
    fire.Fire(finetune_data_to_eval_format)
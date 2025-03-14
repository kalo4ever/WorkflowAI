import os


def build_api_docs_prompt(folder_name: str = "docs") -> str:
    api_docs: str = ""

    for file in os.listdir(folder_name):
        with open(os.path.join(folder_name, file), "r") as f:
            api_docs += f"{file}\n{f.read()}\n\n"

    return api_docs

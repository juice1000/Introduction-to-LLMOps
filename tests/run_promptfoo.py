import os
import shutil
import subprocess
import sys

# Run promptfoo regression tests from Python using eval and Ollama


def run_promptfoo():
    promptfoo_path = shutil.which("promptfoo")

    if not promptfoo_path:
        raise RuntimeError("Promptfoo not found in PATH")
    try:
        # check if yaml file exists
        yaml_file = "promptfoo.yaml"
        if not os.path.exists(yaml_file):
            raise FileNotFoundError(f"{yaml_file} not found. Please create it before running tests.")

        result = subprocess.run(
            ["promptfoo", "eval", "promptfoo.yaml"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Promptfoo eval failed:")
        print(e.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    run_promptfoo()

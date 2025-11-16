import yaml

def load_config(file: str):
    try:
        with open(file, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file} not found.")
    except Exception as e:
        raise ValueError(f"Error reading config at {file}: {e}")

import yaml
import os

def load_config(config_file, default):
    if not os.path.exists(os.path.join("conf")):
        os.makedirs(os.path.join("conf"))
        
    try:
        with open(os.path.join("conf", config_file), 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        config = {}  # If the file doesn't exist, start with an empty dictionary

    # Update missing keys with default values
    for key, value in default.items():
        if key not in config:
            config[key] = value

    # Save the updated config to the file
    with open(os.path.join("conf", config_file), 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

    return config
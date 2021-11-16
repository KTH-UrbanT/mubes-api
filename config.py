import yaml

# Safe loader for any YAML files
def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

# Configuration loader
def load_config():
    try:
        # Trying to read in default configuration updated via git
        config = read_yaml('default.yml')
        try:
            # Trying to read in local configuration for a particular machine
            local = read_yaml('config.yml')

            # If local configuration exists, let's update the default configuration with the new values
            for key in config:
                if key in local:
                    config[key] = local[key]

            if __debug__:
                print("Using the local configuration (config.yml)")
        except:
            # If local configuration doesn't exist, using the default one
            if __debug__:
                print("Using the default configuration (default.yml)")
            pass
        return config
    except:
        try:
            # Trying to read in local configuration for a particular machine
            config = read_yaml('config.yml')
            return config
        except:
            # If neither default nor local configuration is found, throw the exception 
            raise Exception('Configuration file (config.yml) not found.')
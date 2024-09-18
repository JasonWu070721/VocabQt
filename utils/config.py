import os
import yaml

config_file = "config/setting.yaml"


def init_config():

    if not os.path.exists("config"):
        os.makedirs("config")

    check_file = os.path.exists(config_file)

    if check_file:
        return

    config = {
        "app": {"name": "VocabQt", "version": 1.0, "debug": True},
        "setting": {
            "auto_refill": True,
            "random_word_count": 10,
        },
    }

    with open(config_file, "w") as file:
        yaml.dump(config, file, default_flow_style=False)

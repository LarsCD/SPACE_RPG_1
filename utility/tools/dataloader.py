import logging
import os
from os.path import dirname, abspath
from pathlib import Path
import json

from data.config.config_settings import DATALOADER_SETTINGS
from utility.tools.dev_logger import DevLogger

class Dataloader:
    def __init__(self):
        self.log = DevLogger(Dataloader).log

        self.cwd = dirname(dirname(dirname(abspath(__file__))))
        self.data_paths = DATALOADER_SETTINGS['data_paths']

    def load_data(self):
        """
        Load data from self.data_paths

        :return: data dict
        """
        data_dict = {}
        self.log(logging.INFO, f'loading data...')
        for path in self.data_paths:
            full_path = f"{self.cwd}{self.data_paths[path]}"
            folder_name = Path(full_path).name  # <-- get just the folder name
            data_dict[folder_name] = self.load_data_from_path(full_path)
        return data_dict


    def load_data_from_path(self, full_path):
        """
        Load data from path

        :param full_path:
        :return:
        """
        data_dict = {}
        for filename in os.listdir(full_path):
            if filename.endswith(".json"):
                file_path = os.path.join(full_path, filename)
                self.log(logging.INFO, f'loading \'{filename}\'')
                with open(file_path, "r") as file:
                    loaded_data = json.load(file)
                    data_dict[filename.removesuffix('.json')] = loaded_data
        return data_dict


if __name__ == '__main__':
    data = Dataloader().load_data()
    print(data)

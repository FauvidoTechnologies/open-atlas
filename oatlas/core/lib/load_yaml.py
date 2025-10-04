from typing import Tuple, Set, Dict

import yaml

from oatlas.config import Config
from oatlas.logger import get_logger

log = get_logger()


class LoadMethodsYaml:
    """
    This is how the methods yaml looks like:
            EngineName1:
                common_name:
                abbreviated_name:
                Functions:
                    Function1:
                        desc:
                        arguments:
                        return_value:
                    Function2:
                        desc:
                        ...
                ...
            ...
    """

    def __init__(self):
        self.methods_file = Config.path.methods_path
        with open(self.methods_file) as stream:
            try:
                self.data = yaml.safe_load(stream)
            except yaml.YAMLError:
                log.error(
                    "Error in loading the abbreviations file!"
                )  # This will only happen if you mistakenly remove the file or change locations
                return

    def load_engines(self) -> Tuple[Tuple[str, str, str, str], ...]:
        """
        Loads all the modules and their abbreviations along with their common-names
        and the actual engine name.

        Returns a tuple of tuples:
            ((engine_name, abbreviated_name, common_name, desc), ...)
        """
        result = tuple(
            (k, v.get("abbreviated_name"), v.get("common_name"), v.get("desc"))
            for k, v in self.data.items()
            if isinstance(v, dict)
            and "abbreviated_name" in v
            and "common_name" in v
            and "desc" in v
        )

        return result

    def load_functions(self) -> Tuple[Set[str], Dict]:
        """
        Loads all the functions and returns them as a set. This is only keeping the function keys
        which means their names.
        """
        functions_set = set()
        functions_desc_dict = {}

        for engine_name, engine_info in self.data.items():
            if isinstance(engine_info, dict):
                functions = engine_info.get("functions", {})
                if isinstance(functions, dict):
                    functions_set.update(functions.keys())
                    for func_name, func_info in functions.items():
                        if isinstance(func_info, dict):
                            desc = func_info.get("desc", "")
                            functions_desc_dict[func_name] = desc

        return (functions_set, functions_desc_dict)

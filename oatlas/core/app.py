import sys
from typing import List, Dict, Any

import oatlas.tools
from oatlas.config import Config, version_info
from oatlas.core.arg_parser import ArgParser
from oatlas.core.lib.functions import class_function_dict
from oatlas.logger import get_logger, TerminalCodes
from oatlas.utils.dependency_manager import HandleDependencies
from oatlas.utils.die import die_success, die_failure

log = get_logger()


class OAtlas(ArgParser):
    """
    The main aggregator class
    """

    def __init__(self):
        self.print_banner()
        self.setup_dependencies()

        functions = self.get_all_functions()
        self.func_to_class = self.function_to_class_dict()
        self.function_definitions = self.get_function_details(functions)

        super().__init__()

    @staticmethod
    def print_banner() -> None:
        """
        Printing the Atlas banner
        """
        log.write(
            open(Config.path.banner_file)
            .read()
            .format(
                cyan=TerminalCodes.CYAN.value,
                red=TerminalCodes.RED.value,
                rst=TerminalCodes.RESET.value,
                v1=version_info(),
                yellow=TerminalCodes.YELLOW.value,
                green=TerminalCodes.GREEN.value,
            )
        )
        log.reset_color()

    @staticmethod
    def get_all_functions() -> List:
        """
        Returns a list of functions of type FunctionDeclaration
        """
        return [item for sublist in list(class_function_dict.values()) for item in sublist]

    @staticmethod
    def function_to_class_dict() -> Dict:
        """
        This returns all the functions with their classes

        Returns:
            {
                "function_1": "class_1",
                "function_2": "class_2",
                ...
            }
        """
        func_to_class = {
            func.name: cls_name
            for cls_name, funcs in class_function_dict.items()
            for func in funcs
        }
        return func_to_class

    def setup_dependencies(self):
        """
        Set's up the right dependencies

        1. Checks for the platform
        4. Install's playwright dependencies if not already existing
        5. Install's DeepFace dependencies if not already existing
        """
        if sys.platform not in {"darwin", "linux"}:
            die_failure(
                "The platform you're running Atlas on is not supported! Please use Darwin or Linux"
            )

        # Install playwright dependencies
        try:
            HandleDependencies.playwright().handle_dependencies()
        except Exception as e:
            die_failure(f"Couldn't install playwright dependencies for browser automations: {e}")
        # Install DeepFace dependencies
        try:
            HandleDependencies.deepface().handle_dependencies()
        except Exception as e:
            die_failure(f"Couldn't install DeepFace dependencies for image analysis: {e}")
        # Install Rust dependencies
        try:
            HandleDependencies.rust().handle_dependencies()
        except Exception as e:
            # We don't have to kill the application because of this
            log.error(f"Couldn't install rust dependencies for binary analysis: {e}")
        # Install Tesseract OCR dependencies
        try:
            HandleDependencies.tesseract().handle_dependencies()
        except Exception as e:
            # We don't have to kill the application because of this
            log.error(f"Couldn't install Tesseract dependencies for OCR analysis: {e}")

    def map_entered_func_to_class(self, name_list: list) -> Dict[str, str]:
        """
        Function to map the entered function names to their classes.

        Args:
            name_list: The user entered list of function names
        Returns:
            mapping between entered functions to classes
        """
        mapping = {}
        for name in name_list:
            if name in self.func_to_class:
                mapping[name] = self.func_to_class[name]
            else:
                log.warn(f"Function '{name}' not found. It will be skipped.")
                mapping[name] = None
        return mapping

    def _get_user_arguments_for_function(self, func_name: str) -> Dict[str, Any]:
        """Handles the interactive session to get arguments for a single function from the user."""
        definition = self.function_definitions.get(func_name)
        if not definition:
            log.error(f"Could not find definition for function: {func_name}")
            return None

        properties = list(definition.get("properties").items())
        function_desc = definition.get("description")

        print(f"\n{'─' * 50}")
        print(f"🔹 Function: {func_name}")
        print(f"   Description: {function_desc}")
        print(f"{'─' * 50}")
        print("Please provide the following arguments:")

        arg_values = {}
        for arg_name, arg_info in properties:
            required = arg_name in definition.get("required")
            default_val = arg_info.default  # This will be None by default anyways

            print(f"\n  » Argument: '{arg_name}' {'(required)' if required else '(optional)'}")
            print(f"    Description: {arg_info.description}")
            print(f"    Type: {arg_info.type.lower()}")

            while True:
                prompt = f"    Enter value for {arg_name}: "
                user_val = input(prompt).strip()

                if not user_val:  # Blank input
                    if required:
                        print(f"   Error: '{arg_name}' is required. Please provide a value.")
                        continue
                    else:
                        arg_values[arg_name] = default_val
                        break

                try:
                    if arg_info.type.lower() == "integer":
                        user_val = int(user_val)
                    elif arg_info.type.lower() == "number":
                        user_val = float(user_val)
                    elif arg_info.type.lower() == "boolean":
                        user_val = user_val.lower() in ["true", "1", "yes", "y"]
                    elif arg_info.type.lower() == "array":
                        user_val = [x.strip() for x in user_val.split(",")]

                    arg_values[arg_name] = user_val
                    break
                except ValueError:
                    print(f"    Invalid type. Please enter a valid {arg_info.type.lower()}.")

        return arg_values

    def _process_function(self, func_name: str, callable_functions: Dict):
        """Gets arguments for, executes, and prints the result of a single function."""
        arg_values = self._get_user_arguments_for_function(func_name)
        if arg_values is None:
            return  # Skip if definition was not found

        print(f"\n✅ Running '{func_name}' with arguments: {arg_values}\n")
        try:
            result = callable_functions.get(func_name)(**arg_values)
            print(f"✨ Result: {result}")
        except Exception as e:
            log.error(f"An error occurred while running '{func_name}': {e}")

    def _prompt_for_next_run(self) -> bool:
        """Asks the user if they want to continue and updates the function list."""
        choice = input("\nDo you want to run more functions? (yes/no): ").strip().lower()
        if choice not in ["yes", "y"]:
            return False

        new_funcs_str = input("Enter new function names (comma-separated): ").strip()
        if not new_funcs_str:
            print("No new functions entered. Exiting.")
            return False

        self.arguments.functions = [f.strip() for f in new_funcs_str.split(",") if f.strip()]
        return True

    def run(self):
        """
        Main execution loop to run functions interactively.
        """
        while True:
            entered_func_to_class = self.map_entered_func_to_class(self.arguments.functions)

            # Filter out functions that were not found
            valid_funcs_map = {k: v for k, v in entered_func_to_class.items() if v is not None}

            if not valid_funcs_map:
                log.warn("None of the specified functions were found.")
                if not self._prompt_for_next_run():
                    break
                else:
                    continue

            callable_functions = self.names_to_classes(valid_funcs_map)

            log.colorful(
                f"\nStarting execution for: {list(callable_functions.keys())}",
                log.COLORS["INFO"],
            )

            for func_name in callable_functions.keys():
                self._process_function(func_name, callable_functions)

            print(f"\n{'=' * 50}\n")
            if not self._prompt_for_next_run():
                break

        log.excited("All tasks completed.")
        die_success()

    def names_to_classes(self, entered_func_to_class: Dict) -> Dict[str, Any]:
        """
        Takes the dictionary and imports the classes as modules

        returns:
            {
                "function_name": function-to-be-called,
                ...
            }
        """
        output = {}
        for func_name, engine_name in entered_func_to_class.items():
            try:
                engine_class = getattr(oatlas.tools, engine_name)
                func = getattr(engine_class, func_name)
                output[func_name] = func
            except AttributeError:
                log.error(
                    f"Could not load function '{func_name}' from engine '{engine_name}'. Skipping."
                )
        return output

    def get_function_details(self, functions: list) -> Dict:
        """
        Takes all the functions of the FunctionDeclaration type and extracts the relevant
        attributes to help users enter arguments for said functions

        Returns:
        {
            "function_name": {
                "description"="function_description in details",
                "parameters"={
                    "properties": {
                        "argument_1": {
                            "type": "string|number|list",
                            "description": "argument_description",
                        }
                    },
                    "required": ["argument_1"],
                },
            },
            "function_name": {
                "description"="function_description in details",
                "parameters"={
                    "properties": {
                        "argument_1": {
                            "type": "string|number|list",
                            "description": "argument_description",
                        }
                    },
                    "required": ["argument_1"],
                },
            },
            ...
        }
        """
        details = {}
        for func in functions:
            details[func.name] = {
                "description": func.description.strip(),
                "properties": func.parameters.properties,
                "required": func.parameters.required,
            }
        return details

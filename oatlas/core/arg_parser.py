import os
import subprocess
import sys
from argparse import ArgumentParser
from typing import Set

from oatlas import service_dictionary
from oatlas.config import Config, version_info
from oatlas.core.lib.load_yaml import LoadMethodsYaml
from oatlas.logger import get_logger
from oatlas.utils.common import read_file
from oatlas.utils.die import die_failure, die_success

log = get_logger()


class ArgParser(ArgumentParser):
    def __init__(self) -> None:
        super().__init__(prog="oatlas", add_help=False)

        # Load the functions for AA as a set
        self.functions_tuple = self.load_functions()
        self.functions = self.functions_tuple[0]
        self.functions_desc_dict = self.functions_tuple[1]

        # Add and parse arguments
        self.add_arguments()
        self.parse_arguments()

    @staticmethod
    def load_functions() -> Set:
        """
        Loads all the functions that is present within Atlas
        """
        log.info("Loading functions")
        loaded_functions_set = LoadMethodsYaml().load_functions()
        return loaded_functions_set

    def add_arguments(self):
        # --- Engine options ---
        engine_options = self.add_argument_group("Engine", "Engine input options")
        engine_options.add_argument(
            "-V",
            "--version",
            action="store_true",
            dest="show_version",
            default=Config.settings.show_version,
            help="Display the software version",
        )
        engine_options.add_argument(
            "--show-api-services",
            action="store_true",
            default=Config.settings.show_api_services,
            help="Show all the API services that Atlas is using",
        )
        engine_options.add_argument(
            "--show-all-functions",
            action="store_true",
            default=Config.settings.show_all_functions,
            help="Show all the functions that one can use with the AA mode",
        )
        engine_options.add_argument(
            "-h",
            "--help",
            action="store_true",
            default=Config.settings.show_help_menu,
            dest="show_help_menu",
            help="Display the help menu",
        )

        web_server_options = self.add_argument_group("WebServer", "web server options")
        web_server_options.add_argument(
            "--start-web-server",
            action="store_true",
            dest="start_web_server",
            default=Config.web.start_api_server,
            help="Start the webserver for a more interactive and less coding Atlas",
        )

        unified_options = self.add_argument_group("Atlas", "Main execution options")
        unified_options.add_argument(
            "-f",
            "--functions",
            action="store",
            dest="functions",
            default=Config.settings.functions,
            help="Select the functions. For example: {}".format(list(self.functions)[:5]),
        )
        unified_options.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            dest="verbose_mode",
            default=Config.settings.verbose_mode,
            help="Enable verbose responses",
        )
        unified_options.add_argument(
            "-H",
            "--paid-keys",
            action="append",  # Users can enter keys using -H "key1" -H "key2"
            dest="paid_keys",
            default=Config.settings.paid_keys,
            help="Provide paid keys for APIs if needed",
        )
        unified_options.add_argument(
            "-o",
            "--use-openai",
            action="store_true",
            dest="use_openai",
            default=Config.settings.use_openai,  # Default at False
            help="Use this flag if you want to run the loop using OpenAI's GPT-4o",
        )

    def parse_arguments(self):
        """
        check all rules and requirements for ARGS

        Args:
        api_forms: values from nettacker.api

        Returns:
        all ARGS with applied rules
        """
        options = self.parse_args()

        # Check Help Menu
        if options.show_help_menu:
            self.print_help()
            die_success()

        # Check version
        if options.show_version:
            log.info(f"Software-version: {version_info()}")
            die_success()

        if options.show_api_services:
            for service in list(service_dictionary.keys()):
                about = service_dictionary.get(service)
                log.normal(
                    f"""
                    {about.get('name')}: {
                    read_file(Config.path.APIListingStructure).format(
                        description=about.get('description'),
                        current_version=about.get('current_version'),
                        paid_versions_available=about.get('paid_versions_available'),
                        available_paid_versions=about.get('available_paid_versions')
                        )
                    }\n"""
                )
            die_success()

        if options.show_all_functions:
            for func, desc in self.functions_desc_dict.items():
                log.normal(f"{func} - {desc}")
            die_success()

        if options.start_web_server:
            # start the streamlit application and log the API access code for the user
            # This is so not going to work, but it does
            app_path = Config.web.app_path
            proc = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", app_path],
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            proc.wait()

        if not options.functions:
            die_failure("Please specify which modules you want Atlas to run the Aggregator on!")

        options.functions = set(options.functions.split(","))

        if len(options.functions - self.functions) != 0:
            # This means wrong functions were used!
            die_failure(
                f"These functions are not supported: {options.functions-self.functions}. Please check for typos and refer to the functions list"
            )

        if options.use_openai:
            if os.getenv("openai_api_key") is None:
                die_failure(
                    "Please set the OpenAI key in the enviornment if you wish to use its models!"
                )

        self.arguments = options

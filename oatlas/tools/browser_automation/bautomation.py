import os
from typing import Literal

from pyba import Engine, Database, DFS, BFS

from oatlas.config import Config
from oatlas.core.arg_parser import ArgParser


class BrowserAutomationEngine(ArgParser):
    """
    This will work differently from the others. We will have to initialize this!
    """

    def __init__(self):
        super().__init__()
        # VertexAI specific config
        self.project_id = os.getenv(Config.settings.project_id)
        self.location = Config.settings.location

        # OpenAI-specific configurations
        self.openai_api_key = os.getenv(Config.settings.openai_api_key)

        # Gemini specific configuration
        self.gemini_api_key = os.getenv(Config.settings.gemini_api_key)

    def get_database(self):
        # Returns the database instance based on the config values:

        database_configs = Config.browserautomations.Database.as_dict()
        database = Database(**database_configs)
        return database

    def get_automation_engine(
        self,
        enable_tracing: bool,
        trace_save_directory: str,
        headless: bool,
        use_logger: bool,
        database,
        mode: Literal["DFS", "BFS"] = Config.browserautomations.mode,
        max_depth: int = Config.browserautomations.max_depth,
        max_breadth: int = Config.browserautomations.max_breadth,
    ):
        cls = Engine if mode is None else (DFS if mode == "DFS" else BFS)

        kwargs = {
            "handle_dependencies": Config.browserautomations.handle_dependencies,
            "database": database,
            "headless": headless,
            "use_logger": use_logger,
            "enable_tracing": enable_tracing,
            "trace_save_directory": trace_save_directory,
        }

        if cls in (DFS, BFS):
            kwargs["max_depth"] = max_depth
            kwargs["max_breadth"] = max_breadth

        if self.project_id:
            kwargs.update(
                {
                    "vertexai_project_id": self.project_id,
                    "vertexai_server_location": self.location,
                }
            )
        elif self.openai_api_key:
            kwargs.update({"openai_api_key": self.openai_api_key})
        else:
            kwargs.update({"gemini_api_key": self.gemini_api_key})

        return cls(**kwargs)

    @staticmethod
    def run_automated_browser_instance(
        prompt: str,
        database_mode: bool = Config.browserautomations.database_mode,
        generate_code: bool = Config.browserautomations.generate_code,
        enable_tracing: bool = Config.browserautomations.enable_tracing,
        trace_save_directory: str = Config.browserautomations.trace_save_directory,
        mode: Literal["DFS", "BFS"] = Config.browserautomations.mode,
        max_depth: int = Config.browserautomations.max_depth,
        max_breadth: int = Config.browserautomations.max_breadth,
    ):
        instance = BrowserAutomationEngine()

        if database_mode:
            database = instance.get_database()
        else:
            database = None

        engine = instance.get_automation_engine(
            enable_tracing=enable_tracing,
            trace_save_directory=trace_save_directory,
            headless=Config.browserautomations.headless,
            use_logger=Config.browserautomations.use_logger,
            database=database,
            mode=mode,
            max_depth=max_depth,
            max_breadth=max_breadth,
        )

        # running the sync endpoint for now
        output = engine.sync_run(
            prompt=prompt, automated_login_sites=Config.browserautomations.default_login_sites
        )

        if generate_code:
            engine.generate_code(output_path=Config.browserautomations.code_output_path)

        return output

import os

from pyba import Engine

from oatlas.config import Config
from oatlas.core.arg_parser import ArgParser


class BrowserAutomationEngine(ArgParser):
    """
    This will work differently from the others. We will have to initialize this!
    """

    def __init__(self):
        super().__init__()
        self.use_openai = self.arguments.use_openai

        # VertexAI specific config
        self.project_id = os.getenv(Config.settings.project_id)
        self.location = Config.settings.location

        # OpenAI-specific configurations
        self.openai_api_key = os.getenv(Config.settings.openai_api_key)

    def get_automation_engine(self):
        # We need this to handle dependencies for us by default
        if not self.use_openai:
            engine = Engine(
                vertexai_project_id=self.project_id,
                vertexai_server_location=self.location,
                handle_dependencies=Config.browserautomations.handle_dependencies,
            )
        else:
            engine = Engine(openai_api_key=self.openai_api_key)

        return engine

    @staticmethod
    def run_automated_browser_instance(prompt: str):
        instance = BrowserAutomationEngine()
        engine = instance.get_automation_engine()

        # running the sync endpoint for now
        engine.sync_run(
            prompt=prompt, automated_login_sites=Config.browserautomations.default_login_sites
        )

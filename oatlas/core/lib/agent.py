import os
from typing import Union, Dict

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
from openai import OpenAI

from oatlas.config import Config
from oatlas.core.arg_parser import ArgParser
from oatlas.logger import get_logger
from oatlas.utils.common import read_file, build_openai_image_part

load_dotenv()
log = get_logger()


class GeneralAgent(ArgParser):
    """
    Defines the functionality of the General Agent.
    Can operate on either VertexAI (Google) or OpenAI, depending on `use_openai`.
    """

    def __init__(self):
        """
        Takes an additional use_openai parameter to specify which LLM to use.
        """
        super().__init__()
        self.temperature = Config.settings.brain_temperature

        # VertexAI-specific configurations
        self.project_id = os.getenv(Config.settings.project_id)
        self.location = Config.settings.location

        # OpenAI-specific configurations
        self.openai_api_key = os.getenv(Config.settings.openai_api_key)
        self.use_openai = self.arguments.use_openai

    def _initialise_vertexai(
        self,
        temperature: int = 0,
        system_instruction: str = None,
        response_schema=None,
        response_mime_type: str = None,
    ):
        """
        Initializes the VertexAI chat client and context. This is as we were doing previosuly
        """
        self.client = genai.Client(
            vertexai=Config.settings.vertexai,
            project=self.project_id,
            location=self.location,
        )

        chat = self.client.chats.create(
            model=str(Config.settings.model),
            config=GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction,
                response_schema=response_schema,
                response_mime_type=response_mime_type,
            ),
        )
        return chat

    def _process_vertexai(
        self,
        prompt: str,
        temperature: int = 0,
        system_instruction: str = None,
        response_schema=None,
        response_mime_type: str = None,
    ):
        """
        Processes a prompt using VertexAI. The prompt itself willbe handling how the image is to be pasesd.
        You can check how that is working in the .process() method below
        """
        chat_context = self._initialise_vertexai(
            temperature=temperature,
            system_instruction=system_instruction,
            response_schema=response_schema,
            response_mime_type=response_mime_type,
        )
        response = chat_context.send_message(prompt)

        return response

    def _initialise_openai(self):
        """
        Initializes the OpenAI client. This is alittle simpler than vertexAIs, because most of the
        arguments are passed along with the prompt itself
        """
        self.client = OpenAI(api_key=self.openai_api_key)

    def _process_openai(
        self,
        prompt: Union[str, list],
        system_instruction: str = "",
        response_schema=None,
        response_mime_type: str = None,
    ):
        """
        Processes a prompt using OpenAI's API.
        Supports both text-only and multimodal (image+text) inputs.
        """
        if not hasattr(self, "client"):
            self._initialise_openai()

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]

        kwargs = {
            "model": str(Config.settings.openai_model),
            "messages": messages,
        }

        if response_schema:
            # This is when we are passing a response scehma to the model. We use the .parse() endpoint
            response = self.client.chat.completions.parse(
                **kwargs, response_format=response_schema
            )
            return response.choices[0].message
        else:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()

    def process(
        self,
        prompt: Dict,
        temperature: int = 0,
        system_instruction: str = None,
        response_schema=None,
        response_mime_type: str = None,
    ):
        """
        Unified abstraction for OpenAI and VertexAI. Supports both text and multimodal (image + text) prompts.
        This is done using a list which is extracted cleanly later using prompt as a Dictionary to hold different types
        of values
        """

        if self.use_openai:
            print("In here")
            prompt = [
                {"type": "text", "text": read_file(Config.path.GeolocateImageVertexAI)},
                build_openai_image_part(prompt["image_path"], prompt["mime_type"]),
            ]
            return self._process_openai(
                prompt,
                system_instruction=system_instruction,
                response_schema=response_schema,
                response_mime_type=response_mime_type,
            )
        else:
            prompt = [
                read_file(Config.path.GeolocateImageVertexAI),
                types.Part(
                    inline_data=types.Blob(
                        mime_type=prompt["mime_type"], data=prompt["image_bytes"]
                    )
                ),
            ]
            return self._process_vertexai(
                prompt,
                temperature=temperature,
                system_instruction=system_instruction,
                response_schema=response_schema,
                response_mime_type=response_mime_type,
            )

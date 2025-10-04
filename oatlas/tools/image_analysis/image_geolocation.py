import base64
import json
import os
from pathlib import Path
from typing import Dict, Union

import magic
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

from oatlas.config import Config
from oatlas.logger import get_logger
from oatlas.utils.common import read_file
from oatlas.utils.structure import VertexaiGeolocationResponse

log = get_logger()
load_dotenv()


class GeneralAgent:
    """
    Defines the functionality of the general agent
    """

    def __init__(self):
        self.project_id = os.getenv(Config.settings.project_id)
        self.location = Config.settings.location

    def initialise(self):
        """
        Initialises the general agent. It only returns the client object. Can be used anyhow
        """
        client = genai.Client(
            vertexai=Config.settings.vertexai,
            project=self.project_id,
            location=self.location,
        )

        return client


def analyse_picarta_response(response: Dict) -> Dict:
    """
    The raw response from the picarta API looks like this:
    {
            'ai_confidence': 0.9438701868057251,
            'ai_country': 'Australia',
            'ai_lat': -33.86357,
            'ai_lon': 151.20209,
            'camera_maker': 'motorola',
            'camera_model': 'moto g73 5G',
            'city': 'Sydney',
            'province': 'New South Wales',
            'timestamp': '2025:08:30 16:30:08',
            'topk_predictions_dict': {
                    '1': {
                            'address': {
                                    'city': 'Sydney',
                                    'country': 'Australia',
                                    'province': 'New South Wales'
                                    },
                            'confidence': 0.9438701868057251,
                            'gps': [-33.86357, 151.20209]
                            },
                    '2': {
                            'address': {
                                    'city': 'North Adelaide',
                                    'country': 'Australia',
                                    'province': 'South Australia'
                                    },
                            'confidence': 0.9391460204124451,
                            'gps': [-34.915462, 138.59592]
                            },
                    ...
                    ...
            }
    }

    This function is to take the relevant fields from this response and return only those.
    """
    return {
        "camera_maker": response.get("camera_maker"),
        "camera_model": response.get("camera_model"),
        "topk_predictions_dict": response.get(
            "topk_predictions_dict"
        ),  # This will handle the rest
    }


def fix_absolute_path(path: str) -> str:
    """
    Normalize a path for the geolocation engine.

    - If `path` is already absolute, it is returned unchanged.
    - If `path` is relative or just a filename, the basename (filename only)
      is extracted and joined with the scenic images directory.

    Args:
        path: The path that the AI tells us to use.

    Returns:
        abs_path: The absolute path that the engine should use for geolocation.
    """
    path_obj = Path(path)

    # If already absolute, return as string, as will probably be the case for user defined images
    if path_obj.is_absolute():
        return str(path_obj)

    # Always take just the filename part
    filename = path_obj.name
    abs_path_parent = Config.path.image_file_dir / "scenic"
    return str(abs_path_parent / filename)


class ImageGeolocationEngine:
    """
    The image geolocation engine consolidates geolocation information from various APIs and outputs the most accurate location for the image
    """

    @staticmethod
    def geolocate_local_image(
        image_path: str,
        top_k: int = 10,
        country_code: str = None,
        center_latitude: float = None,
        center_longitude: float = None,
        radius: float = None,
    ) -> str:
        """
        Uses the picarta API key to perform geolocation on a locally stored image. The default version uses a free API which has a limit of 1 image search per day
        You are free to use your own API keys using the documentation provided and upgrade this service.

        Args:
                image_path: Path to the local image
                top_k: The top "k" location matches to return, default at 10, can go upto 100
                country_code: This is a 2-letter country code (e.g., "US", "FR", "DE"). Defaults to None which specifies a worldwide search
                center_latitude/center_longitude: These are float values which define the central coordinate of the area. Defaults to None which specifies a worldwide search
                radius: The search area around the center point in kilometers. Defaults to None for a worldwide search

        Returns:
                dictionary: A dictionary of relevant fields defined inside `analyse_picarta_response` if the API call was successful
                string: An error string if the API call was unsuccessful

        """
        api_key = os.getenv(Config.API.picarta.api_key)
        url = Config.API.picarta.url

        headers = {
            "Content-Type": "application/json"
        }  # Works well without a User-Agent explicitly there

        image_path = fix_absolute_path(image_path)

        with open(image_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode("utf-8")

        payload = {
            "TOKEN": api_key,
            "IMAGE": image,
            "TOP_K": top_k,
            "COUNTRY_CODE": country_code,
            "Center_LATITUDE": center_latitude,
            "Center_LONGITUDE": center_longitude,
            "RADIUS": radius,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                return json.dumps(analyse_picarta_response(result))
            else:
                log.error("Request failed with status code:", response.status_code)
                return response.text
        except Exception as e:
            error_msg = f"Failed to hit the servers of picarta: {e}"
            log.error(error_msg)
            return error_msg

    @staticmethod
    def geolocate_online_image(
        image_url: str,
        top_k: int = 10,
        country_code: str = None,
        center_latitude: float = None,
        center_longitude: float = None,
        radius: float = None,
    ) -> str:
        """
        Uses the picarta API key to perform geolocation on an image in the web. The default version uses a free API which has a limit of 1 image search per day
        You are free to use your own API keys using the documentation provided and upgrade this service.

        Args:
                image_url: The online image url
                top_k: The top "k" location matches to return, default at 10, can go upto 100
                country_code: This is a 2-letter country code (e.g., "US", "FR", "DE"). Defaults to None which specifies a worldwide search
                center_latitude/center_longitude: These are float values which define the central coordinate of the area. Defaults to None which specifies a worldwide search
                radius: The search area around the center point in kilometers. Defaults to None for a worldwide search

        Returns:
                dictionary: A dictionary of relevant fields defined inside `analyse_picarta_response` if the API call was successful
                string: An error string if the API call was unsuccessful
        """
        api_key = os.getenv(Config.API.picarta.api_key)
        url = Config.API.picarta.url

        headers = {
            "Content-Type": "application/json"
        }  # Works well without a User-Agent explicitly there

        payload = {
            "TOKEN": api_key,
            "IMAGE": image_url,
            "TOP_K": top_k,
            "COUNTRY_CODE": country_code,
            "Center_LATITUDE": center_latitude,
            "Center_LONGITUDE": center_longitude,
            "RADIUS": radius,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                return json.dumps(analyse_picarta_response(result))
            else:
                log.error("Request failed with status code:", response.status_code)
                return response.text
        except Exception as e:
            error_msg = f"Failed to hit the servers of picarta: {e}"
            log.error(error_msg)
            return error_msg

    @staticmethod
    def geolocate_using_vertexAI(
        image_path: str, prompt: str = None
    ) -> Union[VertexaiGeolocationResponse, None]:
        """
        This uses vertexAI to make inference on an Image. This is a better option for geolocation cause its an LLM ofcourse!

        Args:
            image_path: The path to the image that needs to be scanned
        Returns:
            A parsed pydantic response or None depending on if it succeeded or not
        """
        client = GeneralAgent().initialise()

        image_path = fix_absolute_path(image_path)

        mime_type = magic.from_file(image_path, mime=True)
        if mime_type is None:
            mime_type = "application/octet-stream"  # fallback

        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
        except FileNotFoundError:
            log.error(f"The image doesn't exist at {image_path}")
            return None
        except PermissionError:
            log.error(f"Atlas doesn't have permission to read {image_path}")
            return None
        except Exception as e:
            log.error(f"There was a problem: {e}")
            return None

        try:
            if prompt is None:
                prompt = "You are an image geolocation expert"
            chat = client.chats.create(
                model=Config.settings.model,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_schema=VertexaiGeolocationResponse,
                    response_mime_type="application/json",
                    system_instruction=prompt,
                ),
            )

            response = chat.send_message(
                [
                    read_file(Config.path.GeolocateImageVertexAI),
                    types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes)),
                ]
            )

            return response.parsed.model_dump()  # Return as a dictionary instead of a BaseModel

        except Exception as e:
            log.error(f"Couldn't use VertexAI for geolocation: {e}")
            return None

    @staticmethod
    def combined_llm_deeplearning_analysis(
        image_path: str,
        top_k: int = 10,
        country_code: str = None,
        center_latitude: float = None,
        center_longitude: float = None,
        radius: float = None,
        prompt: str = None,
    ) -> Dict:
        """
        This is a combined engine which takes in a local image and returns both the deeplearning scan and LLM outputs together.
        """

        picarta_result = ImageGeolocationEngine.geolocate_local_image(
            image_path=image_path,
            top_k=top_k,
            country_code=country_code,
            center_latitude=center_latitude,
            center_longitude=center_longitude,
            radius=radius,
        )

        vertex_result = ImageGeolocationEngine.geolocate_using_vertexAI(
            image_path=image_path, prompt=prompt
        )

        return {
            "picarta": picarta_result,
            "vertexai": vertex_result,
        }

    @classmethod
    def get_abbr():
        return "igE"

import asyncio
import os
from typing import Dict, List, Union

import requests

from oatlas.logger import get_logger

log = get_logger()

try:
    from deepface import DeepFace
except Exception as e:
    log.error(f"Couldn't import Deepface: {e}")
    log.error(
        "Please resolve this issue if you want to use it for AI Image detection (it's not the best though!)"
    )

from oatlas.config import UserAgents, Config
from oatlas.tools import StaticImageExtractionEngine
from oatlas.tools.AI_image_detector.utils import upload_via_playwright


class VerifyAIGeneratedImageEngine:
    """
    This class will hold tools to verify if an image is AI generated/tampered or not.

    We use three methods to identify this:
            1. Metadata analysis (looking into the C2PA data) -> Very useful for low-hanging fruits
            2. DeepScan's AI face verification -> Works only if faces are detected in the image
            3. Hacked `isgen.ai` services. This is slightly illegal but they haven't made their APIs available!
    """

    @staticmethod
    def metadata_analysis(image_path: str) -> Dict[str, str]:
        """
        Extracts the c2pa metadata from the image and returns that as a dictonary value. This is using
        the StaticImageExtractionEngine's extract_metadata function with the c2pa and exiftool flags
        enabled. This returns both the exifdata and the c2pa data.

        Args:
                image_path: Path to the image file
        Returns:
                Dict["exifdata": "val", "c2padata": "val"]
        """

        extracted_metadata = StaticImageExtractionEngine.extract_metadata(
            image_path=image_path, use_exif_only=True, use_c2pa_only=True
        )

        """
        This extracted_metadata is of the form:
            {
                "exiftool": "its data",
                "C2PA_metadata": "its data"
            }

        We'll just return this as it is and let the model make the inference.
        """

        return extracted_metadata

    @staticmethod
    def deepscan_fake_image_verification(
        image_path: str,
    ) -> List[Dict[str, Union[bool, str, None]]]:
        """
        Note: This was earlier in the image analysis part of the code base. Now has been moved here.
        (make the necessary migrations, don't keep it in both the places)

        This engine is used to verify if the image is AI generated or not. It uses the DeepScan model
        to verify this ONLY for portraits. If the image is not a portrait, this won't work.

        Additionally, this model is a little weak, as in, it can detect only the very obvious ones!

        Args:
                image_path: path to the image fiel
        Returns:
                List<Dict> containing:
                - is_real <boolean>
                - antispoof_score <Int> -> How real or fake
        """

        result = []
        try:
            face_objs = DeepFace.extract_faces(
                img_path=image_path,
                anti_spoofing=True,
            )
        except ValueError:
            return {
                "is_real": None,
                "antispoof_score": None,
                "is_face": "Couldn't detect faces in the provided image",
            }

        for face in face_objs:
            result.append({"is_real": face["is_real"], "antispoof_score": face["antispoof_score"]})

        return result

    @staticmethod
    def isgsenAI(image_path: str) -> Union[Dict[str, str], None]:
        """
        We don't need any session cookies if we do this using playwright. I have the script written inside utils directory.
        There is only one caveat, we'll have to run this with headless=False because for this to work we probably need the
        javascript to render.

        Its however much safer than asking people to login to their service for which I will have to ask for their creds
        which I don't want to do. So, we're gonna let this one be.

        If the user doesn't have playwright installed for some reason, then we default back to the old code. In this case,
        they will have to find and setup the keys themselves.

        Args:
                image_path: Path to the image which needs to be scanned for AI interference
        Returns:
                Dict[str, str]: Indicating in percentage how much of it was AI and how much was human (for images, its either
                100% AI or 100% human, nothing in between which is right!)
        """

        playwright_output = asyncio.run(upload_via_playwright(image_path))

        if playwright_output is None:
            # This means playwright hasn't been installed in the system and we can default back to the old code
            url = Config.API.isgen.endpoint_url

            headers = {
                "Accept": "*/*",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "apikey,authorization,x-client-info",
                "Origin": Config.API.isgen.base_url,
                "User-Agent": UserAgents.common_linux,
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Dest": "empty",
                "Referer": Config.API.isgen.base_url,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            }

            response = requests.options(url, headers=headers)

            """
            The bearer token contains some PPI and its not going to last always (unlike the API key). To obtain the API
            key and the bearer token, follow these steps:

            1. head over to https://isgen.ai/ai-image-detector
            2. Login (I am not sure why this helps but you get a different bearer token when you do login vs. when you don't)
               And whenever I didn't login, the API-key was the same as the bearer token. But using them didn't work! I had to
               use the `logged in` bearer key so I am suspecting firebase's involvement in this.
            3. Upload an image (any)
            4. Open the inspect tool to the networks tab
            5. Click the upload button and listen for requests, specially to `https://api.isgen.ai/functions/v1/detect-image`
               This will show up as the name `detect-image`.
            6. You will find your bearer key and the API-key in the request headers.

            Note: The bearer token will not last long. So, you'll have to generate a fresh one for every session
                  if you don't install playwright!
            """

            headers = {
                "Authorization": f"Bearer {os.getenv('isgen_bearer')}",
                "Apikey": Config.API.isgen.api_key,  # Similarly we'll need a way to get this for the user by default
                "User-Agent": UserAgents.common_linux,
                "Accept-Language": "en-GB,en;q=0.9",
                "Origin": Config.API.isgen.base_url,
                "Referer": Config.API.isgen.base_url,
            }

            filename = os.path.basename(image_path)

            files = {"image": (filename, open(image_path, "rb"), "image/png")}

            response = requests.post(url, headers=headers, files=files)
            # print(response.status_code, response.text, response.headers, response.content)

            if response.status_code == 401:
                log.error(
                    "Atlas is using an expired/invalid JWT. Please provide one in the enviornment"
                )
                return None

            return {
                "status_code": response.status_code,
                "decision": response.text,
            }

        return playwright_output  # If this is not none then it will be the decision

    @staticmethod
    def combined_AI_image_verification(image_path: str) -> Dict[str, Dict[str, Union[str, dict]]]:
        """
        A function that combines all the above approaches and returns so we don't have to run them individually

        Args:
            image_path: The image path for analysis
        Returns:
            {
                "c2paheaders": {
                    "status": "found|notfound",
                    "value": "None|actualvalue",
                },
                "exifheaders": {
                    "status": "found|notfound",
                    "value": "None|actualvalue",
                },
                "deepface": {
                    "status": "found|notfound",  # Faces present or not present
                    "value": "None|actualvalue",
                },
                "isgenai": {
                    "status": "found|notfound",    # depending on status code
                    "value": "response.text"
                }
            }
        """
        result: Dict[str, Dict[str, Union[str, dict]]] = {
            "c2paheaders": {"status": "notfound", "value": None},
            "exifheaders": {"status": "notfound", "value": None},
            "deepface": {"status": "notfound", "value": None},
            "isgenai": {"status": "notfound", "value": None},
        }

        # Metadata analysis first
        try:
            metadata = VerifyAIGeneratedImageEngine.metadata_analysis(image_path)
            if metadata:
                if "C2PA_metadata" in metadata and metadata["C2PA_metadata"]:
                    result["c2paheaders"]["status"] = "found"
                    result["c2paheaders"]["value"] = metadata["C2PA_metadata"]

                if "exiftool" in metadata and metadata["exiftool"]:
                    result["exifheaders"]["status"] = "found"
                    result["exifheaders"]["value"] = metadata["exiftool"]
        except Exception as e:
            log.error(f"Metadata analysis failed: {e}")

        # Deepface's analysis next
        try:
            deepface_result = VerifyAIGeneratedImageEngine.deepscan_fake_image_verification(
                image_path
            )
            if deepface_result:
                result["deepface"]["status"] = "found"
                result["deepface"]["value"] = deepface_result
        except Exception as e:
            log.error(f"Deepface analysis failed: {e}")

        # Isgen API check
        try:
            isgen_result = VerifyAIGeneratedImageEngine.isgsenAI(image_path)
            if isgen_result and "status_code" in isgen_result:
                if isgen_result["status_code"] == 200:
                    result["isgenai"]["status"] = "found"
                    result["isgenai"]["value"] = isgen_result.get("decision", None)
                else:
                    result["isgenai"]["value"] = f"Error {isgen_result['status_code']}"
        except Exception as e:
            log.error(f"isgen.ai verification failed: {e}")

        return result

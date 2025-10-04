# Reference: https://github.com/serengil/deepface?tab=readme-ov-file
from typing import Dict, List

from oatlas import logger

log = logger.get_logger()

try:
    from deepface import DeepFace
except Exception as e:
    log.error(f"Couldn't import DeepFace due to the following error: {e}")
    log.error("Please resolve if you want to use the DeepScanEngine")

from oatlas.config import Config
from oatlas.tools.image_analysis.utils import extract_text_from_image_advanced
from oatlas.utils.die import die_failure

# Supressing CUDA warnings
# os.environ["CUDA_VISIBLE_DEVICES"] = ""
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class DeepScanEngine:
    """
    This engine houses functions for performing specific feature extractions on
    real human and scenic images.

    Functions using DeepFace:
        1. Verify if two images are of the same people
        2. Analyse facial attributes
        3. Detect AI generated images
        4. OCR text extraction
    Functions using VertexAI Image Analysis:
        We'll see if any are necessary
    """

    @staticmethod
    def OCR_analysis(image_path: str) -> str:
        """
        Performs an OCR analysis on the image to extract textual information
        """
        # Well I have the image extraction ready already for the browser automation case, I can just probably use that
        extracted_text = extract_text_from_image_advanced(image_path)
        return extracted_text

    @staticmethod
    def verify_similar_faces(image_path_1: str, image_path_2: str) -> Dict:
        """
        Runs the DeepFace image verification scan (need not be potraits)

        Args:
            image_path_1: path to the first image as a string
            image_path_2: path to the second image as a string
        Return:
            Dictionary containing:
            - a boolean value for verification status,
            - value for how far apart the images really are
            - the confidence threshold for the prediction
        """

        result = {}
        try:
            output = DeepFace.verify(
                img1_path=image_path_1,
                img2_path=image_path_2,
                model_name=Config.settings.DeepFace_model_name,
                detector_backend=Config.settings.DeepFace_fast_backend,
                align=True,
            )
        except ValueError:
            return {
                "is_face": "Couldn't detect faces in the provided image",
                "verified": None,
                "distance": None,
                "confidence": None,
            }

        if not output:
            die_failure("DeepFace failed to analyse the images")

        result["verified"] = output["verified"]
        result["distance"] = output["distance"]
        result["confidence"] = output["threshold"]

        return result

    @staticmethod
    def face_attribute_analysis(image_path: str) -> List:
        """
        Runs the DeepFace face analysis scan

        Args:
            image_path: path to the image file
        Returns:
            List<Dict> containing:
            - age
            - gender (dominant)
            - race (dominant)
            - emotion (dominant)
        """
        result = []

        try:
            output = DeepFace.analyze(
                img_path=image_path,
                actions=["age", "gender", "race", "emotion"],
            )
        except ValueError:
            return [
                {
                    "is_face": "Couldn't detect faces in the provided image",
                    "age": None,
                    "gender": None,
                    "race": None,
                    "emotion": None,
                }
            ]

        if not output:
            die_failure("DeepFace failed to analyze the image")

        assert isinstance(output, list), "DeepFace should've returned a list!"

        for face in output:
            result.append(
                {
                    "age": face["age"],
                    "gender": face["dominant_gender"],
                    "race": face["dominant_race"],
                    "emotion": face["dominant_emotion"],
                }
            )
        return result

    @classmethod
    def get_abbr():
        return "dsE"

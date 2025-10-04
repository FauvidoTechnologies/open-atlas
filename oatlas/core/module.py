from typing import List

from oatlas.logger import get_logger
from oatlas.tools import DeepScanEngine, StaticImageExtractionEngine

log = get_logger()


class Module:
    def analyse_image_dir(self, image_files: List) -> None:
        """
        Iterate over the images, extract relevant information using predefined models
        Args:
                image_files: Files containing target images
        Returns:
                logs
        """
        logs = {}

        for image in image_files:
            # Since each image name will be a path object, we can do this
            # Also, this can be made better by using the other tools that we have for image scans
            image_log = {}

            face_objs = DeepScanEngine.face_attribute_analysis(image)
            if any("is_face" in obj for obj in face_objs):
                # we'll have `is_face` only when we get a ValueError with no-faces-found
                # In which case we do an OCR analysis
                ocr_result = DeepScanEngine.OCR_analysis(image)
                image_log = {
                    "face-analysis-result": face_objs,
                    "ocr-result": ocr_result,
                }
            else:
                image_log = {"face-analysis-result": face_objs}

            # We're always going to extract the metadata for each image
            metadata = StaticImageExtractionEngine.extract_metadata(
                image, use_exif_only=True
            )  # placeholder function
            image_log["metadata"] = metadata

            logs[str(image)] = image_log

        return logs

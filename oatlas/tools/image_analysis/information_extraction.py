import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List

# Importing the exposed rust functions via pyo3 bindings
import rust
from c2pa import Reader, C2paError
from PIL import Image
from PIL.ExifTags import TAGS

from oatlas.config import Config
from oatlas.logger import get_logger

log = get_logger()


class StaticImageExtractionEngine:
    """
    Class for Image extraction processes.
    """

    @staticmethod
    def extract_metadata(
        image_path: str, use_exif_only: bool = False, use_c2pa_only: bool = False
    ) -> Dict[str, str]:
        """
        Image metadata extraction function. This is the best first approach to get information
        on an image. This is also the first approach to identify if an image is AI generated or
        now. Sometimes we can get some low-hanging fruits by reading the metadata.

        Args:
            image_path: Full path to the image you want to scan
            use_exif_only: Flag to indicate if only the raw exiftool data is required
            use_c2pa_only: Flag to indeicate if only the raw c2pa data is required
        Returns:
            Dict[str,str] -> A full description of the metadata stored as a key-value pair

        If the use_exif_only flag is enabled, only the exiftool returned, and if use_c2pa_only flag
        is enabled then only the c2pa data is returned. Atlas doesn't need to know about these flags
        because it should never set these as True anyways.

        The following functions are run one by one:

        1. Normal metadata analysis using Pillow
        2. Exiftool analysis using subprocesses and output captures from stdout
        3. c2pa analysis (for ones that have that metadata -> Usually OpenAI models)

        example c2pa code: (the library has been added to poetry)

        ```py
            from c2pa import Reader

            with Reader("~/Downloads/chatgptimage.png") as reader:
                manifest_json = reader.json()

            print(manifest_json)
        ```

        Note that according to their library, only the Reader class works now, and everything else
        is deprecated. So, just stick to this.

        In case both the flags are set, we return both the values as a dictionary

        """
        metadata, exif_only, c2pa_only, exif_c2pa = {}, {}, {}, {}

        # Basic pillow metadata
        try:
            image = Image.open(image_path)
            metadata.update(
                {
                    "Filename": image.filename,
                    "Image Size": str(image.size),
                    "Image Height": str(image.height),
                    "Image Width": str(image.width),
                    "Image Format": str(image.format),
                    "Image Mode": str(image.mode),
                    "Image is Animated": str(getattr(image, "is_animated", False)),
                    "Frames in Image": str(getattr(image, "n_frames", 1)),
                }
            )
        except Exception as e:
            log.error(f"There was a problem in the basic metadata scan: {e}")
            metadata[
                "Pillow Error"
            ] = f"Failed to load image: {e}"  # Saving it so that the brain knows this was an issue
            return metadata  # Cannot proceed further without at least opening it

        # Exifdata via Pillow
        try:
            exif_data = image._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata[f"EXIF_{tag}"] = str(value)
        except Exception as e:
            metadata["EXIF Error"] = f"Failed to parse EXIF: {e}"

        # Running exiftool as a subprocess (this has been added as a dependency)
        try:
            result = subprocess.run(
                [
                    "exiftool",
                    "-a",
                    "-u",
                    "-g1",
                    "-json",
                    image_path,
                ],  # raw extract everything setup
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                exiftool_data = json.loads(result.stdout)
                metadata["EXIFTOOL_RAW"] = exiftool_data
                # I am using this for preliminary analysis on entered images
                if use_exif_only and not use_c2pa_only:
                    exif_only["exiftool"] = exiftool_data
                    return exif_only
                elif use_exif_only and use_c2pa_only:
                    exif_c2pa["exiftool"] = exiftool_data
            if result.stderr:
                metadata["Exiftool Warning"] = result.stderr.strip()

        except FileNotFoundError:
            log.error("Exiftool is not installed! Please install it to get its output as well")
        except Exception as e:
            log.error(f"There was an error in running exiftool: {e}")

        # C2PA metadata -> Slowly gaining traction for security compliance, OpenAI already uses this
        try:
            with Reader(image_path) as reader:
                manifest_json = reader.json()
                metadata["C2PA_Metadata"] = manifest_json
                if use_c2pa_only and not use_exif_only:
                    c2pa_only["C2PA_Metadata"] = manifest_json
                    return c2pa_only
                elif use_exif_only and use_c2pa_only:
                    exif_c2pa["C2PA_Metadata"] = manifest_json
                    return exif_c2pa  # We can return it here now
        except C2paError.Io:
            metadata["C2PA_Metadata"] = "Image doesn't contain C2PA metadata"
            if use_c2pa_only:
                c2pa_only["C2PA_Metadata"] = "Image doesn't contain C2PA metadata"
                return c2pa_only
            elif use_exif_only and use_c2pa_only:
                exif_c2pa["C2PA_Metadata"] = "Image doesn't contain C2PA metadata"
                return exif_c2pa
        except Exception as e:
            log.error(f"There was an error in running c2pa extraction: {e}")

        return metadata

    @staticmethod
    def scan_firmware(image_path) -> str:
        """
        Uses Binwalk as a rust binding to scan for firmware data

        Args: image_path -> path to where the file is
        Returns: string of python dictionaries holding data

        For more information on return type: atlas/utils/tool_descriptions
        """
        result = rust.scan_firmware(image_path)
        return json.loads(result)

    @staticmethod
    def extract_firmware(
        input_path: str, skip: int, count: int, output_file_name: str, block_size: int = 1
    ):
        """
        Extracts the image by reading the specified bytes. The output_file
        by default is defined inside config (binwalk_extracted_output_dir).
        """
        output_file = Config.path.binwalk_extracted_output_dir / output_file_name
        try:
            with Path(input_path).open("rb") as f_in:
                # Calculate the seek position in bytes
                seek_position = skip * block_size
                f_in.seek(seek_position)

                # Calculate the number of bytes to read
                bytes_to_read = count * block_size

                # Read the data
                data = f_in.read(bytes_to_read)

            with open(output_file, "wb") as f_out:
                f_out.write(data)

            log.excited(f"Successfully extracted {bytes_to_read} bytes to '{output_file}'")
            return {"extracted_bytes": bytes_to_read, "output_file": output_file}

        except FileNotFoundError:
            log.error(f"The input file '{input_path}' was not found.")
            return None
        except Exception as e:
            log.error(f"Could not extract due to the following reason: {e}")
            return None

    @staticmethod
    def extract_strings(input_path: str, min_length: int = 4) -> List:
        """
        Native python implementation of a string extraction for a binary file

        Returns:
            List<strings> for all strings that are available
        """

        with Path(input_path).open("rb") as f:
            data = f.read()

        # Regex for printable ASCII and UTF-16LE sequences of printable ASCII
        ascii_re = re.compile(rb"[ -~]{%d,}" % min_length)
        utf16le_re = re.compile(rb"(?:[ -~]\x00){%d,}" % min_length)

        matches = []
        for m in ascii_re.finditer(data):
            matches.append((m.start(), m.group().decode("ascii", errors="ignore")))
        for m in utf16le_re.finditer(data):
            matches.append((m.start(), m.group().decode("utf-16le", errors="ignore")))

        # Sorting by position in file to match GNU `strings` order
        matches.sort(key=lambda x: x[0])

        return [s for _, s in matches]

    @classmethod
    def get_abbr():
        return "siE"

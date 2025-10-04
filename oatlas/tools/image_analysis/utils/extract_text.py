import cv2
import numpy as np
import pytesseract
from PIL import Image

# IMPORTANT: You may need to set the path to your Tesseract executable.
# For Windows, it might look something like this:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_skew_angle(image):
    """
    Calculates the skew angle of an image.
    This function uses a probabilistic Hough Line Transform to detect text lines
    and determines the average angle to correct for image tilt.
    """
    # Convert image to grayscale for line detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Canny edge detection to find edges in the image
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Find lines using the Hough Line Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    if lines is None:
        return 0  # No lines found, assume no skew

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Calculate angle of the line in radians
        angle = np.arctan2(y2 - y1, x2 - x1)
        angles.append(angle)

    # Calculate the average angle in degrees
    avg_angle = np.mean(angles)
    skew_angle = np.degrees(avg_angle)

    # Tesseract often works best with text that is horizontally aligned.
    # We want to correct the angle to be as close to 0 as possible.
    # If the text is tilted a little up or down, this helps straighten it.
    return skew_angle


def deskew_image(image, angle):
    """
    Rotates an image to correct for skew.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    # Get the rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # Perform the rotation, filling the new areas with the background color
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def extract_text_from_image_advanced(image_path):
    """
    Extracts text from an image using Tesseract OCR with several preprocessing steps.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The extracted text from the image.
    """
    try:
        # Step 1: Load the image using OpenCV
        img = cv2.imread(image_path)

        if img is None:
            return f"Error: Could not read image from path '{image_path}'"

        # Step 2: Denoising (remove noise while preserving edges)
        # This is particularly useful for noisy or blurry scanned documents.
        # It's an optional but highly effective step.
        denoised_img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

        # Step 3: Deskewing (correcting for rotation)
        # Tesseract works best with horizontally aligned text. This step
        # corrects for any tilt in the document.
        angle = get_skew_angle(denoised_img)
        deskewed_img = deskew_image(denoised_img, angle)

        # Step 4: Convert to grayscale
        gray = cv2.cvtColor(deskewed_img, cv2.COLOR_BGR2GRAY)

        # Step 5: Rescaling (for better DPI)
        # Tesseract's documentation suggests a DPI of at least 300.
        # Resizing the image can help improve accuracy for low-resolution scans.
        # We increase the image size by a factor of 2.
        resized_gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Step 6: Binarization (thresholding)
        # Convert the image to pure black and white for maximum contrast.
        # Otsu's method automatically determines the optimal threshold.
        thresh = cv2.threshold(resized_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Step 7: Tesseract configuration
        # --oem 3: Use the default OCR Engine Mode (LSTM + Legacy)
        # --psm 6: Assume a single uniform block of text
        custom_config = r"--oem 3 --psm 6"

        # Step 8: Use pytesseract to extract text from the preprocessed image
        text = pytesseract.image_to_string(Image.fromarray(thresh), config=custom_config)

        return text
    except Exception as e:
        return f"An error occurred: {e}"

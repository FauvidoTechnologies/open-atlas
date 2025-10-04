import os
import shutil
import subprocess
import sys
from pathlib import Path

import requests

from oatlas.config import Config
from oatlas.logger import get_logger
from oatlas.utils.die import die_failure

log = get_logger()


class PlaywrightDependencies:
    """
    Class for handling playwright's dependencies, should be called at the start of Atlas' execution
    and before actual browser automation
    """

    @staticmethod
    def check_playwright_browsers_installed() -> bool:
        """
        Check if Playwright browsers are installed by running `playwright install --dry-run`
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )
            # If dry-run shows no browsers to install, they are already installed
            return "No browsers to install" in result.stdout
        except Exception:
            return False

    @staticmethod
    def install_playwright_browsers():
        """
        Install Playwright browsers automatically.
        """
        log.info("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
        log.info("Playwright browsers installed successfully")

    @staticmethod
    def check_missing_dependencies():
        """
        Run a test to identify missing dependencies using `playwright install-deps --dry-run`.
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install-deps", "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout.strip() + "\n" + result.stderr.strip()
            # Filter only the lines that mention missing libraries
            missing_lines = [
                line
                for line in output.splitlines()
                if "Missing" in line or line.strip().endswith(".so") or "║" in line
            ]
            if missing_lines:
                log.warn("Missing system dependencies detected:")
                print("\n".join(missing_lines))
                log.info("Please install them manually using your package manager or run:")
                log.excited("poetry run playwright install-deps")
            else:
                log.info("No missing system dependencies detected")
        except FileNotFoundError:
            log.error("Could not run playwright. Is it installed in this environment?")

    def handle_dependencies(self):
        # Step 1: Check if browsers are installed
        log.info("Checking if Playwright browsers are installed")
        if self.check_playwright_browsers_installed():
            log.info("Playwright browsers already installed")
        else:
            log.warn("Playwright browsers not found.")
            choice = input("Do you want to install them automatically? (y/n): ").strip().lower()
            if choice == "y":
                self.install_playwright_browsers()
            else:
                log.warn("Please install browsers manually with:")
                print("poetry run playwright install")
                log.warn("Proceeding anyways!")
        # Step 2: Check missing system dependencies
        log.info("Checking for missing system dependencies")
        self.check_missing_dependencies()


class DeepFaceDependencies:
    """
    Install DeepFace dependencies for image analysis
    """

    BASE_DIR = Config.path.deepface_base_dir  # The default cache location for deepface
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _download_file(url: str, save_path: Path):
        """
        Download a file from a URL to the specified save path.
        """
        if save_path.exists():
            log.verbose_info(f"Already exists: {save_path}")
            return str(save_path)

        log.info(f"Downloading {url} -> {save_path}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        log.excited(f"Downloaded: {save_path}")
        return str(save_path)

    @staticmethod
    def install_verification_weights():
        """
        Installing weights for image comparisons between two faces (VGG-Face)
        """
        url = "https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.h5"
        save_path = DeepFaceDependencies.BASE_DIR / "vgg_face_weights.h5"
        return DeepFaceDependencies._download_file(url, save_path)

    @staticmethod
    def install_attribute_analysis_weights():
        """
        Installing weights for face attribute analysis
        """
        urls = [
            "https://github.com/serengil/deepface_models/releases/download/v1.0/gender_model_weights.h5",
            "https://github.com/serengil/deepface_models/releases/download/v1.0/facial_expression_model_weights.h5",
            "https://github.com/serengil/deepface_models/releases/download/v1.0/race_model_single_batch.h5",
            "https://github.com/serengil/deepface_models/releases/download/v1.0/age_model_weights.h5",
        ]

        downloaded_files = []
        for url in urls:
            filename = url.split("/")[-1]
            save_path = DeepFaceDependencies.BASE_DIR / filename
            downloaded_files.append(DeepFaceDependencies._download_file(url, save_path))

        return downloaded_files

    @staticmethod
    def install_deepfake_detection_weights():
        """
        Placeholder for deepfake detection weights installation
        """
        url = "https://github.com/serengil/deepface_models/releases/download/v1.0/facenet512_weights.h5"

        save_path = DeepFaceDependencies.BASE_DIR / "facenet512_weights.h5"
        return DeepFaceDependencies._download_file(url, save_path)

    def handle_dependencies(self):
        log.info("Installing DeepFace weights")
        self.install_attribute_analysis_weights()
        self.install_verification_weights()
        self.install_deepfake_detection_weights()
        log.info("Deepface weights installation completed!")


class RustDependencies:
    """
    Class for handling Rust and Cargo dependencies, required for pyo3 bindings.
    """

    @staticmethod
    def is_cargo_installed() -> bool:
        """
        Check if cargo is installed and available in the system's PATH.
        `shutil.which` is a reliable way to check for an executable in the PATH.
        """
        return shutil.which("cargo") is not None

    @staticmethod
    def install_rust_toolchain():
        """
        Install the Rust toolchain (including cargo) using the official rustup script.
        This is a non-interactive installation.
        """
        log.info("Installing Rust toolchain (cargo, rustc)... This may take a few minutes.")
        log.warn("Ensure that you have the following dependencies already installed via apt")
        log.info("sudo apt install build-essential libfontconfig1-dev liblzma-dev")
        try:
            command = "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
            # We run the command via shell, which is necessary for the pipe `|` to work.
            # While `shell=True` has security implications, this specific command is trusted.
            result = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True
            )
            log.excited("Rust toolchain installed successfully!")
            log.verbose_info(f"Install log: {result.stdout}")

            # The installer modifies shell profile files (e.g., .bashrc, .profile),
            # but the changes don't affect the current running process.
            # We must manually add cargo to the PATH for the current session.
            cargo_path = Path.home() / ".cargo" / "bin"
            os.environ["PATH"] = str(cargo_path) + os.pathsep + os.environ["PATH"]
            log.verbose_info(f"Temporarily added '{cargo_path}' to PATH for this session.")
            log.warn(
                "You may need to restart your terminal for 'cargo' to be available in new sessions."
            )

        except subprocess.CalledProcessError as e:
            log.error("Failed to install Rust toolchain.")
            log.verbose_info(f"Stderr: {e.stderr}")
            log.error("Please try installing it manually by visiting https://rustup.rs/")
        except Exception as e:
            log.error(f"An unexpected error occurred during Rust installation: {e}")

    def handle_dependencies(self):
        """
        Check for cargo and prompt for installation if missing.
        """
        log.verbose_info("Checking for Rust (cargo) dependency...")
        if self.is_cargo_installed():
            log.excited("Rust (cargo) is already installed.")
        else:
            log.warn("Rust dependency 'cargo' is not found.")
            log.warn("This is required for compiling binwalk plugins")
            choice = (
                input("Do you want to install the Rust toolchain automatically? (y/n): ")
                .strip()
                .lower()
            )
            if choice == "y":
                self.install_rust_toolchain()
            else:
                log.warn("Skipping Rust installation. Some features may not be available.")
                log.warn("To install it manually, visit https://rustup.rs/")


class TesseractDependencies:
    """
    Class for handling Tesseract OCR dependencies
    """

    @staticmethod
    def is_tesseract_installed() -> bool:
        """
        Check if Tesseract is installed and available in the system's PATH.
        `shutil.which` is a reliable way to check for an executable in the PATH.
        """
        return shutil.which("tesseract") is not None

    @staticmethod
    def install_tesseract():
        """
        Instructions for installing the Tesseract OCR engine.
        There is no single command to install Tesseract across all operating systems.
        This method provides guidance based on the detected OS.
        """
        log.warn("Tesseract OCR is not found.")

        if os.uname().sysname.lower() == "darwin":
            log.info("For macOS: Use Homebrew to install Tesseract.")
            log.info("Install Tesseract: brew install tesseract")
        elif os.uname().sysname.lower() == "linux":
            log.info("For Linux systems use apt-get")
            log.info("sudo apt-get install tesseract-ocr")
        else:
            log.info(
                "For other operating systems, please refer to the official Tesseract installation documentation:"
            )
            log.info("https://tesseract-ocr.github.io/tessdoc/Installation.html")

        choice = (
            input("Do you want to continue without installing Tesseract's OCR?: (y/n)")
            .strip()
            .lower()
        )
        if choice == "y":
            log.warn("Continuing without OCR")
        else:
            die_failure("Please install Tesseract's OCR using the provided instructions")

    def handle_dependencies(self):
        """
        Check for Tesseract and prompt for installation if missing.
        """
        log.verbose_info("Checking for Tesseract dependency...")
        if self.is_tesseract_installed():
            log.excited("Tesseract is already installed.")
        else:
            self.install_tesseract()


class HandleDependencies:
    """
    The only class required for managing dependencies
    """

    tesseract = TesseractDependencies
    rust = RustDependencies
    deepface = DeepFaceDependencies
    playwright = PlaywrightDependencies

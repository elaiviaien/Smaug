""" A module to build a project."""

import os
import shutil
import subprocess
import sys
import tempfile
import venv

from .logger import setup_logger

logger = setup_logger(f"smaug_{os.getpid()}")


class Builder:
    """Builds a project."""

    def __init__(self):
        self.build_dir = tempfile.mkdtemp(prefix="smaug_")
        self.venv_dir = os.path.join(self.build_dir, "venv")
        logger.info(
            "Initialized Builder with build_dir: %s and venv_dir: %s",
            self.build_dir,
            self.venv_dir,
        )

    def copy_files(self, dir_path: str) -> None:
        """Copy files from the given directory to the build directory."""
        logger.info("Starting to copy files from %s to %s", dir_path, self.build_dir)
        for item in os.listdir(dir_path):
            s = os.path.join(dir_path, item)
            d = os.path.join(self.build_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        logger.info("Finished copying files from %s to %s", dir_path, self.build_dir)

    def create_venv(self) -> None:
        """Create a virtual environment."""
        logger.info("Starting to create virtual environment in %s", self.venv_dir)
        venv.create(self.venv_dir, with_pip=True)
        logger.info("Finished creating virtual environment in %s", self.venv_dir)

    def install_dependencies(self) -> None:
        """Install dependencies from requirements.txt."""
        pip_exe = os.path.join(self.venv_dir, "bin", "pip")
        logger.info("Starting to install dependencies using %s", pip_exe)
        try:
            requirements_abs_path = os.path.join(self.build_dir, "requirements.txt")
            result = subprocess.run(
                [pip_exe, "install", "-r", requirements_abs_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            logger.error("Command %s failed with return code %s", e.cmd, e.returncode)
            logger.info("Output: %s", e.stdout.decode())
            logger.error("Error: %s", e.stderr.decode())
        logger.info("Finished installing dependencies")

    def build(self, dir_path: str) -> None:
        """Build the project."""
        logger.info("Starting to build the project from %s", dir_path)
        self.copy_files(dir_path)
        self.create_venv()
        logger.info("Files in directory: %s", os.listdir(self.build_dir))
        if "requirements.txt" in os.listdir(self.build_dir):
            self.install_dependencies()
        logger.info("Finished building the project from %s", dir_path)

    def __del__(self) -> None:
        logger.info("Deleting the build directory %s", self.build_dir)
        shutil.rmtree(self.build_dir)
        logger.info("Deleted the build directory %s", self.build_dir)

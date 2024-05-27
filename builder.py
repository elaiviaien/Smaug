""" A module to build a project."""
import os
import shutil
import subprocess
import tempfile
import venv


class Builder:
    """Builds a project."""
    def __init__(self):
        self.build_dir = tempfile.mkdtemp(prefix="smaug_")
        self.venv_dir = os.path.join(self.build_dir, "venv")

    def copy_files(self, dir_path):
        """Copy files from the given directory to the build directory."""
        for item in os.listdir(dir_path):
            s = os.path.join(dir_path, item)
            d = os.path.join(self.build_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    def create_venv(self):
        """Create a virtual environment."""
        venv.create(self.venv_dir, with_pip=True)

    def install_dependencies(self):
        """Install dependencies from requirements.txt."""
        pip_exe = os.path.join(self.venv_dir, "bin", "pip")
        try:
            requirements_abs_path = os.path.join(
                self.build_dir, "requirements.txt")
            result = subprocess.run(
                [pip_exe, "install", "-r", requirements_abs_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(
                f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
            print(f"Output: {e.output.decode()}")
            print(f"Error: {e.stderr.decode()}")

    def build(self, dir_path):
        """Build the project."""
        self.copy_files(dir_path)
        self.create_venv()
        print("Files in directory:", os.listdir(self.build_dir))
        if "requirements.txt" in os.listdir(self.build_dir):
            self.install_dependencies()

    def __del__(self):
        shutil.rmtree(self.build_dir)

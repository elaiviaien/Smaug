import os
import shutil
import subprocess
import tempfile
import venv


class Builder:
    def __init__(self):
        self.build_dir = tempfile.mkdtemp(prefix='smaug_')
        self.venv_dir = os.path.join(self.build_dir, 'venv')

    def copy_files(self, dir_path):
        for item in os.listdir(dir_path):
            s = os.path.join(dir_path, item)
            d = os.path.join(self.build_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    def create_venv(self):
        print(self.venv_dir)
        venv.create(self.venv_dir, with_pip=True)

    def install_dependencies(self):
        pip_exe = os.path.join(self.venv_dir, 'bin', 'pip')
        try:
            requirements_abs_path = os.path.join(self.build_dir, 'requirements.txt')
            result = subprocess.run([pip_exe, 'install', '-r', requirements_abs_path],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
            print(f"Output: {e.output.decode()}")
            print(f"Error: {e.stderr.decode()}")

    def build(self, dir_path):
        self.copy_files(dir_path)
        self.create_venv()
        print("Files in directory:", os.listdir(self.build_dir))
        if 'requirements.txt' in os.listdir(self.build_dir):
            self.install_dependencies()

    def __del__(self):
        shutil.rmtree(self.build_dir)

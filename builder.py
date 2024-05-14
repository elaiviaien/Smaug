import os
import shutil
import subprocess
import tempfile
import venv


class Builder:
    def __init__(self):
        self.work_dir = tempfile.mkdtemp(prefix='smaug_')
        self.venv_dir = os.path.join(self.work_dir, 'venv')

    def copy_files(self, dir_path):
        files = [os.path.join(dir_path, file) for file in os.listdir(dir_path)]
        for file in files:
            shutil.copy(file, self.work_dir)

    def create_venv(self):
        print(self.venv_dir)
        venv.create(self.venv_dir, with_pip=True)

    def install_dependencies(self):
        pip_exe = os.path.join(self.venv_dir, 'bin', 'pip')
        try:
            requirements_abs_path = os.path.join(self.work_dir, 'requirements.txt')
            result = subprocess.run([pip_exe, 'install', '-r', requirements_abs_path],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
            print(f"Output: {e.output.decode()}")
            print(f"Error: {e.stderr.decode()}")

    def build(self, files):
        self.copy_files(files)
        self.create_venv()
        print("Files in directory:", os.listdir(self.work_dir))
        self.install_dependencies()

    def __del__(self):
        shutil.rmtree(self.work_dir)

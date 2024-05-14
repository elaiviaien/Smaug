import venv
import subprocess
import os
import pwd
import grp
import tempfile
from builder import Builder


class ScriptRunner:
    def __init__(self, script_path):
        self.script_path = script_path
        self.builder = Builder()
        self.work_dir = self.builder.work_dir

    @property
    def script_path(self):
        return self._script_path

    @script_path.setter
    def script_path(self, path):
        if os.path.isabs(path):
            self._script_path = path
        else:
            self._script_path = os.path.abspath(path)
        if not os.path.exists(self._script_path):
            raise FileNotFoundError(f"Script {self._script_path} does not exist")

    def run_as_temp_user(self):
        username = tempfile.mktemp()

        subprocess.run(['useradd', '-m', username], check=True)

        uid = pwd.getpwnam(username).pw_uid
        gid = grp.getgrnam(username).gr_gid

        os.setgid(gid)
        os.setuid(uid)

        subprocess.run(['userdel', '-r', username], check=True)

    def change_working_directory(self):
        script_dir = os.path.dirname(os.path.abspath(self.script_path))
        os.chdir(script_dir)

    def create_venv(self):
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(self.venv_dir)

    def mount_directory(self, source, target):
        subprocess.run(['mount', '--bind', source, target], check=True)

    def run_script_in_venv(self):
        python_exe = f"{self.venv_dir}/bin/python"
        process = subprocess.Popen([python_exe, self.script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("Output:", stdout.decode())
        if stderr:
            print("Error:", stderr.decode())

    def run(self):
        self.change_working_directory()
        self.create_venv()
        self.run_script_in_venv()


class IsolatedScriptRunner(ScriptRunner):
    def __init__(self,  script_path):
        self.script_path = script_path

    def isolate_script(self):
        script_dir = os.path.dirname(os.path.abspath(self.script_path))
        isolate_params = [
            'unshare',  # Unshare the namespaces
            '-m',  # Mount namespace
            '-r',  # UTS namespace
            '-n',  # Network namespace
            '-i',  # IPC namespace
            '-p',  # PID namespace
            '--fork',  # Fork the process
            '--mount-proc=%s/proc' % script_dir  # Mount the proc filesystem
        ]
        subprocess.run(isolate_params)

    def run(self):
        self.change_working_directory()
        self.create_venv()
        self.isolate_script()
        self.run_script_in_venv()

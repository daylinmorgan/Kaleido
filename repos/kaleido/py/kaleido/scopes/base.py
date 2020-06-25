import subprocess
import json
import base64
from threading import Lock
import os
import sys

executable_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'executable', 'kaleido')


class BaseScope(object):
    _json_encoder = None

    def __init__(self, disable_gpu=True, suppress_stderr=True, **kwargs):

        # Properties
        self.suppress_stderr = suppress_stderr

        # TODO: Validate disable_gpu
        kwargs['disable_gpu'] = disable_gpu

        # Build process arguments list
        self.proc_args = [executable_path, self.scope_name]
        for k, v in kwargs.items():
            if v is True:
                flag = '--' + k.replace("_", "-")
            elif v is False or v is None:
                # Logical flag set to False, don't inlude argument
                continue
            else:
                # Flag with associated value
                flag = '--' + k.replace("_", "-") + "=" + repr(str(v))
            self.proc_args.append(flag)

        # Launch subprocess
        self._proc = None
        self._proc_lock = Lock()

    def __del__(self):
        self._shutdown_kaleido()

    def _ensure_kaleido(self):
        if self._proc is None or self._proc.poll() is not None:
            with self._proc_lock:
                if self._proc is None or self._proc.poll() is not None:
                    # Wait on process if crashed to prevent zombies
                    if self._proc is not None:
                        self._proc.wait()

                    # Launch kaleido subprocess
                    # Note: shell=True seems to be needed on Windows to handle executable path with
                    # spaces.  The subprocess.Popen docs makes it sound like this shouldn't be
                    # necessary.
                    if self.suppress_stderr:
                        stderr = open(os.devnull, "wb")
                    else:
                        stderr = None

                    self._proc = subprocess.Popen(
                        self.proc_args,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=stderr,
                        shell=sys.platform == "win32"
                    )

                    # Read startup message and check for errors
                    startup_response_bytes = self._proc.stdout.readline()
                    startup_response = json.loads(startup_response_bytes.decode('utf-8'))
                    if startup_response.get("code", 0) != 0:
                        self._proc.wait()
                        raise ValueError(startup_response.get("message", "Failed to start kaleido executable"))

    def _shutdown_kaleido(self):
        if self._proc is not None:
            with self._proc_lock:
                if self._proc is not None:
                    if self._proc.poll() is None:
                        # Process still running, close stdin to tell kaleido to shut down gracefully
                        self._proc.stdin.close()

                    # wait for process to terminate if it was running, also prevent zombie process if
                    # process crashed on it's own
                    try:
                        self._proc.wait(timeout=2.0)
                    except:
                        # We tried to wait! Moving on...
                        pass

                    # Clear _proc property
                    self._proc = None

    @property
    def scope_name(self):
        raise NotImplementedError

    def to_image(self, figure, format="png", width=700, height=500, scale=1):
        # Ensure that kaleido subprocess is running
        self._ensure_kaleido()

        # Perform export
        export_spec = json.dumps({
            "figure": figure,
            "format": format,
            "width": width,
            "height": height,
            "scale": scale,
        }, cls=self._json_encoder).encode('utf-8')

        # Write to process and read result within a lock so that can be
        # sure we're reading the response to our request
        with self._proc_lock:
            # Write and flush spec
            self._proc.stdin.write(export_spec)
            self._proc.stdin.write("\n".encode('utf-8'))
            self._proc.stdin.flush()
            response = self._proc.stdout.readline()

        response = json.loads(response.decode('utf-8'))
        code = response.pop("code", 0)

        # Check for export error
        if code != 0:
            message = response.get("message", None)
            raise ValueError(
                "Image export failed with error code {code}: {message}".format(
                    code=code, message=message
                )
            )

        # Export successful
        img_string = response.pop("result", None)
        if format == 'svg':
            img = img_string.encode()
        else:
            img = base64.decodebytes(img_string.encode())
        return img
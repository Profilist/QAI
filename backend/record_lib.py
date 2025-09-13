"""
FFmpeg screen recorder helpers for Linux VMs (X11) without a web server.

Usage with computer.venv_exec:
  await computer.venv_exec("demo_venv", record_lib.start_recording, output_dir="/var/replays", fps=5)
  # ...
  await computer.venv_exec("demo_venv", record_lib.stop_recording)

Notes:
  - Each function is self-contained (no module-level helper dependencies),
    so execution environments that serialize only the function body will work.
  - State is stored at /tmp/cua_recorder/state.json
"""

import os
import json
import time
import signal
import platform
import subprocess
from pathlib import Path


def start_recording(output_dir=None, fps=None, width=None, height=None, display=None):
    """Start ffmpeg screen recording in background and persist PID.

    Returns a dict with { ok, path, pid, fps }.
    """
    # Local imports to support environments that serialize function bodies only
    import os as _os
    import json as _json
    import time as _time
    import subprocess as _subprocess
    from pathlib import Path as _Path

    state_dir = _Path("/tmp/cua_recorder"); state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / "state.json"

    # Load prior state
    prior = {}
    if state_path.exists():
        try:
            prior = _json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            prior = {}

    # If already recording, return
    pid = prior.get("pid")
    if isinstance(pid, int):
        try:
            _os.kill(pid, 0)
            # still alive
            return {"ok": False, "error": "already_recording", "path": prior.get("path"), "pid": pid}
        except Exception:
            pass

    # Prepare output and command
    fps_val = int(fps or _os.getenv("CUA_REPLAY_FPS", 5))
    out_dir = _Path(output_dir) if output_dir else _Path(_os.getenv("REPLAY_DIR", "/replays"))
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = _time.strftime("%Y%m%d_%H%M%S")
    output_path = out_dir / f"session_{stamp}.mp4"

    # Build ffmpeg command (Linux X11)
    vf = ["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2"]
    common = ["-y", "-framerate", str(fps_val)]
    dpy = display or _os.getenv("DISPLAY", ":0.0")
    size_args = []
    if width and height:
        size_args = ["-video_size", f"{width}x{height}"]
    cmd = [
        "ffmpeg",
        *common,
        *size_args,
        "-f", "x11grab",
        "-i", dpy,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        *vf,
        "-movflags", "+faststart",
        str(output_path),
    ]
    try:
        # Start detached so it survives beyond this function
        proc = _subprocess.Popen(
            cmd,
            stdin=_subprocess.PIPE,
            stdout=_subprocess.DEVNULL,
            stderr=_subprocess.DEVNULL,
            start_new_session=True,
        )
        new_state = {
            "pid": proc.pid,
            "path": str(output_path),
            "fps": fps_val,
            "started_at": _time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        try:
            state_path.write_text(_json.dumps(new_state, indent=2), encoding="utf-8")
        except Exception:
            pass
        return {"ok": True, "path": str(output_path), "pid": proc.pid, "fps": fps_val}
    except Exception as e:
        return {"ok": False, "error": repr(e)}


def stop_recording():
    """Stop ffmpeg recording using the persisted PID.

    Returns a dict with { ok, path }.
    """
    # Local imports for serialized execution environments
    import os as _os
    import json as _json
    import time as _time
    import signal as _signal
    from pathlib import Path as _Path

    state_path = _Path("/tmp/cua_recorder/state.json")
    data = {}
    if state_path.exists():
        try:
            data = _json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    pid = data.get("pid")
    if not isinstance(pid, int):
        return {"ok": False, "error": "not_recording"}
    try:
        _os.kill(pid, 0)
        alive = True
    except Exception:
        alive = False
    if not alive:
        return {"ok": False, "error": "not_recording"}
    try:
        _os.kill(pid, _signal.SIGTERM)
        # wait briefly
        for _ in range(20):
            try:
                _os.kill(pid, 0)
                still_alive = True
            except Exception:
                still_alive = False
            if not still_alive:
                break
            _time.sleep(0.1)
        path = data.get("path")
        try:
            state_path.write_text(_json.dumps({}), encoding="utf-8")
        except Exception:
            pass
        # Try upload to local server
        upload = {"ok": False}
        try:
            import urllib.request as _urlreq
            import uuid as _uuid
            import os as _os

            if path and _os.path.exists(path):
                boundary = f"----WebKitFormBoundary{_uuid.uuid4().hex}"
                CRLF = "\r\n"
                # Build multipart body
                with open(path, "rb") as f:
                    file_bytes = f.read()
                parts = []
                parts.append(f"--{boundary}{CRLF}")
                parts.append(
                    "Content-Disposition: form-data; name=\"video\"; filename=\"" + _os.path.basename(path) + "\"" + CRLF
                )
                parts.append("Content-Type: video/mp4" + CRLF + CRLF)
                body_prefix = ("".join(parts)).encode("utf-8")
                body_suffix = (CRLF + f"--{boundary}--{CRLF}").encode("utf-8")
                body = body_prefix + file_bytes + body_suffix

                req = _urlreq.Request(
                    url="http://localhost:3000/upload-video",
                    data=body,
                    method="POST",
                    headers={
                        "Content-Type": f"multipart/form-data; boundary={boundary}",
                        "Content-Length": str(len(body)),
                    },
                )
                with _urlreq.urlopen(req, timeout=30) as resp:
                    resp_body = resp.read().decode("utf-8", errors="ignore")
                    try:
                        upload_json = _json.loads(resp_body)
                    except Exception:
                        upload_json = {"raw": resp_body}
                    upload = {"ok": True, "response": upload_json}
        except Exception as _e:
            upload = {"ok": False, "error": repr(_e)}

        return {"ok": True, "path": path, "upload": upload}
    except Exception as e:
        return {"ok": False, "error": repr(e)}


def status():
    # Local imports for serialized execution environments
    import os as _os
    import json as _json
    from pathlib import Path as _Path

    state_path = _Path("/tmp/cua_recorder/state.json")
    data = {}
    if state_path.exists():
        try:
            data = _json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    pid = data.get("pid")
    running = False
    if isinstance(pid, int):
        try:
            _os.kill(pid, 0)
            running = True
        except Exception:
            running = False
    return {"ok": True, "running": running, "path": data.get("path"), "pid": pid, "fps": data.get("fps")}


def _pid_alive(pid):
    # Kept for compatibility if imported directly; not used by venv_exec paths
    import os as _os
    try:
        _os.kill(pid, 0)
        return True
    except Exception:
        return False



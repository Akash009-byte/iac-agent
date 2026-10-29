#!/usr/bin/env python3
"""Start the local application using tested dependencies and persistent storage."""
import os, pathlib, secrets, shutil, socket, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent
NAME = ROOT.name
MONGO = (ROOT / "tools/mongo").exists()
FRONTEND = (ROOT / "webapp/package.json").exists()

def run(args, **kwargs):
    subprocess.run(args, check=True, **kwargs)

def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Use Python 3.12: python3.12 dev.py")
    if (MONGO or FRONTEND) and not shutil.which("npm"):
        raise SystemExit("Install Node.js 22 or newer (including npm) first.")
    os.chdir(ROOT)
    local = ROOT / ".local"
    local.mkdir(exist_ok=True)
    venv = ROOT / ".venv"
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists(): run([sys.executable, "-m", "venv", str(venv)])
    lock = ROOT / "requirements.lock.txt"
    marker = local / "dependencies.sha256"
    import hashlib
    digest = hashlib.sha256(lock.read_bytes()).hexdigest()
    if not marker.exists() or marker.read_text() != digest:
        run([str(python), "-m", "pip", "install", "-r", str(lock)])
        marker.write_text(digest)
    config = ROOT / "app/.env"
    if not config.exists():
        sample = (ROOT / "app/.env.example").read_text()
        sample = sample.replace("JWT_SECRET_KEY=replace-with-a-random-secret", "JWT_SECRET_KEY=" + secrets.token_urlsafe(48))
        sample = sample.replace("SEED_ADMIN_PASSWORD=\n", "SEED_ADMIN_PASSWORD=" + secrets.token_urlsafe(18) + "\n")
        config.write_text(sample)
        config.chmod(0o600)
        print("Created app/.env. LearnSphere admin credentials, when applicable, are stored there.")
    # Read settings with the same dotenv parser used by the backend.
    import json
    settings = json.loads(subprocess.check_output([str(python), "-c", "import json; from dotenv import dotenv_values; print(json.dumps(dotenv_values('app/.env')))"], text=True))
    env = dict(os.environ)
    env.update({k: v for k, v in settings.items() if v is not None})
    children = []
    try:
        if MONGO and not env.get("MONGO_URL"):
            host, port = env.get("MONGO_HOST", "127.0.0.1"), int(env.get("MONGO_PORT", "27017"))
            try:
                with socket.create_connection((host, port), timeout=1): pass
            except OSError:
                if host not in {"127.0.0.1", "localhost"}:
                    raise SystemExit("Configured MongoDB host is unavailable.")
                tools = ROOT / "tools/mongo"
                if not (tools / "node_modules").exists(): run(["npm", "ci", "--ignore-scripts"], cwd=tools)
                children.append(subprocess.Popen(["node", "server.cjs"], cwd=tools, env=env))
                import time
                for _ in range(180):
                    try:
                        with socket.create_connection((host, port), timeout=1): break
                    except OSError:
                        if children[-1].poll() is not None: raise SystemExit("Local MongoDB failed to start.")
                        time.sleep(1)
                else: raise SystemExit("MongoDB startup timed out.")
        port = env.get("SERVER_PORT", "5010" if FRONTEND else ("5001" if MONGO else "5000"))
        children.append(subprocess.Popen([str(python), "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", port], cwd=ROOT / "app", env=env))
        if FRONTEND:
            if not (ROOT / "webapp/node_modules").exists(): run(["npm", "ci"], cwd=ROOT / "webapp")
            env["VITE_API_BASE_URL"] = "http://127.0.0.1:" + port
            children.append(subprocess.Popen(["npm", "run", "dev", "--", "--host", "127.0.0.1"], cwd=ROOT / "webapp", env=env))
            print("Frontend: http://127.0.0.1:5173")
        print("API docs: http://127.0.0.1:" + port + "/docs")
        import time
        while all(child.poll() is None for child in children): time.sleep(.5)
        if any(child.returncode not in (None, 0) for child in children): raise SystemExit("A service failed; see its error above.")
    except KeyboardInterrupt:
        pass
    finally:
        for child in reversed(children):
            if child.poll() is None: child.terminate()
        for child in children:
            try: child.wait(timeout=10)
            except subprocess.TimeoutExpired: child.kill(); child.wait()

if __name__ == "__main__": main()

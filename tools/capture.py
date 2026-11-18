"""Capture unmodified emulator screenshots and record their origin and SHA-256."""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("name", help="PNG filename without extension")
parser.add_argument("description")
parser.add_argument("--adb", default=str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe"))
parser.add_argument("--serial", default="emulator-5554")
args = parser.parse_args()

def adb(*commands):
    return subprocess.check_output([args.adb, "-s", args.serial, *commands])

data = adb("exec-out", "screencap", "-p")
if not data.startswith(b"\x89PNG\r\n\x1a\n"):
    raise RuntimeError("Device did not return a PNG")
path = ROOT / "screenshots" / f"{args.name}.png"
path.write_bytes(data)
manifest_path = ROOT / "screenshots" / "manifest.json"
manifest = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else {}
manifest[path.name] = {
    "captured_at": datetime.now(ZoneInfo("America/Guayaquil")).isoformat(),
    "device": args.serial,
    "api": adb("shell", "getprop", "ro.build.version.sdk").decode().strip(),
    "size": adb("shell", "wm", "size").decode().strip(),
    "description": args.description,
    "sha256": hashlib.sha256(data).hexdigest(),
    "source": "adb exec-out screencap -p; PNG sin editar",
}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), "utf-8")
print(path)

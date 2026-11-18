"""Exercise the installed production APK against Google Books on an emulator."""
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
SERIAL = "emulator-5554"
PACKAGE = "com.example.bookshelf"

def adb(*args):
    return subprocess.check_output([ADB, "-s", SERIAL, *args], stderr=subprocess.STDOUT).decode("utf-8", "replace").strip()

def shell(*args): return adb("shell", *args)

def hierarchy():
    shell("uiautomator", "dump", "/sdcard/bookshelf-window.xml")
    return ET.fromstring(shell("cat", "/sdcard/bookshelf-window.xml"))

def wait_text(text, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root = hierarchy()
        if any(text in node.get("text", "") for node in root.iter("node")):
            return root
        time.sleep(1)
    raise TimeoutError(f"Expected UI text did not appear: {text}")

def tap_text(text):
    root = wait_text(text)
    node = next(node for node in root.iter("node") if node.get("text") == text)
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.get("bounds")))
    shell("input", "tap", str((x1+x2)//2), str((y1+y2)//2))

def capture(name, description):
    subprocess.run([sys.executable, str(ROOT / "tools/capture.py"), name, description], check=True)

def launch():
    shell("am", "force-stop", PACKAGE)
    shell("am", "start", "-W", "-n", f"{PACKAGE}/.MainActivity")

if not SERIAL.startswith("emulator-"): raise RuntimeError("Emulator required")
rotation = shell("settings", "get", "system", "user_rotation")
accelerometer = shell("settings", "get", "system", "accelerometer_rotation")
density_text = shell("wm", "density")
density = re.search(r"Override density: (\d+)", density_text)
wifi = shell("settings", "get", "global", "wifi_on")
data = shell("settings", "get", "global", "mobile_data")

try:
    shell("wm", "density", "420")
    shell("settings", "put", "system", "accelerometer_rotation", "0")
    shell("settings", "put", "system", "user_rotation", "0")
    shell("svc", "wifi", "enable"); shell("svc", "data", "enable")
    launch()
    capture("03_carga", "Consulta real a Google Books iniciada; indicador de carga de metadatos")
    wait_text("Explora tu biblioteca")
    time.sleep(4)
    capture("01_galeria", "Libros y portadas de la consulta real jazz history en Google Books")
    shell("input", "swipe", "800", "1660", "800", "700", "500")
    time.sleep(2)
    capture("02_desplazamiento", "Cuadrícula desplazada a otros resultados de la consulta real")

    shell("svc", "wifi", "disable"); shell("svc", "data", "disable")
    launch()
    wait_text("Revisa tu conexión")
    capture("04_error_sin_red", "Petición real sin Wi-Fi ni datos; mensaje de conectividad y Reintentar")
    shell("svc", "wifi", "enable"); shell("svc", "data", "enable")
    time.sleep(4)
    tap_text("Reintentar")
    wait_text("Explora tu biblioteca")
    time.sleep(3)
    capture("05_recuperacion", "Misma consulta recuperada al restablecer la red y pulsar Reintentar")

    shell("settings", "put", "system", "user_rotation", "1")
    time.sleep(3)
    wait_text("Explora tu biblioteca")
    capture("06_horizontal", "Mismos resultados conservados al rotar; cuadrícula con más columnas")
    shell("settings", "put", "system", "user_rotation", "0")
    time.sleep(2)
    root = hierarchy()
    field = next(node for node in root.iter("node") if node.get("class") == "android.widget.EditText")
    x1,y1,x2,y2=map(int,re.findall(r"\d+",field.get("bounds")))
    shell("input", "tap", str((x1+x2)//2), str((y1+y2)//2))
    shell("input", "keyevent", "KEYCODE_MOVE_END")
    shell("input", "keyevent", *(["KEYCODE_DEL"] * len(field.get("text", ""))))
    shell("input", "text", "kotlin")
    tap_text("Buscar")
    wait_text("libros · kotlin")
    time.sleep(4)
    capture("07_busqueda", "Búsqueda real de kotlin enviada por el campo y el botón Buscar")
finally:
    shell("svc", "wifi", "enable" if wifi != "0" else "disable")
    shell("svc", "data", "enable" if data != "0" else "disable")
    shell("settings", "put", "system", "user_rotation", rotation)
    shell("settings", "put", "system", "accelerometer_rotation", accelerometer)
    shell("wm", "density", density.group(1) if density else "reset")

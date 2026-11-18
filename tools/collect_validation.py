"""Collect observed build/test results and verify screenshot provenance."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
docs = ROOT / "docs"
build = (docs / "build-validation.log").read_text("utf-8-sig")
ui = (docs / "ui-tests.log").read_text("utf-8-sig")
lint = (docs / "lint-results.txt").read_text("utf-8-sig")
assert "BUILD SUCCESSFUL" in build, "Build is not green"
ui_match = re.search(r"OK \((\d+) tests?\)", ui)
assert ui_match, "Instrumented tests are not green"
lint_match = re.search(r"(\d+) errors?, (\d+) warnings?", lint)
assert lint_match, "Lint summary missing"
roots = [ET.parse(path).getroot() for path in (docs / "test-results").glob("TEST-*.xml")]
assert roots, "JUnit reports missing"
tests = sum(int(root.attrib["tests"]) for root in roots)
failures = sum(int(root.attrib["failures"]) + int(root.attrib["errors"]) for root in roots)
assert failures == 0, "JUnit suite is not green"
manifest = json.loads((ROOT / "screenshots/manifest.json").read_text("utf-8"))
for name, metadata in manifest.items():
    assert hashlib.sha256((ROOT / "screenshots" / name).read_bytes()).hexdigest() == metadata["sha256"], name
apk = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
results = {
    "date": "2026-11-18", "build": "BUILD SUCCESSFUL", "unit_tests": tests,
    "unit_failures": failures, "ui_tests": int(ui_match.group(1)), "ui_failures": 0,
    "lint_errors": int(lint_match.group(1)), "lint_warnings": int(lint_match.group(2)),
    "device": "Cupcake_API29 / Android 10 / API 29 / x86_64",
    "apk_sha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
    "screenshots": len(manifest),
}
assert results["lint_errors"] == 0
(docs / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), "utf-8")
lines = [
    "# Validación de Bookshelf", "", "Fecha: 18 de noviembre de 2026.", "",
    "## Compilación y análisis", "",
    "Comando ejecutado:", "", "```powershell",
    ".\\gradlew.bat testDebugUnitTest assembleDebug assembleDebugAndroidTest lintDebug --no-daemon --console=plain",
    "```", "", f"Resultado: **BUILD SUCCESSFUL**. {tests} pruebas unitarias, 0 fallos y 0 errores.", "",
    f"Android Lint: **{results['lint_errors']} errores y {results['lint_warnings']} advertencias**. "
    "Las advertencias corresponden a versiones más recientes de dependencias; se conserva el conjunto compatible con las prácticas anteriores.", "",
    "[Registro completo](build-validation.log) · [Informe Lint](lint-results.txt) · [Resultados JUnit](test-results)", "",
    "## Pruebas unitarias", "",
    "Las pruebas de repositorio usan MockWebServer y FakeBooksApiService; las de ViewModel inyectan un repositorio controlado. "
    "No dependen de la disponibilidad de Google Books.", "",
    "| Suite | Caso | Resultado |", "| --- | --- | --- |",
]
for root in roots:
    for case in root.findall("testcase"):
        lines.append(f"| {root.attrib['name'].split('.')[-1]} | `{case.attrib['name']}` | Correcto |")
lines.extend([
    "", "El registro [test-red.log](test-red.log) conserva la fase previa a implementar los comportamientos: "
    "12 pruebas ejecutadas y 11 fallos esperados con el repositorio vacío y el ViewModel sin consultas. "
    "La suite final incorpora además la prueba con FakeBooksApiService.", "",
    "## Pruebas instrumentadas", "", "APK de prueba instalado en Cupcake_API29. Comando ejecutado:", "",
    "```powershell", "adb shell am instrument -w com.example.bookshelf.test/androidx.test.runner.AndroidJUnitRunner", "```", "",
    f"Resultado: **OK ({results['ui_tests']} tests)**. Se verificaron cuadrícula y desplazamiento, estado de carga, "
    "lista vacía, búsqueda y recuperación mediante Reintentar. Los datos de estas pruebas son controlados "
    "y están únicamente en androidTest.", "", "[Registro instrumentado](ui-tests.log)", "",
    "## Ejecución con el servicio real", "",
    "La consulta sin clave respondió HTTP 429. Después de configurar una clave local, Google Books respondió "
    "HTTP 200 y devolvió 12 libros para jazz history. La app de producción no usa resultados ficticios.", "",
    "Se verificaron galería con portadas descargadas, desplazamiento, búsqueda adicional, orientación horizontal, "
    "error sin conexión y recuperación al restablecer Wi-Fi/datos y pulsar Reintentar.", "",
    "Las capturas originales proceden de `adb exec-out screencap -p`. "
    "[manifest.json](../screenshots/manifest.json) registra fecha, dispositivo, resolución y SHA256 de cada PNG sin editar.", "",
    f"APK verificado: SHA256 `{results['apk_sha256']}`. El APK y local.properties se excluyen de Git para no publicar la clave.", "",
    "## Reproducir", "",
    "Configurar una clave de Books API en local.properties o GOOGLE_BOOKS_API_KEY; abrir en Android Studio con JDK 17 "
    "y SDK 35. Ejecutar en API 24 o superior con Internet. Para repetir las capturas en el emulador puede usarse "
    "`python tools/runtime_evidence.py`; el script restaura conectividad, orientación y densidad al terminar.", "",
    "El Word se crea con `python tools/create_evidence_document.py`; el PDF se exporta con "
    "`tools/export_word_pdf.ps1` y ambos se revisan visualmente antes de la entrega.",
])
(docs / "Validacion.md").write_text("\n".join(lines) + "\n", "utf-8")
print(json.dumps(results, ensure_ascii=False, indent=2))

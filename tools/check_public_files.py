"""Verify the public Git payload without printing credential values."""
from pathlib import Path
import io
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
paths = subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
).decode("utf-8").split("\0")
local_file = ROOT / "local.properties"
secrets = []
if local_file.exists():
    for line in local_file.read_text("utf-8").splitlines():
        if line.strip().startswith("BOOKS_API_KEY="):
            value = line.split("=", 1)[1].strip()
            if value: secrets.append(value.encode())

violations = []
for name in filter(None, paths):
    path = ROOT / name
    if name.endswith("local.properties") or "/build/" in name or name.endswith(".apk"):
        violations.append((name, "local/generated file")); continue
    data = path.read_bytes()
    payloads = [data]
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            payloads.extend(archive.read(item) for item in archive.namelist() if item.endswith((".xml", ".rels")))
    if name.endswith(".pdf"):
        import pymupdf as fitz
        with fitz.open(path) as pdf:
            payloads.append("\n".join(page.get_text() for page in pdf).encode())
    if any(secret in payload for secret in secrets for payload in payloads):
        violations.append((name, "local API key found"))
    if any(re.search(rb"AIza[0-9A-Za-z_-]{35}", payload) for payload in payloads):
        violations.append((name, "Google API key pattern found"))
if violations:
    for name, reason in violations: print(f"BLOCKED: {name}: {reason}")
    raise SystemExit(1)
print(f"Public payload checked: {len(list(filter(None, paths)))} files; no API keys or generated APKs.")

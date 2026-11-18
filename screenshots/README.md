# Evidencias de ejecución

Fecha: 18 de noviembre de 2026. Dispositivo: **Cupcake_API29**, Android 10, API 29, x86_64. Capturas verticales de 1080 × 1920 y horizontal de 1920 × 1080, con densidad de 420 dpi.

Se instaló el APK de depuración compilado del proyecto. Las imágenes proceden directamente de `adb exec-out screencap -p`, sin retoques ni composición. [manifest.json](manifest.json) incluye resolución, fecha, descripción y huella SHA256 de cada archivo.

| Archivo | Acción y resultado observado |
| --- | --- |
| `00_cuota_sin_clave.png` | Antes de configurar la clave, Google Books respondió HTTP 429. Se conserva como evidencia de la incidencia inicial. |
| `01_galeria.png` | Búsqueda real jazz history, detalles de los volúmenes y portadas descargadas con Coil. Un volumen sin portada muestra el estado correspondiente. |
| `02_desplazamiento.png` | Desplazamiento vertical a otros libros de la misma consulta. |
| `03_carga.png` | Inicio de la consulta real y estado de carga de metadatos. |
| `04_error_sin_red.png` | Wi-Fi y datos móviles deshabilitados; nueva petición que termina con error de conectividad. |
| `05_recuperacion.png` | Conectividad restaurada y botón Reintentar pulsado; recuperación de la galería. |
| `06_horizontal.png` | Rotación del emulador y conservación de los resultados con más columnas. |
| `07_busqueda.png` | Cambio de consulta a kotlin mediante el campo y el botón Buscar. |

Las capturas `01` a `07` corresponden a la app de producción configurada con una clave local de Books API. Los resultados de Google Books pueden cambiar por fecha o ubicación. Las pruebas automatizadas con datos controlados se documentan aparte y no se usan para sustituir los datos de estas capturas.

Para repetir el recorrido con la app instalada y una clave configurada:

```powershell
python tools/runtime_evidence.py
```

El script actúa solo sobre `emulator-5554` y restaura la conectividad, la orientación y la densidad que tenía el emulador al comenzar.

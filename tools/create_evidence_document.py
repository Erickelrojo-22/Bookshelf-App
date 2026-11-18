"""Create the editable evidence report from verified results and original screenshots."""
from pathlib import Path
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/Erickelrojo-22/Bookshelf-App"
CODELAB = "https://developer.android.com/codelabs/basic-android-kotlin-compose-bookshelf"
results = json.loads((ROOT / "docs/results.json").read_text("utf-8"))
manifest = json.loads((ROOT / "screenshots/manifest.json").read_text("utf-8"))
doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.27), Inches(11.69)
section.top_margin = section.bottom_margin = Inches(0.65)
section.left_margin = section.right_margin = Inches(0.8)
for name in ("Normal", "Title", "Subtitle", "Heading 1", "Heading 2", "Caption"):
    doc.styles[name].font.name = "Calibri"
    doc.styles[name].font.color.rgb = RGBColor(0, 0, 0)
doc.styles["Normal"].font.size = Pt(11)
doc.styles["Normal"].paragraph_format.space_after = Pt(8)
doc.styles["Title"].font.size = Pt(27)
doc.styles["Heading 1"].font.size = Pt(20)
doc.styles["Heading 2"].font.size = Pt(14)
doc.styles["Caption"].font.size = Pt(9)
for border in doc.styles.element.xpath(".//w:pBdr"):
    border.getparent().remove(border)
doc.core_properties.title = "Bookshelf evidencias del codelab"
doc.core_properties.author = "Erick Alexander Moreira Bailón"
doc.core_properties.subject = "Aplicación Android con Google Books Retrofit Gson y Coil"

def paragraph(text, style=None):
    return doc.add_paragraph(text, style)

def link(label, url):
    p = paragraph(label + " ")
    element = OxmlElement("w:hyperlink")
    element.set(qn("r:id"), p.part.relate_to(url, RT.HYPERLINK, is_external=True))
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), "0563C1"); props.append(color)
    run.append(props)
    text = OxmlElement("w:t"); text.text = url; run.append(text)
    element.append(run); p._p.append(element)

def heading(text):
    doc.add_heading(text, level=1)

def caption(text):
    p = paragraph(text, "Caption"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER

def image(name, width):
    if name not in manifest:
        raise ValueError(f"Missing capture provenance: {name}")
    p = paragraph(""); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ROOT / "screenshots" / name), width=Inches(width))

def image_row(names, width):
    p = paragraph(""); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, name in enumerate(names):
        if name not in manifest: raise ValueError(name)
        if i: p.add_run("    ")
        p.add_run().add_picture(str(ROOT / "screenshots" / name), width=Inches(width))

def table(headers, rows):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Light Shading Accent 1"
    for cell, text in zip(t.rows[0].cells, headers): cell.text = text
    repeat = OxmlElement("w:tblHeader"); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        for cell, text in zip(t.add_row().cells, row): cell.text = str(text)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(5)
                for r in p.runs: r.font.size = Pt(10)

paragraph("Bookshelf", "Title")
paragraph("Evidencias del codelab de Android", "Subtitle")
paragraph("Erick Alexander Moreira Bailón")
paragraph("Ingeniería de Software\nAplicaciones Móviles Nativas · Sexto nivel\n18 de noviembre de 2026")
paragraph("Esta práctica implementa una biblioteca de libros obtenidos desde Google Books. "
          "El proyecto aplica consultas de red con Retrofit, conversión JSON con Gson, "
          "carga de portadas con Coil y separación de responsabilidades mediante un repositorio.")
link("Repositorio de la entrega", REPO)
link("Codelab de referencia", CODELAB)
doc.add_heading("Requisitos implementados", level=2)
table(("Requisito", "Implementación"), [
    ("Consultas al servicio", "Búsqueda de identificadores y detalle de cada volumen"),
    ("Presentación de libros", "Cuadrícula vertical adaptable con títulos y portadas"),
    ("Carga asíncrona", "Coil con indicador de carga y portada no disponible"),
    ("Arquitectura", "Repositorio, contenedor e inyección por constructor"),
    ("Pruebas", "Servicio falso, servidor HTTP local y pruebas Compose"),
])
paragraph("Las capturas corresponden a la aplicación instalada en Cupcake_API29, Android 10, "
          "API 29. Los originales se incluyen sin editar y con sus huellas SHA256 en el repositorio.")

doc.add_page_break(); heading("Arquitectura y acceso a los datos")
paragraph("La aplicación mantiene separadas la capa de datos y la interfaz. "
          "DefaultAppContainer construye Retrofit, el servicio y NetworkBooksRepository. "
          "MainActivity inyecta ese repositorio al crear BooksViewModel con una fábrica.")
table(("Componente", "Responsabilidad"), [
    ("BooksApiService", "Declara GET volumes y GET volumes/{id}"),
    ("Modelos de datos", "Extraen id, volumeInfo, title, authors e imageLinks"),
    ("NetworkBooksRepository", "Busca, consulta los detalles y normaliza las portadas a HTTPS"),
    ("BooksViewModel", "Expone Loading, Success, Empty y Error; cancela búsquedas anteriores"),
    ("BookshelfApp", "Presenta buscador, cuadrícula y acción de reintento"),
])
doc.add_heading("Flujo de una búsqueda", level=2)
for text in [
    "El usuario introduce un título, autor o tema; al iniciar se utiliza jazz history.",
    "Retrofit solicita hasta 12 resultados y Gson extrae sus identificadores.",
    "El repositorio solicita el detalle de cada volumen de forma secuencial.",
    "Las URL de portada se convierten de HTTP a HTTPS antes de entregarlas a Coil.",
    "El ViewModel publica la lista y Compose muestra una cuadrícula con claves por identificador.",
]: paragraph(text, "List Number")
doc.add_heading("Estado y configuración", level=2)
paragraph("El ViewModel conserva la consulta y los resultados al rotar. El texto del buscador usa "
          "rememberSaveable. Una búsqueda nueva cancela el trabajo anterior para evitar resultados atrasados. "
          "La clave de Books API se configura localmente y el archivo que la contiene está excluido de Git.")
paragraph("Se declara el permiso INTERNET. Los modelos contemplan campos opcionales, y la interfaz "
          "muestra un indicador cuando un libro no dispone de portada o su descarga falla.")

doc.add_page_break(); heading("Libros y desplazamiento")
paragraph("La cuadrícula presenta libros de la consulta inicial. Cada tarjeta contiene la portada, "
          "el título y los autores cuando están disponibles. La segunda captura muestra el desplazamiento "
          "a otros resultados de la misma consulta.")
image_row(["01_galeria.png", "02_desplazamiento.png"], 2.55)
caption("Galería inicial y cuadrícula desplazada en el emulador")
paragraph("Las imágenes se descargan en segundo plano con Coil. Las celdas se calculan con "
          "GridCells.Adaptive de 150 dp, por lo que la cantidad de columnas depende del ancho disponible.")

doc.add_page_break(); heading("Carga error y recuperación")
paragraph("La interfaz informa del progreso de la consulta. Para comprobar el manejo de errores "
          "se deshabilita la conexión del emulador y se inicia una petición nueva. Después se restaura "
          "la conexión y se pulsa Reintentar.")
image_row(["03_carga.png", "04_error_sin_red.png", "05_recuperacion.png"], 1.93)
caption("Carga de datos, error de conexión y recuperación al reintentar")
doc.add_heading("Comportamiento observado", level=2)
paragraph("Durante la consulta aparece un indicador de progreso. Cuando la petición falla por "
          "conectividad, la app muestra una explicación y el botón Reintentar. Al recuperar la conexión, "
          "la misma consulta vuelve a obtener los libros sin reiniciar la aplicación.")
paragraph("Los errores HTTP se diferencian de los errores de conectividad. Para HTTP 429 se informa "
          "de la cuota de Google Books, y para otros códigos HTTP se muestra el código recibido.")

doc.add_page_break(); heading("Búsqueda de libros")
paragraph("El buscador permite cambiar la consulta inicial. La siguiente captura registra una "
          "búsqueda adicional y los resultados obtenidos. La consulta visible en el resumen de la lista "
          "corresponde al texto enviado al servicio.")
image("07_busqueda.png", 2.55)
caption("Resultados de una búsqueda adicional en Google Books")
paragraph("El botón Buscar y la acción de búsqueda del teclado ejecutan la consulta. Las respuestas "
          "sin libros presentan un estado vacío; esta condición también está cubierta por pruebas.")

doc.add_page_break(); heading("Diseño adaptable")
paragraph("Al ampliar el espacio disponible la cuadrícula aumenta el número de columnas. "
          "La captura registra la aplicación en orientación horizontal y permite verificar la "
          "distribución de las tarjetas y la conservación de los resultados.")
image("06_horizontal.png", 6.4)
caption("Bookshelf en orientación horizontal")
paragraph("La interfaz utiliza un ancho mínimo por celda en lugar de fijar el número de columnas. "
          "Los títulos largos tienen un máximo de dos líneas y el autor se limita a una línea. "
          "La lista conserva identificadores estables para cada libro.")

doc.add_page_break(); heading("Validación de la entrega")
paragraph("La verificación automatizada se ejecutó sobre el proyecto entregado. Las pruebas "
          "unitarias emplean dobles de prueba y un servidor HTTP local; las pruebas instrumentadas "
          "ejercitan Compose con datos controlados. Las capturas de las páginas anteriores "
          "corresponden a la ejecución de la app con el servicio real.")
table(("Verificación", "Resultado"), [
    ("Compilación y APK de depuración", results["build"]),
    ("Pruebas unitarias", f'{results["unit_tests"]} pruebas · {results["unit_failures"]} fallos'),
    ("Pruebas Compose en API 29", f'{results["ui_tests"]} pruebas · {results["ui_failures"]} fallos'),
    ("Android Lint", f'{results["lint_errors"]} errores · {results["lint_warnings"]} advertencias'),
])
doc.add_heading("Casos comprobados", level=2)
for text in [
    "Repositorio: búsqueda y detalles, URL HTTPS, resultados vacíos, consulta en blanco, duplicados y errores HTTP.",
    "Inyección: FakeBooksApiService entrega datos sin usar el servicio de Internet.",
    "ViewModel: carga, éxito, vacío, error, reintento, cuota HTTP 429 y cancelación de una búsqueda anterior.",
    "Interfaz: cuadrícula, desplazamiento, carga, vacío, búsqueda y recuperación mediante Reintentar.",
]: paragraph(text, "List Bullet")
doc.add_heading("Comandos de reproducción", level=2)
p = paragraph(".\\gradlew.bat testDebugUnitTest assembleDebug lintDebug\n"
              ".\\gradlew.bat connectedDebugAndroidTest")
for run in p.runs: run.font.name = "Consolas"; run.font.size = Pt(9)
paragraph("El repositorio incluye los registros de compilación y pruebas, el resultado resumido "
          "y el manifiesto de capturas. Las advertencias de Lint se detallan en docs/Validacion.md.")
paragraph("Tecnologías: Kotlin 2.1.0, Compose BOM 2024.12.01, Retrofit 2.9.0, Gson Converter 2.9.0, "
          "OkHttp 4.11.0 y Coil Compose 2.4.0. Compilación con JDK 17, Gradle 8.12 y AGP 8.8.0.")
link("Código y evidencias", REPO)

output = ROOT / "docs/Evidencias_Bookshelf.docx"
doc.save(output)
print(output)

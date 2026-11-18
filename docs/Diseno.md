# Diseño de la práctica Bookshelf

Fecha: 18 de noviembre de 2026.

Entrega solicitada: proyecto Android independiente, nuevo repositorio GitHub y documento de evidencias con el mismo formato de las prácticas anteriores de Erick Alexander Moreira Bailón.

## Alcance del codelab

- Consultar Google Books con Retrofit y Gson.
- Buscar identificadores y consultar posteriormente cada volumen.
- Mostrar título y portada mediante Coil en una cuadrícula vertical adaptable.
- Separar presentación y datos con repositorio e inyección manual.
- Probar con un servicio falso sin usar Internet.

## Decisiones

Una sola pantalla Compose con buscador, cuadrícula adaptable de celdas mínimas de 150 dp y estados Loading, Success, Empty y Error. Se conserva la consulta durante la rotación con ViewModel y el texto del buscador con rememberSaveable. Las nuevas búsquedas cancelan las anteriores. Las peticiones de detalle son secuenciales y se limitan a 12 libros por búsqueda.

Retrofit y Gson modelan únicamente los campos necesarios de Google Books. Los campos opcionales admiten ausencia; una portada inexistente o fallida tiene una representación explícita. El contenedor crea el cliente, el servicio y el repositorio; la actividad inyecta el repositorio en la fábrica del ViewModel.

La clave se lee de la variable GOOGLE_BOOKS_API_KEY o del archivo excluido local.properties. No se incorpora a archivos de código versionados ni a registros. La versión de producción consulta el servicio real; los dobles de prueba solo existen en test y androidTest.

## Validación prevista

Pruebas del repositorio con un servidor HTTP local y FakeBooksApiService; estados y cancelación del ViewModel; pruebas Compose instrumentadas; compilación y Android Lint; capturas sin editar desde el emulador; revisión visual del Word y PDF; revisión del contenido Git antes de publicar.

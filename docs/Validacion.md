# Validación de Bookshelf

Fecha: 18 de noviembre de 2026.

## Compilación y análisis

Comando ejecutado:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug assembleDebugAndroidTest lintDebug --no-daemon --console=plain
```

Resultado: **BUILD SUCCESSFUL**. 13 pruebas unitarias, 0 fallos y 0 errores.

Android Lint: **0 errores y 10 advertencias**. Las advertencias corresponden a versiones más recientes de dependencias; se conserva el conjunto compatible con las prácticas anteriores.

[Registro completo](build-validation.log) · [Informe Lint](lint-results.txt) · [Resultados JUnit](test-results)

## Pruebas unitarias

Las pruebas de repositorio usan MockWebServer y FakeBooksApiService; las de ViewModel inyectan un repositorio controlado. No dependen de la disponibilidad de Google Books.

| Suite | Caso | Resultado |
| --- | --- | --- |
| BooksRepositoryTest | `detailFailureIsNotDisguisedAsSuccess` | Correcto |
| BooksRepositoryTest | `absentItemsProducesEmptyList` | Correcto |
| BooksRepositoryTest | `quotaFailureIsPropagated` | Correcto |
| BooksRepositoryTest | `searchFetchesDetailsAndUpgradesThumbnailToHttps` | Correcto |
| BooksRepositoryTest | `duplicateIdsAreRequestedOnlyOnce` | Correcto |
| BooksRepositoryTest | `blankQueryDoesNotCallNetwork` | Correcto |
| BooksViewModelTest | `loadingThenSuccessFromInjectedRepository` | Correcto |
| BooksViewModelTest | `quotaFailureExplainsApiKeyRequirement` | Correcto |
| BooksViewModelTest | `retryRecoversFromOfflineFailure` | Correcto |
| BooksViewModelTest | `emptyResponseHasDedicatedState` | Correcto |
| BooksViewModelTest | `whitespaceOnlySearchProducesEmptyState` | Correcto |
| BooksViewModelTest | `newSearchCancelsOldResults` | Correcto |
| FakeServiceRepositoryTest | `fakeServiceIsInjectedAndSmallThumbnailIsSupported` | Correcto |

El registro [test-red.log](test-red.log) conserva la fase previa a implementar los comportamientos: 12 pruebas ejecutadas y 11 fallos esperados con el repositorio vacío y el ViewModel sin consultas. La suite final incorpora además la prueba con FakeBooksApiService.

## Pruebas instrumentadas

APK de prueba instalado en Cupcake_API29. Comando ejecutado:

```powershell
adb shell am instrument -w com.example.bookshelf.test/androidx.test.runner.AndroidJUnitRunner
```

Resultado: **OK (5 tests)**. Se verificaron cuadrícula y desplazamiento, estado de carga, lista vacía, búsqueda y recuperación mediante Reintentar. Los datos de estas pruebas son controlados y están únicamente en androidTest.

[Registro instrumentado](ui-tests.log)

## Ejecución con el servicio real

La consulta sin clave respondió HTTP 429. Después de configurar una clave local, Google Books respondió HTTP 200 y devolvió 12 libros para jazz history. La app de producción no usa resultados ficticios.

Se verificaron galería con portadas descargadas, desplazamiento, búsqueda adicional, orientación horizontal, error sin conexión y recuperación al restablecer Wi-Fi/datos y pulsar Reintentar.

Las capturas originales proceden de `adb exec-out screencap -p`. [manifest.json](../screenshots/manifest.json) registra fecha, dispositivo, resolución y SHA256 de cada PNG sin editar.

APK verificado: SHA256 `9329fba3a327522bee14d5de4bce310d21a5892b9c42521f213fb872c0eb3a6a`. El APK y local.properties se excluyen de Git para no publicar la clave.

## Reproducir

Configurar una clave de Books API en local.properties o GOOGLE_BOOKS_API_KEY; abrir en Android Studio con JDK 17 y SDK 35. Ejecutar en API 24 o superior con Internet. Para repetir las capturas en el emulador puede usarse `python tools/runtime_evidence.py`; el script restaura conectividad, orientación y densidad al terminar.

El Word se crea con `python tools/create_evidence_document.py`; el PDF se exporta con `tools/export_word_pdf.ps1` y ambos se revisan visualmente antes de la entrega.

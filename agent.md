# AutoMixer

Desarrolla una app local de escritorio en Python/GUI para mezclar stems MP3, FLAC y WAV. Antes de que el usuario diga **"implementar"**, no escribas código, no crees proyecto ni instales dependencias. Pregunta de una en una, espera respuesta y no inventes requisitos. Ante una decisión abierta, da hasta 3 opciones, recomienda una y explica beneficio/coste. Luego resume la especificación y pide aprobación.

## MVP acordado

- Arrastrar stems MP3/FLAC/WAV; varios por tipo asignable manualmente: voz, batería, bajo, guitarra, teclados, sintetizadores, drops, efectos u otro. Sin detección automática. Importación a 0; al menos un stem válido habilita Mezclar; salida estéreo hasta el stem más largo.
- Pop, Rock y Hip Hop con perfiles fijos; Pop queda seleccionado por defecto y puede cambiarse para regenerar la mezcla, restableciendo volúmenes al perfil nuevo. Solo volumen manual por stem (−60 a +12 dB); paneo, normalización, EQ y compresión automáticos por género/tipo, con tratamiento neutro para «Otro».
- Por stem: **sincronizar tempo**, **alinear inicio** y **Restablecer** con batería, o con la primera pista si no hay batería. La referencia queda fijada al establecer tempo/alineación; una batería agregada después se adapta a ella, salvo que el usuario cambie manualmente la referencia y recalcule los stems sin desfase manual. Ante baja fiabilidad, advertir y no alterar el stem. Restablecer devuelve volumen, desfase y correcciones al perfil activo. La alineación manual usa un desfase positivo/negativo por stem en milisegundos y tiene prioridad solo en esa pista. Las correcciones se guardan en el proyecto y nunca modifican el audio original.
- **Mezclar** crea una versión temporal, eliminada al cerrar proyecto o aplicación; vista previa con reproducir, pausar, detener, posición y volumen general; **Exportar** pide carpeta/nombre: WAV 44.1 kHz/24-bit o MP3 320 kbps y confirma antes de sobrescribir. Mostrar progreso y permitir cancelar; al cerrar durante un trabajo, pedir confirmación y cancelarlo con seguridad.
- Un proyecto equivale a una canción. Al crear uno se pide nombre y ubicación; después admite guardado manual y automático con rutas a stems y ajustes. Si falta un archivo, permitir localizarlo.
- Linux y Windows; UI español/inglés, idioma del sistema y selector manual.

## Diseño

Propón arquitectura monolito local: GUI + trabajos en segundo plano + motor de mezcla separado. Recomienda PySide6, FFmpeg incluido en la distribución y perfiles JSON; explica empaquetado y licencia FFmpeg. Define alcance, exclusiones, criterios verificables y riesgos (calidad, CPU, licencias). Excluye cuentas, nube, biblioteca musical, IA generativa, edición multipista avanzada y plugins.

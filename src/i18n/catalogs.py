from __future__ import annotations

# Catálogos de mensajes (decisión D3: claves msg.*, fallback inglés).
# Los placeholders se formatean con {0}, {1}, ... vía `.format(**params)` o index.

ES = {
    "project.name_empty": "El nombre del proyecto no puede estar vacío.",
    "project.folder_notwritable": "No se puede escribir en la ubicación seleccionada.",
    "project.schema_unsupported": "Versión del esquema del proyecto no soportada.",
    "project.not_found": "No se encuentra el proyecto o el archivo.",
    "project.load_failed": "No se pudo cargar el proyecto.",
    "project.save_failed": "No se pudo guardar el proyecto.",
    "project.not_open": "No hay un proyecto abierto.",
    "stem.format_unsupported": "Formato no soportado: solo MP3, FLAC y WAV.",
    "stem.decode_failed": "No se puede decodificar el archivo de audio.",
    "stem.not_found": "Stem faltante: localízalo para continuar.",
    "stem.gain_out_of_range": "Ganancia fuera de rango (−60 a +12 dB).",
    "sync.low_confidence_tempo": "Sincronización poco fiable (confianza {0}%). Stem sin modificar.",
    "sync.low_confidence_alignment": "Alineación poco fiable (confianza {0}%). Stem sin modificar.",
    "export.overwrite_confirmation": "El destino ya existe. ¿Sobrescribir?",
    "export.failed": "No se pudo exportar la mezcla.",
    "busy.confirm_close": "Hay un trabajo de audio en curso. ¿Cancelar y cerrar?",
    "busy.job_active": "Ya hay una tarea de audio en curso.",
    "job.cancelled": "Operación cancelada.",
    "job.failed": "El trabajo de audio falló.",
    "ffmpeg.not_found": "FFmpeg no está disponible en esta instalación.",
    "i18n.unsupported_language": "Idioma no soportado.",
    # --- UI (SPEC010 / UI_DECISIONS U1-U8) ---
    "app.title": "AutoMixer",
    "ui.new_project": "Nuevo",
    "ui.open": "Abrir",
    "ui.save": "Guardar",
    "ui.preferences": "Preferencias",
    "ui.project_name": "Nombre del proyecto",
    "ui.folder": "Ubicación",
    "ui.import_hint": "Importa stems aquí (arrastra MP3/FLAC/WAV)",
    "ui.genre": "Género",
    "ui.mix": "Mezclar",
    "ui.export": "Exportar",
    "ui.language": "Idioma",
    "ui.spanish": "Español",
    "ui.english": "English",
    "ui.cancel": "Cancelar",
    "ui.ok": "Aceptar",
    "ui.play": "Reproducir",
    "ui.pause": "Pausar",
    "ui.stop": "Detener",
    "ui.volume": "Volumen",
    "ui.layout": "Diseño",
    "ui.stem_type": "Tipo",
    "ui.stem_file": "Archivo",
    "ui.stem_volume": "Volumen",
    "ui.stem_action": "Acción",
    "ui.genre_pop": "Pop",
    "ui.genre_rock": "Rock",
    "ui.genre_hip_hop": "Hip Hop",
}

EN = {
    "project.name_empty": "Project name cannot be empty.",
    "project.folder_notwritable": "The selected location is not writable.",
    "project.schema_unsupported": "Unsupported project schema version.",
    "project.not_found": "Project or file not found.",
    "project.load_failed": "Could not load the project.",
    "project.save_failed": "Could not save the project.",
    "project.not_open": "No project is open.",
    "stem.format_unsupported": "Unsupported format: only MP3, FLAC and WAV.",
    "stem.decode_failed": "Cannot decode the audio file.",
    "stem.not_found": "Missing stem: locate it to continue.",
    "stem.gain_out_of_range": "Gain out of range (−60 to +12 dB).",
    "sync.low_confidence_tempo": "Low-confidence tempo sync ({0}%). Stem left unchanged.",
    "sync.low_confidence_alignment": "Low-confidence alignment ({0}%). Stem left unchanged.",
    "export.overwrite_confirmation": "The destination already exists. Overwrite?",
    "export.failed": "Could not export the mix.",
    "busy.confirm_close": "An audio job is running. Cancel and close?",
    "busy.job_active": "An audio job is already running.",
    "job.cancelled": "Operation cancelled.",
    "job.failed": "The audio job failed.",
    "ffmpeg.not_found": "FFmpeg is not available in this installation.",
    "i18n.unsupported_language": "Unsupported language.",
    # --- UI (SPEC010 / UI_DECISIONS U1-U8) ---
    "app.title": "AutoMixer",
    "ui.new_project": "New",
    "ui.open": "Open",
    "ui.save": "Save",
    "ui.preferences": "Preferences",
    "ui.project_name": "Project name",
    "ui.folder": "Location",
    "ui.import_hint": "Drop stems here (drag MP3/FLAC/WAV)",
    "ui.genre": "Genre",
    "ui.mix": "Mix",
    "ui.export": "Export",
    "ui.language": "Language",
    "ui.spanish": "Español",
    "ui.english": "English",
    "ui.cancel": "Cancel",
    "ui.ok": "OK",
    "ui.play": "Play",
    "ui.pause": "Pause",
    "ui.stop": "Stop",
    "ui.volume": "Volume",
    "ui.layout": "Layout",
    "ui.stem_type": "Type",
    "ui.stem_file": "File",
    "ui.stem_volume": "Volume",
    "ui.stem_action": "Action",
    "ui.genre_pop": "Pop",
    "ui.genre_rock": "Rock",
    "ui.genre_hip_hop": "Hip Hop",
}

_CATALOGS = {"es": ES, "en": EN}
_DEFAULT = "en"

SUPPORTED_LANGUAGES = ("es", "en")
DEFAULT_LANGUAGE = "en"
# Idioma predeterminado de producto cuando el del sistema no es es/en (decisión D6).
PRODUCT_DEFAULT_LANGUAGE = "es"


def t(code: str, lang: str = DEFAULT_LANGUAGE, params: dict | None = None) -> str:
    catalog = _CATALOGS.get(lang, _CATALOGS[_DEFAULT])
    text = catalog.get(code, _CATALOGS[_DEFAULT].get(code, code))
    if params:
        try:
            return text.format(*params)
        except (IndexError, KeyError):
            return text
    return text

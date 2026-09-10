# AutoMixer — Decisiones de Diseño UI

**Propósito:** fijar las decisiones de interfaz que quedaron pendientes de la especificación funcional. Cada entrada marca la decisión, la zona de la UI que afecta y la spec donde se aplica. **Estado:** U1–U8 resueltas.

## U1 — Layout de la ventana principal

- **Estado:** resuelta (2026-08-31) · **Afecta a:** ventana principal (todas las specs).
- **Decisión:** layout vertical en **3 zonas**:

```
┌────────────────────────────────────────────────────────────────────┐
│ 🎵 AutoMixer — [Nombre del proyecto ▼]  [Nuevo] [Abrir] [Guardar]    │
│ Género: (●) Pop  ( ) Rock  ( ) Hip Hop                [⚙ Preferencias] │
├────────────────────────────────────────────────────────────────────┤
│  Importa stems aquí (arrastra MP3/FLAC/WAV)                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Tipo      | Archivo           │ Volumen   │ Sincronizar/│  │  │  │
│  │ ▼ voz     | vocal.wav         │ ──●────── │ Alinear  ↩ │ Rest. │  │
│  │ ▼ batería | drums.flac        │ ──●────── │ ...        │       │  │
│  │ ▼ bajo    | bass.wav          │ ──●────── │ ...        │       │  │
│  │ ...       | ...               │           │            │       │  │
│  └───────────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────────┤
│ [▶ Mezclar]   ◀──▶ 0:34 / 3:12   [▶][⏸][⏹]  Volumen: ──●────  [💾 Exportar] │
└────────────────────────────────────────────────────────────────────┘
```

- **Zona 1 (arriba):** barra de proyecto — nombre, acciones `Nuevo`/`Abrir`/`Guardar`, selector de género y `Preferencias`.
- **Zona 2 (centro):** lista/área de stems con drag & drop; una fila por stem con columna de tipo, archivo, volumen y acciones (sincronizar/alinear/restablecer) — detalle en `U3`.
- **Zona 3 (abajo):** barra de reproducción — `Mezclar`, posición, transporte (`▶ ⏸ ⏹`), volumen de preview y `Exportar`.
- **Motivo:** el MVP es de una canción por proyecto; una sola pantalla mantiene visibles todas las acciones del flujo (importar → asignar → mezclar → previsualizar → exportar) sin paneles adicionales.

## U2 — Diálogo de creación de proyecto

- **Estado:** resuelta (2026-08-31) · **Afecta a:** `SPEC001`.
- **Decisión:** diálogo modal con **nombre del proyecto** (texto) y **botón `📁` para elegir carpeta** de destino.

```
┌─ Nuevo proyecto ───────────────────────┐
│  Nombre:  [Mi canción            ]     │
│  Ubicación: [C:/música/proyectos/  ] [📁]
│  [Cancelar]                    [Crear]  │
└────────────────────────────────────────┘
```

- El botón `Crear` queda **deshabilitado mientras el nombre esté vacío** (evita depender solo del error `project.name_empty` en el instante del clic).
- Si la carpeta elegida no es escribible, se muestra `project.folder_notwritable` y no se crea el proyecto.
- Al crear, el archivo de proyecto se guarda como `<Nombre>.automixer` en la carpeta elegida (nombre por defecto; la validación de sobrescritura/ubicación corresponde a `SPEC001`/`SPEC008`).
- `Cancelar` cierra el diálogo sin efectos.

## U3 — Lista de stems

- **Estado:** resuelta (2026-08-31) · **Afecta a:** `SPEC002`, `SPEC003`, `SPEC004`.
- **Decisión:** tabla de filas (una por stem) con columnas: **Tipo · Archivo · Volumen · Ajuste temporal · Desfase · Acción**.

```
┌──────┬───────────────┬──────────┬──────────────────┬──────┬────────┐
│ Tipo │ Archivo       │ Volumen  │ Ajuste temporal  │ Desf │ Acción │
├──────┼───────────────┼──────────┼──────────────────┼──────┼────────┤
│ [voz▼]│ vocal.wav    │ ──●──── 0dB │ [Sinc] [Alinea] │ +12ms│ [Rest] │
│ [batería▼]│ drums.flac│ ────●─ +3dB │ [Sinc] [Alinea] │ 0ms  │ [Rest] │
│ ✗ bass_old.wav (faltante)                    [Reubicar]            │
└──────┴───────────────┴──────────┴──────────────────┴──────┴────────┘
```

- `Tipo`: desplegable manual por stem (voz, batería, bajo, guitarra, teclados, sintetizadores, drops, efectos, otro).
- `Volumen`: slider de −60 a +12 dB con valor numérico al lado; fuera de rango se rechaza (`stem.gain_out_of_range`, SPEC003 AC-05).
- `Ajuste temporal`: botones `[Sinc]` (sincronizar tempo) y `[Alinea]` (alinear inicio), según SPEC004; con baja fiabilidad se advierte y no se modifica.
- `Desfase`: campo de desfase manual en ms (positivo/negativo), prioridad solo en ese stem.
- `Acción`: `[Rest]` = `Restablecer` (volumen, desfase y correcciones al perfil activo).
- Stem no disponible/missing: fila marcada (✗) y botón `[Reubicar]` para localizar la ruta nueva (SPEC008 AC-06).
- El área de lista admite **drag & drop** de archivos MP3/FLAC/WAV (SPEC002).

## U4 — Controles de mezcla (género y Mezclar)

- **Estado:** resuelta (2026-08-31) · **Afecta a:** `SPEC003`, `SPEC005`.
- **Decisión:** **radio buttons** para el género (Pop / Rock / Hip Hop) en la barra superior, y botón **`[▶ Mezclar]`** independiente en la barra inferior.

```
┌────────────────────────────────────────────────────┐
│ Género:  (●) Pop   ( ) Rock   ( ) Hip Hop          │
│  [▶ Mezclar]                                        │
│  • Deshabilitado si hay 0 stems válidos             │
└────────────────────────────────────────────────────┘
```

## Estados (reglas MVP)

| Situación | Género | `Mezclar` | Notas |
|---|---|---|---|
| Sin stems válidos | habilitado | **deshabilitado** | SPEC002 AC-06 / SPEC005 AC-02 |
| ≥1 stem válido, sin mezclar | habilitado | habilitado | SPEC002 AC-05 |
| Tras cambiar género | habilitado | habilitado | restablece ganancias y marca regeneración (SPEC003 AC-06) |
| Trabajo de render en curso | habilitado | **deshabilitado** | un trabajo de audio a la vez (SPEC009 AC-03) |

- Al cambiar de género se **restablecen las ganancias** al perfil nuevo y la mezcla queda marcada para regeneración (SPEC003 AC-06); el temporal anterior sigue disponible hasta el nuevo render, pero la UI indica "mezcla pendiente de regenerar" (especificado en `U7` con detalle de estado).
- Cambiar género **no** importa/borra stems.

## U5 — Reproductor de vista previa

- **Estado:** resuelta (2026-08-31) · **Afecta a:** `SPEC006`.
- **Decisión:** barra de reproducción en la **zona inferior** con:

```
┌────────────────────────────────────────────────────────────┐
│ ◀──▶ 0:00 / 3:12                                      ┃   │
│  [▶/⏸] [⏹]   Volumen preview: ──●──── 100%            │
└────────────────────────────────────────────────────────────┘
```

- **Slider de posición** con tiempo `actual/total` (seek; SPEC006 AC-05).
- **Botón `▶/⏸` alternado** (reproducir ↔ pausar; pausa conserva posición — SPEC006 AC-03).
- **Botón `⏹` (detener):** vuelve a la posición inicial (SPEC006 AC-04).
- **Slider de volumen general de preview** (SPEC006 AC-06): solo afecta a la reproducción, no a la mezcla ni a la exportación.
- **Estado con sin WAV temporal:** todos los controles del reproductor aparecen **deshabilitados** y la UI indica "Mezcla pendiente de regenerar" (SPEC006 AC-07).
- Un render nuevo exitoso reemplaza la fuente de preview anterior (SPEC005/`SPEC006`).

## U6 — Diálogo de exportación de mezcla

- **Estado:** resuelta (2026-08-31) · **Afecta a:** `SPEC007`.
- **Decisión:** se reutiliza el **cuadro nativo "Guardar como"** del sistema (Qt `QFileDialog::getSaveFileName`) con un **selector de formato** integrado como filtro:

```
Guardar como (nativo del SO) — filtro de formato:
  (●) WAV 44.1 kHz / 24-bit (*.wav)
  ( ) MP3 320 kbps (*.mp3)
Nombre sugerido por defecto: <nombre proyecto>_mezcla.<ext>
```

- El **formato elegido** queda determinado por el filtro seleccionado (WAV o MP3); la extensión se aplica automáticamente.
- **Confirmación de sobrescritura:** si el archivo destino ya existe, se muestra `export.overwrite_confirmation` (sí/no) antes de exportar, porque el comportamiento nativo de sobrescritura varía entre Linux y Windows.
- `Cancelar` en el cuadro nativo: no se exporta nada (SPEC007 AC-05).
- Fallo de escritura: `export.failed` y el proyecto se conserva (SPEC007 AC-06).
- Botón `Exportar` de la barra inferior abre este cuadro con el nombre de proyecto como base.

## U7 — Progreso, cancelación y cierre seguro

- **Estado:** resuelta (2026-08-31) · **Afecta a:** `SPEC009`.
- **Decisión:** **barra de progreso con porcentaje + botón `✕ Cancelar`** integrados en la **barra inferior** (no en una ventana separada).

```
Durante render/exportación:
┌──────────────────────────────────────────────┐
│  Mezclando…   ████████░░░░ 64%   [✕ Cancelar] │
└──────────────────────────────────────────────┘
```

- **Durante el trabajo:** `Mezclar` y `Exportar` quedan deshabilitados (SPEC009 AC-03); se permite un trabajo de audio a la vez.
- **Cancelar:** termina el proceso FFmpeg asociado, conserva el proyecto y limpia solo temporales/parciales del trabajo (SPEC009 AC-04/AC-05).
- **Al cerrar (proyecto o aplicación) con trabajo activo:** diálogo de confirmación `busy.confirm_close`:

```
┌─ Confirmar cierre ─────────────────┐
│ Hay un trabajo de audio en curso.  │
│ ¿Cancelar y cerrar?                │
│            [Cancelar]   [Cerrar]   │
└────────────────────────────────────┘
```

- `Cancelar`: permanece en la aplicación · `Cerrar`: cancela el trabajo y cierra (SPEC001 AC-04 / SPEC009 AC-06).

## U8 — Idioma y preferencias

- **Estado:** resuelta (2026-08-31) · **Afecta a:** `SPEC010`.
- **Decisión:** diálogo **Preferencias** pensado para crecer (hoy solo contiene idioma, pero la estructura permite añadir más opciones en el futuro), abierto desde el icono **`⚙`** de la barra superior.

```
┌─ Preferencias ──────────────┐
│ Idioma:  (●) Español        │
│          ( ) English        │
│                    [OK]     │
└─────────────────────────────┘
```

- Radio **Español / English**; al pulsar `OK` la UI cambia de idioma al instante y la preferencia se persiste (QSettings) — SPEC010 AC-05.
- Detección inicial según decisión D6: preferencia guardada → idioma del sistema (`es`/`en`) → **español** por defecto (SPEC010 AC-01..04).
- El diálogo queda abierto a futuras opciones (p. ej. volumen por defecto), por eso es un diálogo y no un menú desplegable.

## Pendientes

Ninguna: decisiones de Diseño UI U1–U8 resueltas (ver secciones anteriores).
from __future__ import annotations

"""Ventana principal (UI): 3 zonas según decisión U1 + selector de idioma (U8).

El import de PySide6 es perezoso para permitir probar el núcleo sin entorno
gráfico. `MainWindow` hereda de `QMainWindow` y, cuando se le pasa
`services["i18n_service"]`, traduce las etiquetas y habilita el diálogo de
Preferencias (SPEC010 AC-05).
"""

import os
import typing

try:
    from PySide6 import QtWidgets as _qw
    from PySide6.QtCore import QTimer as _QTimer
except Exception:  # noqa: BLE001 - PySide6 opcional durante headless/tests
    _qw = None
    _QTimer = None

if typing.TYPE_CHECKING:
    from PySide6 import QtWidgets as Qw  # noqa: F401


def build_main_window(services: dict | None = None):
    """Construye la `MainWindow` si PySide6 está disponible."""
    if _qw is None:
        raise RuntimeError("PySide6 no está instalado; no se puede construir la UI.")
    return MainWindow(_qw, services)


class MainWindow(_qw.QMainWindow if _qw else object):  # type: ignore[misc]
    """Ventana principal de 3 zonas (U1) con idioma configurable (U8)."""

    def __init__(self, QtWidgets, services: dict | None) -> None:
        super().__init__()
        self._qw = QtWidgets
        self._services = services or {}
        self._btn_labels: dict = {}
        self._stem_items: dict = {}  # map: QListWidgetItem -> stem_id

        central = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout(central)
        self._build_top_bar()
        self._build_stems_area()
        self._build_playback_bar()
        self._build_progress_bar()
        self.setCentralWidget(central)
        self._apply_language()

    # --- construcción de zonas ---

    def _add_button(self, text: str, *, with_save: bool = False):
        btn = self._qw.QPushButton(text)
        self._btn_labels[btn] = text
        if with_save:
            btn.clicked.connect(self._open_preferences)
        return btn

    def _build_top_bar(self) -> None:
        ql = self._layout
        top = self._qw.QWidget()
        top_layout = self._qw.QHBoxLayout(top)
        self._name_label = self._qw.QLabel("")
        top_layout.addWidget(self._name_label)

        btn_new = self._add_button("")
        btn_new.clicked.connect(self._new_project)
        top_layout.addWidget(btn_new)

        btn_open = self._add_button("")
        btn_open.clicked.connect(self._open_project)
        top_layout.addWidget(btn_open)

        btn_save = self._add_button("")
        btn_save.clicked.connect(self._save_project)
        top_layout.addWidget(btn_save)

        top_layout.addStretch()

        self._genre_label = self._qw.QLabel("")
        top_layout.addWidget(self._genre_label)
        self._genre_combo = self._qw.QComboBox()
        self._genre_combo.addItem("Pop", "pop")
        self._genre_combo.addItem("Rock", "rock")
        self._genre_combo.addItem("Hip Hop", "hip_hop")
        self._genre_combo.currentIndexChanged.connect(self._on_genre_changed)
        top_layout.addWidget(self._genre_combo)

        btn_prefs = self._add_button("", with_save=True)
        top_layout.addWidget(btn_prefs)

        ql.addWidget(top)

    def _build_stems_area(self) -> None:
        ql = self._layout
        stems = self._qw.QWidget()
        stems_layout = self._qw.QVBoxLayout(stems)
        self._hint = self._qw.QLabel("")
        stems_layout.addWidget(self._hint)

        self._stems_list = self._qw.QListWidget()
        stems_layout.addWidget(self._stems_list)

        # Botón para importar stems (diálogo de archivo, evita crashs de Qt con drag & drop)
        self._btn_import = self._qw.QPushButton(self._tr("ui.import_hint"))
        self._btn_import.clicked.connect(self._import_stems)
        stems_layout.addWidget(self._btn_import)

        ql.addWidget(stems, 1)

    def _build_playback_bar(self) -> None:
        ql = self._layout
        bottom = self._qw.QWidget()
        bottom_layout = self._qw.QHBoxLayout(bottom)
        self._mix_btn = self._add_button("")
        self._mix_btn.clicked.connect(self._on_mix)
        bottom_layout.addWidget(self._mix_btn)
        self._position = self._qw.QLabel("")
        bottom_layout.addWidget(self._position)
        bottom_layout.addWidget(self._qw.QSlider())
        bottom_layout.addStretch()

        self._volume_label = self._qw.QLabel("")
        bottom_layout.addWidget(self._volume_label)
        self._volume_slider = self._qw.QSlider()
        self._volume_slider.setRange(-60, 12)
        self._volume_slider.setValue(0)
        self._volume_slider.setTickPosition(self._qw.QSlider.TickPosition.NoTicks)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        bottom_layout.addWidget(self._volume_slider)
        self._volume_db_label = self._qw.QLabel("0 dB")
        self._volume_db_label.setMinimumWidth(50)
        bottom_layout.addWidget(self._volume_db_label)

        self._lufs_label = self._qw.QLabel("")
        bottom_layout.addWidget(self._lufs_label)
        self._lufs_value_label = self._qw.QLabel("-14.0 LUFS")
        self._lufs_value_label.setMinimumWidth(80)
        bottom_layout.addWidget(self._lufs_value_label)

        self._truepeak_label = self._qw.QLabel("")
        bottom_layout.addWidget(self._truepeak_label)
        self._truepeak_value_label = self._qw.QLabel("-1.0 dB")
        self._truepeak_value_label.setMinimumWidth(55)
        bottom_layout.addWidget(self._truepeak_value_label)

        self._export_btn = self._add_button("")
        self._export_btn.clicked.connect(self._on_export)
        bottom_layout.addWidget(self._export_btn)
        ql.addWidget(bottom)

    def _on_volume_changed(self, value: int) -> None:
        self._volume_db_label.setText(f"{value} dB")
        target = self._get_target_lufs()
        approx_lufs = round(target + value, 1)
        self._lufs_value_label.setText(f"{approx_lufs:.1f} LUFS")

    def _get_target_lufs(self) -> float:
        ps = self._project_service()
        if ps is None or ps.active_project is None:
            return -14.0
        profile_svc = self._services.get("profile_service")
        if profile_svc is None:
            return -14.0
        norm = profile_svc.normalization(ps.active_project.genre)
        return norm.lufs if norm else -14.0

    def _build_progress_bar(self) -> None:
        self._progress_bar = self._qw.QProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("%p%")
        self._progress_bar.hide()
        self._layout.addWidget(self._progress_bar)

    # --- helpers ---

    def _project_service(self):
        return self._services.get("project_service")

    def _mix_service(self):
        return self._services.get("mix_service")

    def _worker_manager(self):
        return self._services.get("worker_manager")

    def _collect_interactive_widgets(self) -> list:
        return [
            self._mix_btn,
            self._export_btn,
            self._btn_import,
            self._genre_combo,
        ]

    def _set_busy(self, label: str = "") -> None:
        for w in self._collect_interactive_widgets():
            w.setEnabled(False)
        fmt = (label + " %p%") if label else "%p%"
        self._progress_bar.setFormat(fmt)
        self._progress_bar.setValue(0)
        self._progress_bar.show()

    def _set_idle(self) -> None:
        self._progress_bar.hide()
        self._progress_bar.setValue(0)
        ps = self._project_service()
        playback_enabled = ps.mix_enabled if ps and ps.active_project else False
        self._mix_btn.setEnabled(playback_enabled)
        self._export_btn.setEnabled(playback_enabled)
        self._btn_import.setEnabled(True)
        self._genre_combo.setEnabled(
            ps is not None and ps.active_project is not None
        )

    def _update_progress(self, pct: int) -> None:
        if _QTimer is not None:
            _QTimer.singleShot(0, lambda p=pct: self._progress_bar.setValue(p))
        else:
            self._progress_bar.setValue(pct)

    def _update_project_name(self) -> None:
        ps = self._project_service()
        if ps is None:
            self._name_label.setText(self._tr("ui.project_name"))
            return
        proj = ps.active_project
        if proj is None:
            self._name_label.setText(self._tr("ui.project_name"))
        else:
            self._name_label.setText(
                f"{self._tr('ui.project_name')}: {proj.name}"
            )

    def _sync_genre(self) -> None:
        ps = self._project_service()
        if ps is None or ps.active_project is None:
            self._genre_combo.setEnabled(False)
            return
        self._genre_combo.setEnabled(True)
        genre = ps.active_project.genre
        self._genre_combo.blockSignals(True)
        idx = self._genre_combo.findData(genre.value)
        if idx >= 0:
            self._genre_combo.setCurrentIndex(idx)
        self._genre_combo.blockSignals(False)

    def _on_genre_changed(self, index: int) -> None:
        qw = self._qw
        ps = self._project_service()
        if ps is None or ps.active_project is None:
            return
        genre_value = self._genre_combo.currentData()
        if not genre_value:
            return
        from ..models.project import Genre
        genre_map = {g.value: g for g in Genre}
        genre = genre_map.get(genre_value)
        if genre is None:
            return
        res = ps.change_genre(genre)
        if not res.is_ok:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("project.not_open")
            )

    def _enable_playback_controls(self, enabled: bool) -> None:
        self._mix_btn.setEnabled(enabled)
        self._export_btn.setEnabled(enabled)

    @staticmethod
    def _is_audio_file(path: str) -> bool:
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        return ext in ("mp3", "flac", "wav")

    # --- handlers de botones ---

    def _new_project(self) -> None:
        qw = self._qw
        ps = self._project_service()
        if ps is None:
            return

        dlg = qw.QDialog(self)
        dlg.setWindowTitle(self._tr("ui.new_project"))
        lay = qw.QFormLayout(dlg)

        name_input = qw.QLineEdit()
        lay.addRow(self._tr("ui.project_name") + ":", name_input)

        folder_combo = qw.QComboBox()
        lay.addRow(self._tr("ui.folder") + ":", folder_combo)

        active_path = ps.active_path
        if active_path:
            folder_combo.addItem(os.path.dirname(active_path))
        folder_combo.addItem(os.path.expanduser("~"))
        folder_combo.addItem(os.getcwd())

        btn_box = qw.QDialogButtonBox(
            qw.QDialogButtonBox.StandardButton.Ok
            | qw.QDialogButtonBox.StandardButton.Cancel
        )
        lay.addRow(btn_box)

        def on_ok():
            name = name_input.text().strip()
            if not name:
                qw.QMessageBox.warning(
                    dlg, self._tr("ui.preferences"),
                    self._tr("project.name_empty")
                )
                return
            folder = str(folder_combo.currentText())
            if not folder:
                folder = os.getcwd()
            res = ps.create(name, folder)
            if res.is_ok:
                self._update_project_name()
                self._sync_genre()
                self._refresh_stems_list()
                self._enable_playback_controls(ps.mix_enabled)
                dlg.accept()
            else:
                msg = getattr(
                    getattr(res, "error", None), "message", str(res)
                )
                qw.QMessageBox.warning(dlg, self._tr("ui.preferences"), msg)

        btn_box.accepted.connect(on_ok)
        btn_box.rejected.connect(dlg.reject)
        dlg.exec()

    def _open_project(self) -> None:
        qw = self._qw
        ps = self._project_service()
        if ps is None:
            return
        path, _ = qw.QFileDialog.getOpenFileName(
            self, self._tr("ui.open"), "", "Proyectos (*.automixer)"
        )
        if not path:
            return
        res = ps.open(path)
        if res.is_ok:
            self._update_project_name()
            self._sync_genre()
            self._refresh_stems_list()
            self._enable_playback_controls(ps.mix_enabled)
        else:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("project.load_failed")
            )

    def _save_project(self) -> None:
        qw = self._qw
        ps = self._project_service()
        if ps is None:
            return
        res = ps.save()
        if not res.is_ok:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("project.save_failed")
            )

    # --- gestión de stems (U3) ---

    def _on_stem_item_clicked(self, item) -> None:
        # Buscar el stem_id a partir del QListWidgetItem
        stem_id = None
        for sid, lst_item in self._stem_items.items():
            if lst_item is item:
                stem_id = sid
                break
        if stem_id is None:
            return
        qw = self._qw
        ps = self._project_service()
        if ps is None or ps.active_project is None:
            return
        stem = ps.active_project.find_stem(stem_id)
        if stem is None:
            return
        qw.QMessageBox.information(
            self, self._tr("ui.stem_file"),
            f"{self._tr('ui.stem_file')}: {stem.path}\n"
            f"{self._tr('ui.stem_type')}: {stem.type.value}\n"
            f"{self._tr('ui.stem_volume')}: {stem.gain_db:.1f} dB",
        )

    def _import_stems(self) -> None:
        """Importar stems mediante diálogo de archivo (evita crashs de Qt con drag & drop)."""
        qw = self._qw
        paths, _ = qw.QFileDialog.getOpenFileNames(
            self,
            self._tr("ui.import_hint"),
            "",
            "Audio (*.mp3 *.flac *.wav)",
        )
        if not paths:
            return
        self._add_stems_from_paths(paths)

    def _add_stems_from_paths(self, paths: list) -> None:
        qw = self._qw
        ps = self._project_service()
        if ps is None or ps.active_project is None:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("project.not_open")
            )
            return
        added = 0
        for path in paths:
            if not self._is_audio_file(path):
                continue
            res = ps.add_stem(path)
            if res.is_ok:
                stem = res.value
                self._add_stem_item(stem)
                added += 1
        if added:
            self._enable_playback_controls(ps.mix_enabled)
            suffix = "" if added == 1 else "s"
            self._hint.setText(
                f"{self._tr('ui.import_hint')}  ({added} añadido{suffix})"
            )

    def _add_stem_item(self, stem) -> None:
        qw = self._qw
        item = qw.QListWidgetItem()
        item.setText(stem.path)
        self._stems_list.addItem(item)
        # Usar el ID del stem como clave (los QListWidgetItem no son hashables en PySide6)
        self._stem_items[stem.id] = item

    def _refresh_stems_list(self) -> None:
        self._stems_list.clear()
        self._stem_items.clear()
        ps = self._project_service()
        if ps is None or ps.active_project is None:
            return
        for stem in ps.active_project.stems:
            self._add_stem_item(stem)

    # --- handlers de reproducción (SPEC005/SPEC006/SPEC007) ---

    def _on_mix(self) -> None:
        qw = self._qw
        ps = self._project_service()
        ms = self._mix_service()
        wm = self._worker_manager()
        if ps is None or ms is None or wm is None:
            return
        if ps.active_project is None:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("project.not_open")
            )
            return
        if not ps.mix_enabled:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("ui.import_hint")
            )
            return

        project = ps.active_project

        def work(token, progress_cb):
            return ms.render_preview(
                project,
                on_progress=progress_cb,
                cancel=token.cancelled.__bool__,
            )

        def on_progress(pct):
            self._update_progress(pct)

        def on_done(result):
            if result.is_ok:
                load_res = ms.load_preview()
                if load_res.is_ok:
                    self._update_progress(100)
                    self._set_idle()
                    self._position.setText("0:00")
                else:
                    self._set_idle()
                    qw.QMessageBox.warning(
                        self, self._tr("ui.preferences"),
                        self._tr("job.failed")
                    )
            else:
                self._set_idle()
                msg = getattr(
                    getattr(result, "error", None), "message", str(result)
                )
                qw.QMessageBox.warning(
                    self, self._tr("ui.preferences"),
                    msg or self._tr("job.failed")
                )

        self._set_busy(self._tr("ui.mix"))
        wm.start(work, on_progress=on_progress, on_done=on_done)

    def _on_export(self) -> None:
        qw = self._qw
        ps = self._project_service()
        ms = self._mix_service()
        wm = self._worker_manager()
        if ps is None or ms is None or wm is None:
            return
        if ps.active_project is None:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("project.not_open")
            )
            return
        if not ps.mix_enabled:
            qw.QMessageBox.warning(
                self, self._tr("ui.preferences"),
                self._tr("ui.import_hint")
            )
            return

        name = ps.active_project.name
        base_name = (name or "mezcla").replace(" ", "_")
        filters = "WAV 44.1 kHz / 24-bit (*.wav);;MP3 320 kbps (*.mp3)"
        path, selected_filter = qw.QFileDialog.getSaveFileName(
            self, self._tr("ui.export"), f"{base_name}.wav", filters
        )
        if not path:
            return
        fmt = "wav" if "*.wav" in (selected_filter or "") else "mp3"
        from ..ports.audio import ExportFormat
        export_fmt = (
            ExportFormat.WAV_44100_24 if fmt == "wav" else ExportFormat.MP3_320
        )

        project = ps.active_project

        def work(token, progress_cb):
            return ms.export(
                project, path, export_fmt,
                on_progress=progress_cb,
                cancel=token.cancelled.__bool__,
            )

        def on_progress(pct):
            self._update_progress(pct)

        def on_done(result):
            if result.is_ok:
                self._update_progress(100)
                self._set_idle()
            else:
                self._set_idle()
                msg = getattr(
                    getattr(result, "error", None), "message", str(result)
                )
                qw.QMessageBox.warning(
                    self, self._tr("ui.preferences"),
                    msg or self._tr("export.failed")
                )

        self._set_busy(self._tr("ui.export"))
        wm.start(work, on_progress=on_progress, on_done=on_done)

    # --- idioma (SPEC010 AC-05, U8) ---

    def _tr(self, code: str) -> str:
        i18n = self._services.get("i18n_service")
        return i18n.tr(code) if i18n is not None else code

    def _apply_language(self) -> None:
        t = self._tr
        self.setWindowTitle(t("app.title"))
        buttons = list(self._btn_labels)
        self._name_label.setText(t("ui.project_name"))
        labels = [t("ui.new_project"), t("ui.open"), t("ui.save")]
        for i, btn in enumerate(buttons[:3]):
            btn.setText(labels[i])
        buttons[3].setText(t("ui.preferences"))
        self._hint.setText(t("ui.import_hint"))
        self._genre_label.setText(t("ui.genre") + ":")
        self._genre_combo.blockSignals(True)
        genre_labels = [t("ui.genre_pop"), t("ui.genre_rock"), t("ui.genre_hip_hop")]
        genre_values = ["pop", "rock", "hip_hop"]
        self._genre_combo.clear()
        for label, value in zip(genre_labels, genre_values):
            self._genre_combo.addItem(label, value)
        self._genre_combo.blockSignals(False)
        self._sync_genre()
        self._mix_btn.setText(t("ui.mix"))
        self._position.setText("0:00")
        self._export_btn.setText(t("ui.export"))
        self._volume_label.setText(t("ui.volume") + ":")
        self._lufs_label.setText(t("ui.lufs") + ":")
        self._truepeak_label.setText(t("ui.true_peak") + ":")
        self._on_volume_changed(self._volume_slider.value())

    def _open_preferences(self) -> None:
        """Diálogo Preferencias (U8): selector de idioma que persiste (AC-05).

        Usa `QDialog` con botones personalizados para garantizar que el
        diálogo se cierre correctamente tras aplicar el idioma.
        """
        qw = self._qw
        i18n = self._services.get("i18n_service")
        if i18n is None:
            return

        dlg = qw.QDialog(self)
        dlg.setWindowTitle(self._tr("ui.preferences"))
        dlg.setModal(True)
        lay = qw.QVBoxLayout(dlg)

        lang_label = qw.QLabel(self._tr("ui.language") + ":")
        lay.addWidget(lang_label)

        lang_box = qw.QComboBox()
        lang_box.addItem(self._tr("ui.spanish"), "es")
        lang_box.addItem(self._tr("ui.english"), "en")
        idx = lang_box.findData(i18n.language)
        if idx >= 0:
            lang_box.setCurrentIndex(idx)
        lay.addWidget(lang_box)

        # Botones personalizados para mayor control
        btn_ok = qw.QPushButton(self._tr("ui.ok"))
        btn_cancel = qw.QPushButton(self._tr("ui.cancel"))
        lay.addWidget(btn_ok)
        lay.addWidget(btn_cancel)

        def on_ok_clicked():
            res = i18n.set_language(str(lang_box.currentData()))
            if res.is_ok:
                self._apply_language()
                self._update_project_name()
                dlg.accept()
            else:
                qw.QMessageBox.warning(
                    dlg, self._tr("ui.preferences"),
                    self._tr("i18n.unsupported_language")
                )

        btn_ok.clicked.connect(on_ok_clicked)
        btn_cancel.clicked.connect(dlg.reject)
        dlg.exec()

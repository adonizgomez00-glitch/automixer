from __future__ import annotations
import array
import math
import os
import shutil
import subprocess
from typing import List, Optional, Sequence, Tuple

from ..models.mix_profile import EqBand
from ..ports.audio import (
    AlignmentAnalysis,
    AudioCancelled,
    AudioEngine,
    ExportFormat,
    Normalization,
    RenderStem,
    TempoAnalysis,
)
from ..utils.result import DomainError
from ..ports.audio import CancelCheck, ProgressCallback


# Envolvente: ventanas de 20 ms sobre audio mono 8 kHz (160 muestras).
ENV_SR = 8000
ENV_WINDOW = 160
ENV_RATE = ENV_SR // ENV_WINDOW          # 50 envolventes/segundo
ENV_MS = 1000 // ENV_RATE                # 20 ms por paso
MAX_ANALYSIS_SECONDS = 600               # límite de análisis (10 min)


class FFmpegEngine(AudioEngine):
    """Motor de audio real: análisis, render temporal y exportación (Fase 3).

    - FFmpeg/ffprobe se invocan **sin shell** (ARCHITECTURE.md, SPEC002).
    - Binario: primero el incluido en el bundle (`resources/`), luego el PATH (D5).
    - Cancelación: termina el proceso y limpia el parcial (SPEC005 AC-07).
    """

    def __init__(self, bundled_dir: Optional[str] = None) -> None:
        self._bundled_dir = bundled_dir

    # --- binarios ---

    def _resolve(self, name: str) -> str:
        candidates: List[str] = []
        if self._bundled_dir:
            exe = name + (".exe" if os.name == "nt" else "")
            candidates.append(os.path.join(self._bundled_dir, exe))
        found = shutil.which(name)
        if found:
            candidates.append(found)
        for cand in candidates:
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                return cand
        raise DomainError("ffmpeg.not_found")

    @property
    def ffmpeg(self) -> str:
        return self._resolve("ffmpeg")

    @property
    def ffprobe(self) -> str:
        return self._resolve("ffprobe")

    # --- ejecución sin shell con progreso y cancelación ---

    def _run(
        self,
        cmd: Sequence[str],
        *,
        total_ms: Optional[int],
        failure_code: str,
        on_progress: Optional[ProgressCallback] = None,
        cancel: Optional[CancelCheck] = None,
        capture_stderr: bool = True,
    ) -> None:
        proc = subprocess.Popen(  # noqa: S603 - lista de args, sin shell
            list(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE if capture_stderr else subprocess.DEVNULL,
            text=True,
        )
        stderr_text = ""
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.strip()
                if cancel is not None and cancel():
                    proc.terminate()
                    proc.wait(timeout=10)
                    raise AudioCancelled()
                if not line.startswith("out_time_ms="):
                    continue
                try:
                    us = int(line.split("=", 1)[1])
                except ValueError:
                    continue
                if on_progress and total_ms:
                    pct = max(0, min(99, int(us / 1000 * 100 / total_ms)))
                    on_progress(pct)
            proc.wait(timeout=600)
            if capture_stderr and proc.stderr is not None:
                try:
                    stderr_text = proc.stderr.read()[-2000:]
                except (OSError, ValueError):
                    stderr_text = ""
        except AudioCancelled:
            raise
        finally:
            for stream in (proc.stdout, proc.stderr):
                try:
                    if stream is not None:
                        stream.close()
                except OSError:
                    pass
        if proc.returncode != 0:
            raise DomainError(failure_code, {"detail": stderr_text.strip()[:500]})
        if on_progress:
            on_progress(100)

    # --- decodificación y duración ---

    def is_decodable(self, path: str) -> bool:
        if not os.path.isfile(path):
            return False
        try:
            proc = subprocess.run(  # noqa: S603 - lista de args, sin shell
                [
                    self.ffprobe,
                    "-v", "error",
                    "-select_streams", "a:0",
                    "-show_entries", "stream=codec_name",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return proc.returncode == 0 and bool(proc.stdout.strip())

    # --- análisis (envolvente/onsets, decisión D2) ---

    def _decode_envelope(self, path: str) -> List[float]:
        """Envolvente RMS a 50 Hz de la pista mono 8 kHz vía pipe de FFmpeg."""
        cmd = [
            self.ffmpeg,
            "-nostdin", "-hide_banner", "-v", "error",
            "-i", path,
            "-map", "a:0",
            "-t", str(MAX_ANALYSIS_SECONDS),
            "-f", "s16le", "-ac", "1", "-ar", str(ENV_SR),
            "pipe:1",
        ]
        proc = subprocess.Popen(  # noqa: S603 - lista de args, sin shell
            cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        samples: array.array = array.array("h")
        assert proc.stdout is not None
        while True:
            chunk = proc.stdout.read(ENV_SR * 2)  # 1 s de muestras s16le
            if not chunk:
                break
            samples.frombytes(chunk)
        proc.stdout.close()
        proc.wait(timeout=120)
        if proc.returncode != 0:
            raise DomainError("stem.decode_failed", {"path": path})

        env: List[float] = []
        total = len(samples)
        for start in range(0, total - ENV_WINDOW + 1, ENV_WINDOW):
            acc = 0.0
            for i in range(start, start + ENV_WINDOW):
                v = samples[i] / 32768.0
                acc += v * v
            env.append(math.sqrt(acc / ENV_WINDOW))
        return env

    @staticmethod
    def _onsets(envelope: List[float]) -> List[float]:
        """Envolvente de onsets: diferencia positiva (rectificación media onda)."""
        return [
            max(0.0, envelope[i] - envelope[i - 1])
            for i in range(1, len(envelope))
        ]

    @staticmethod
    def _peak_correlation(a: List[float], b: List[float], max_lags: int) -> Tuple[int, float]:
        """Correlación cruzada normalizada; devuelve (lag, confianza en [0,1])."""
        best_lag, best_val = 0, 0.0
        for lag in range(-max_lags, max_lags + 1):
            num = den_a = den_b = 0.0
            for i in range(len(a)):
                j = i + lag
                if 0 <= j < len(b):
                    num += a[i] * b[j]
                    den_a += a[i] * a[i]
                    den_b += b[j] * b[j]
            if den_a <= 0.0 or den_b <= 0.0:
                continue
            val = num / math.sqrt(den_a * den_b)
            if val > best_val:
                best_val, best_lag = val, lag
        return best_lag, max(0.0, min(1.0, best_val))

    @staticmethod
    def _beat_period(onsets: List[float]) -> Optional[int]:
        """Periodo de beat (en pasos de envolvente) por autocorrelación (0.3–1.0 s)."""
        if len(onsets) < 60:
            return None
        mean = sum(onsets) / len(onsets)
        centered = [v - mean for v in onsets]
        energy = sum(v * v for v in centered)
        if energy <= 0.0:
            return None
        low, high = int(0.3 * ENV_RATE), int(1.0 * ENV_RATE)
        best_lag, best_val = None, 0.0
        for lag in range(low, min(high, len(centered) - 1)):
            num = 0.0
            for i in range(len(centered) - lag):
                num += centered[i] * centered[i + lag]
            val = num / energy
            if val > best_val:
                best_val, best_lag = val, lag
        return best_lag

    def analyze_alignment(self, path: str, reference_path: str) -> AlignmentAnalysis:
        """Desfase por correlación de envolventes (±2000 ms de búsqueda).

        `offset_ms` es la corrección a aplicar: lag>0 (stem tarde) → negativo
        (recorte); lag<0 (stem temprano) → positivo (adelay).
        """
        stem_env = self._decode_envelope(path)
        ref_env = self._decode_envelope(reference_path)
        if len(stem_env) < 5 or len(ref_env) < 5:
            return AlignmentAnalysis(offset_ms=0, confidence=0.0)
        lag, confidence = self._peak_correlation(stem_env, ref_env, max_lags=100)
        return AlignmentAnalysis(offset_ms=int(-lag * ENV_MS), confidence=confidence)

    def analyze_tempo(self, path: str, reference_path: str) -> TempoAnalysis:
        """Ratio de tempo por periodo de beat (autocorrelación) y confianza por
        correlación de onsets stem/referencia (decisión D2)."""
        stem_on = self._onsets(self._decode_envelope(path))
        ref_on = self._onsets(self._decode_envelope(reference_path))
        if len(stem_on) < 30 or len(ref_on) < 30:
            return TempoAnalysis(ratio=1.0, confidence=0.0)

        _, confidence = self._peak_correlation(stem_on, ref_on, max_lags=100)
        stem_period = self._beat_period(stem_on)
        ref_period = self._beat_period(ref_on)
        if not stem_period or not ref_period:
            return TempoAnalysis(ratio=1.0, confidence=confidence)
        ratio = stem_period / ref_period
        ratio = max(0.5, min(2.0, ratio))
        return TempoAnalysis(ratio=round(ratio, 4), confidence=confidence)

    # --- render y exportación (SPEC005/SPEC007) ---

    @staticmethod
    def _atempo_chain(ratio: float) -> List[str]:
        """Cadena `atempo` para ratios fuera de [0.5, 2] (defensivo)."""
        parts: List[str] = []
        r = float(ratio)
        while r > 2.0:
            parts.append("atempo=2.0")
            r /= 2.0
        while r < 0.5:
            parts.append("atempo=0.5")
            r /= 0.5
        parts.append(f"atempo={r:.6f}")
        return parts

    def _stem_chain(self, rs: RenderStem) -> Tuple[List[str], str]:
        """Entradas previas (-ss para recorte) y cadena de filtros del stem.

        Orden: aformat → HPF → EQ → compresor → volumen → tempo → paneo → adelay.
        """
        inputs: List[str] = []
        if rs.offset_ms < 0:
            inputs += ["-ss", f"{-rs.offset_ms / 1000.0:.3f}"]
        inputs += ["-i", rs.path]

        f: List[str] = ["aformat=sample_fmts=fltp:channel_layouts=stereo"]
        if rs.hpf_hz:
            f.append(f"highpass=f={rs.hpf_hz:g}")
        for band in rs.eq:  # EqBand(gain_db, freq_hz)
            f.append(f"equalizer=f={band.freq_hz:g}:t=q:w=1:g={band.gain_db:g}")
        if (
            rs.compressor_threshold_db is not None
            and rs.compressor_ratio is not None
            and rs.compressor_attack_ms is not None
            and rs.compressor_release_ms is not None
        ):
            f.append(
                "acompressor="
                f"threshold={rs.compressor_threshold_db:g}dB"
                f":ratio={rs.compressor_ratio:g}"
                f":attack={rs.compressor_attack_ms:g}"
                f":release={rs.compressor_release_ms:g}"
            )
        total_gain = rs.gain_db + rs.makeup_gain_db
        if abs(total_gain) > 1e-6:
            f.append(f"volume={total_gain:.4f}dB")
        if rs.tempo_ratio is not None and abs(rs.tempo_ratio - 1.0) > 1e-6:
            f.extend(self._atempo_chain(rs.tempo_ratio))
        if abs(rs.pan) > 1e-6:
            p = max(-1.0, min(1.0, rs.pan))
            left = min(1.0, 1.0 - p)
            right = min(1.0, 1.0 + p)
            f.append(f"pan=stereo|c0={left:.4f}*c0|c1={right:.4f}*c1")
        if rs.offset_ms > 0:
            f.append(f"adelay={int(rs.offset_ms)}:all=1")
        return inputs, ",".join(f)

    def _mix_graph(
        self,
        stems: Sequence[RenderStem],
        normalization: Optional[Normalization],
    ) -> Tuple[List[str], str]:
        """Construye `-filter_complex`: filtros por stem + amix + normalización."""
        inputs: List[str] = []
        parts: List[str] = []
        for idx, rs in enumerate(stems):
            stem_inputs, chain = self._stem_chain(rs)
            inputs.extend(stem_inputs)
            parts.append(f"[{idx}:a]{chain}[s{idx}]")
        mix_refs = "".join(f"[s{i}]" for i in range(len(stems)))
        graph = ";".join(parts)
        graph += (
            f";{mix_refs}amix=inputs={len(stems)}:duration=longest:normalize=0[mix]"
        )
        if normalization is not None:
            graph += (
                f";[mix]loudnorm=I={normalization.lufs:g}"
                f":TP={normalization.true_peak_db:g}:LRA=11[fin]"
                ";[fin]aresample=44100[out]"
            )
        else:
            graph += ";[mix]aresample=44100[out]"
        return inputs, graph

    def duration_ms(self, path: str) -> int:
        proc = subprocess.run(  # noqa: S603 - lista de args, sin shell
            [
                self.ffprobe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            return int(float(proc.stdout.strip()) * 1000)
        except ValueError:
            raise DomainError("stem.decode_failed", {"path": path})

    def _render_to(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        out_args: List[str],
        failure_code: str,
        normalization: Optional[Normalization],
        on_progress: Optional[ProgressCallback],
        cancel: Optional[CancelCheck],
    ) -> None:
        """Ejecuta FFmpeg sobre el grafo de mezcla; limpia el parcial en fallo/cancel."""
        if not stems:
            raise DomainError("project.no_valid_stems")
        total_ms = 0
        for rs in stems:
            total_ms = max(total_ms, self.duration_ms(rs.path) + max(0, rs.offset_ms))
        inputs, graph = self._mix_graph(stems, normalization)
        cmd = [
            self.ffmpeg,
            "-nostdin", "-hide_banner", "-v", "error", "-y",
            "-progress", "pipe:1", "-nostats",
            *inputs,
            "-filter_complex", graph,
            "-map", "[out]",
            *out_args,
            out_path,
        ]
        try:
            self._run(
                cmd,
                total_ms=total_ms or None,
                failure_code=failure_code,
                on_progress=on_progress,
                cancel=cancel,
            )
        except AudioCancelled:
            self._safe_remove(out_path)
            raise
        except DomainError:
            self._safe_remove(out_path)
            raise
        if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
            raise DomainError(failure_code)

    @staticmethod
    def _safe_remove(path: str) -> None:
        try:
            if os.path.isfile(path):
                os.remove(path)
        except OSError:
            pass

    def render_mix(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        normalization: Optional[Normalization] = None,
        on_progress: Optional[ProgressCallback] = None,
        cancel: Optional[CancelCheck] = None,
    ) -> None:
        """WAV temporal estéreo 44.1 kHz/16-bit para vista previa (SPEC005 AC-03)."""
        self._render_to(
            stems,
            out_path,
            ["-c:a", "pcm_s16le", "-ar", "44100"],
            "render.failed",
            normalization,
            on_progress,
            cancel,
        )

    def export_mix(
        self,
        stems: Sequence[RenderStem],
        out_path: str,
        fmt: ExportFormat,
        normalization: Optional[Normalization] = None,
        on_progress: Optional[ProgressCallback] = None,
        cancel: Optional[CancelCheck] = None,
    ) -> None:
        """Exporta WAV 44.1 kHz/24-bit o MP3 320 kbps (SPEC007 AC-01/02)."""
        if fmt == ExportFormat.WAV_44100_24:
            out_args = ["-c:a", "pcm_s24le", "-ar", "44100"]
        else:
            out_args = ["-c:a", "libmp3lame", "-b:a", "320k", "-ar", "44100"]
        self._render_to(
            stems,
            out_path,
            out_args,
            "export.failed",
            normalization,
            on_progress,
            cancel,
        )


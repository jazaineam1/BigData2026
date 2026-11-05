"""S11: panel de progreso REAL para Colab/Jupyter con control de tareas.

Usar: panel=LiveMonitor(total); panel.show(); panel.start(...); panel.wait().
Al pulsar "Pausar" se detiene la admisión, no se abortan tareas activas.
Al cancelar no se declara completo un manifiesto parcial.
Si ipywidgets no está disponible, los eventos JSONL siguen siendo verificables.
"""
from __future__ import annotations
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import html
import json
from pathlib import Path
import threading

try:
    import ipywidgets as W
    from IPython.display import display
except ImportError:
    W = None
    display = None


class LiveMonitor:
    def __init__(self, sources: int, *, title="Laura · ETL Live", keep=14):
        if not 1 <= sources <= 2000:
            raise ValueError("Total de fuentes no válido")
        self.sources = sources
        self.title = title
        self.events = deque(maxlen=keep)
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        self.future = None
        self.executor = None
        self.result_data = None
        self._lock = threading.RLock()
        self._latest = None
        if W is not None:
            self.progress = W.IntProgress(min=0, max=sources, value=0,
                                          description="Fuentes:", bar_style="")
            self.stage = W.HTML(value="<b>Preparado</b> · no hay tareas en ejecución")
            self.rates = W.HTML(value="<small>Velocidad y trabajadores: sin mediciones todavía</small>")
            self.log = W.HTML(value="<small>Aquí aparecerán eventos REALES</small>")
            self.pause_button = W.Button(description="Pausar admisión", icon="pause",
                                         button_style="warning")
            self.cancel_button = W.Button(description="Cancelar", icon="stop", button_style="danger")
            self.pause_button.on_click(self._toggle_pause)
            self.cancel_button.on_click(self._cancel)
            self.widget = W.VBox([
                W.HTML(f"<h3>{html.escape(title)}</h3>"),
                self.stage, self.progress, self.rates,
                W.HBox([self.pause_button, self.cancel_button]), self.log,
                W.HTML("<small>Threads comparten un proceso. Los tiempos y el progreso provienen "
                       "de eventos del motor Python, no de una animación.</small>")
            ])
        else:
            self.widget = None

    def show(self):
        if self.widget is not None:
            display(self.widget)
        else:
            print("Panel de widgets no disponible; se registrará events.jsonl.")

    def _toggle_pause(self, _):
        if self.future is None or self.future.done():
            return
        if self.pause_event.is_set():
            self.pause_event.clear()
            if W is not None:
                self.pause_button.description = "Pausar admisión"
                self.pause_button.icon = "pause"
        else:
            self.pause_event.set()
            if W is not None:
                self.pause_button.description = "Reanudar admisión"
                self.pause_button.icon = "play"

    def _cancel(self, _):
        self.cancel_event.set()
        self.pause_event.clear()
        if W is not None:
            self.cancel_button.disabled = True
            self.pause_button.disabled = True
            self.stage.value = "<b>Cancelación solicitada:</b> finalizando tareas activas."

    def on_event(self, evt: dict):
        """Callback de eventos del coordinador; nunca modifica los datos ETL."""
        with self._lock:
            self._latest = dict(evt)
            self.events.append(evt)
            if W is None:
                if evt.get("state") in ("partition_saved", "finished", "failed", "cancelled"):
                    print(f"[LIVE] {evt.get('step')} {evt.get('state')}: "
                          f"{evt.get('completed_sources')}/{self.sources} "
                          f"{evt.get('derivatives_per_second')} deriv/s")
                return
            completed = min(int(evt.get("completed_sources", 0)), self.sources)
            self.progress.value = completed
            self.stage.value = (
                f"<b>Estado:</b> {html.escape(str(evt.get('state')))} · "
                f"<b>etapa:</b> {html.escape(str(evt.get('step')))} · "
                f"<b>{completed}/{self.sources}</b> fuentes"
            )
            self.rates.value = (
                f"<b>{evt.get('derivatives_per_second', 0):.2f}</b> derivados/s · "
                f"<b>{evt.get('sources_per_second', 0):.2f}</b> fuentes/s · "
                f"<b>{int(evt.get('workers', 1))}</b> threads · "
                f"<b>{evt.get('inflight', 0)}</b> tareas enviadas/en vuelo · "
                f"<b>{evt.get('retries', 0)}</b> reintentos · "
                f"<b>{evt.get('failed_sources', 0)}</b> fallos definitivos"
            )
            lines = []
            for record in list(self.events)[-10:]:
                label = html.escape(str(record.get("source_id") or record.get("partition") or ""))
                msg = html.escape(str(record.get("message") or ""))
                lines.append(
                    f"<tr><td>{record.get('seconds', 0):.2f}s</td>"
                    f"<td>{html.escape(str(record.get('state')))}</td>"
                    f"<td>{label}</td><td>{msg}</td></tr>"
                )
            self.log.value = ("<div style='max-height:185px;overflow:auto'>"
                              "<table style='font-size:12px;width:100%'>"
                              "<thead><tr><th>t</th><th>evento</th><th>fuente/lote</th><th>observación</th></tr></thead>"
                              "<tbody>" + "".join(lines) + "</tbody></table></div>")
            if evt.get("state") in ("finished", "failed", "cancelled"):
                self.cancel_button.disabled = True
                self.pause_button.disabled = True
                self.progress.bar_style = "success" if evt.get("state") == "finished" else "danger"

    def start(self, engine, root, images, audios, *, workers=2, batch_size=32,
              label="monitor", inject_once_at=None, core=None):
        """La ejecución ocurre EN SEGUNDO PLANO dentro de la sesión, no en un servidor.

        Este método retorna de inmediato y permite que botones de Jupyter
        procesen eventos mientras el motor trabaja.
        """
        if self.future is not None and not self.future.done():
            raise RuntimeError("Ya existe una ejecución activa en este panel")
        self.cancel_event.clear()
        self.pause_event.clear()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="s11-control")
        from functools import partial
        kwargs = dict(workers=workers, batch_size=batch_size, label=label,
                      on_event=self.on_event, cancel_event=self.cancel_event,
                      pause_event=self.pause_event, inject_once_at=inject_once_at, core=core)
        if getattr(engine, "__name__", "").endswith("s11_etl_live"):
            self.future = self.executor.submit(
                engine.run_live, root, images, audios, **kwargs
            )
        else:
            raise ValueError("El motor debe ser utils/s11_etl_live.py")
        return self.future

    def wait(self):
        """No fuerza un éxito: si se canceló o falló, devuelve el estado verificable."""
        if self.future is None:
            raise RuntimeError("Ejecuta primero start()")
        try:
            self.result_data = self.future.result()
            return self.result_data
        finally:
            if self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None

    def stop(self):
        """Cancelación programática, útil en pruebas automatizadas."""
        self._cancel(None)

    def snapshot(self):
        with self._lock:
            return dict(self._latest) if self._latest else None

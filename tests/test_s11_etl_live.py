"""S11 Live: tests de ejecución concurrente REAL, nunca tiempos inventados."""
from pathlib import Path
from threading import Event
import tempfile
import unittest
from unittest import mock
import json
import pandas as pd

from test_s11_etl import crear_datos
from utils import s11_etl_core as core
from utils import s11_etl_live as live


class TestS11Live(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(prefix="s11-live-test-")
        self.root = Path(self.t.name)
        self.fixture = crear_datos()
        self.patch_url = mock.patch.object(
            core, "obtener", side_effect=lambda url, limite: self.fixture[url]
        )
        self.patch_hash = mock.patch.object(
            core, "SHA_PARQUET", core.sha256(self.fixture[core.PARQUET_VOZ])
        )
        self.patch_url.start()
        self.patch_hash.start()
        self.images = core.extraer_imagenes(self.root, 4)
        self.audios = core.extraer_audios(self.root, 3)

    def tearDown(self):
        self.patch_url.stop()
        self.patch_hash.stop()
        self.t.cleanup()

    def test_mismo_fingerprint_por_workers_y_eventos_reales(self):
        runs = []
        for n in (1, 2, 4):
            events = []
            output = live.run_live(self.root, self.images, self.audios, workers=n,
                                   batch_size=8, label="qa", core=core,
                                   on_event=events.append)
            self.assertEqual(output["status"], "complete")
            self.assertTrue(output["verified"]["ok"])
            self.assertEqual(output["verified"]["rows"], 11)
            self.assertEqual(output["manifest"]["sources"], 7)
            self.assertEqual(output["manifest"]["expected_derivatives"], 11)
            self.assertEqual(output["manifest"]["workers"], n)
            self.assertEqual(events[-1]["state"], "finished")
            self.assertEqual(events[-1]["completed_sources"], 7)
            self.assertEqual(events[-1]["completed_derivatives"], 11)
            self.assertTrue(any(e["state"] == "partition_saved" for e in events))
            self.assertTrue(all(isinstance(e["seconds"], float) for e in events))
            self.assertTrue(all(e["workers"] == n for e in events))
            events_stored = [
                json.loads(s) for s in output["events_path"].read_text().splitlines()
            ]
            self.assertEqual(len(events), len(events_stored))
            runs.append(output["manifest"]["fingerprint"])
        self.assertEqual(len(set(runs)), 1, "Paralelismo alteró bytes o perfiles")

    def test_reintento_y_fallo_definitivo_no_se_marcan_exitosos(self):
        events = []
        result = live.run_live(self.root, self.images, self.audios, workers=2,
                               batch_size=8, label="retry", core=core,
                               inject_once_at=1, on_event=events.append)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["manifest"]["retries"], 1)
        self.assertTrue(any(e["state"] == "retry" for e in events))
        self.assertTrue(result["verified"]["ok"])
        failed = live.run_live(self.root, self.images, self.audios, workers=2,
                               batch_size=8, label="failure", core=core,
                               inject_always_at=1, max_retries=1)
        self.assertEqual(failed["status"], "failed")
        self.assertFalse(failed["verified"]["ok"])
        self.assertFalse(live.verify_run(self.root, failed["manifest_path"], core=core)["ok"])

    def test_cancelacion_parcial_y_recuperacion(self):
        cancel = Event()
        def handler(event):
            if event["state"] == "processed":
                cancel.set()
        result = live.run_live(self.root, self.images, self.audios, workers=2,
                               batch_size=8, label="cancel", core=core,
                               cancel_event=cancel, on_event=handler)
        self.assertEqual(result["status"], "cancelled")
        self.assertIsNone(result["manifest"]["fingerprint"])
        self.assertFalse(live.verify_run(self.root, result["manifest_path"], core=core)["ok"])
        again = live.run_live(self.root, self.images, self.audios, workers=2,
                              batch_size=8, label="recovered", core=core)
        self.assertEqual(again["status"], "complete")
        self.assertTrue(again["verified"]["ok"])

    def test_rechaza_cambios_y_benchmark_calcula_mediana_real(self):
        result = live.run_live(self.root, self.images, self.audios, workers=1,
                               batch_size=8, label="tamper", core=core)
        part = result["manifest"]["partitions"][0]["file"]
        file = result["manifest_path"].parent / part
        original = file.read_bytes()
        file.write_bytes(b"PARQUET_CORRUPTO")
        self.assertFalse(live.verify_run(self.root, result["manifest_path"], core=core)["ok"])
        file.write_bytes(original)
        self.assertTrue(live.verify_run(self.root, result["manifest_path"], core=core)["ok"])
        comp = live.run_benchmark(self.root, self.images, self.audios, workers=(1, 2, 4),
                                  repeats=2, batch_size=8, core=core)
        summary = comp["summary"]
        self.assertEqual(len(comp["measurements"]), 6)
        self.assertEqual(len(summary), 3)
        self.assertAlmostEqual(float(summary.loc[summary.workers == 1, "speedup"].iloc[0]), 1.)
        self.assertEqual(comp["measurements"]["fingerprint"].nunique(), 1)
        self.assertTrue((summary["seconds_median"] > 0).all())
        report = live.export_benchmark(comp)
        import zipfile
        with zipfile.ZipFile(report) as z:
            self.assertIsNone(z.testzip())
            self.assertIn("comparacion.csv", z.namelist())
            self.assertNotIn("raw", "\n".join(z.namelist()))

    def test_pausar_admision_real_y_reanudar_sin_perder_tareas(self):
        from concurrent.futures import ThreadPoolExecutor
        pause = Event()
        paused_seen = Event()
        events = []
        def callback(evt):
            events.append(evt)
            if evt["state"] == "queued" and evt["source_index"] == 0:
                pause.set()
            if evt["state"] == "paused":
                paused_seen.set()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(live.run_live, self.root, self.images, self.audios,
                                 workers=1, batch_size=8, label="pause",
                                 core=core, pause_event=pause, on_event=callback)
            self.assertTrue(paused_seen.wait(timeout=10), "No se publicó la pausa")
            self.assertFalse(future.done(), "La ejecución terminó mientras estaba pausada")
            pause.clear()
            result = future.result(timeout=50)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["verified"]["rows"], 11)
        self.assertTrue(any(x["state"] == "resumed" for x in events))
        self.assertEqual(events[-1]["state"], "finished")

    def test_fuentes_heterogeneas_uci_editorial_y_audio_en_threads(self):
        uci = core.extraer_imagenes_digitos(self.root, 12)
        all_images = self.images + uci
        result = live.run_live(self.root, all_images, self.audios,
                               workers=4, batch_size=8, label="qa_mix", core=core)
        self.assertEqual(result["status"], "complete")
        self.assertTrue(result["verified"]["ok"])
        self.assertEqual(result["verified"]["sources"], 19)
        self.assertEqual(result["verified"]["rows"], 35)
        import pandas as pd
        for part in result["manifest"]["partitions"]:
            frame = pd.read_parquet(result["manifest_path"].parent / part["file"])
            for _, row in frame.iterrows():
                if str(row["source_kind"]).startswith("UCI_digits"):
                    self.assertTrue(pd.isna(row["article_id"]))

    def test_pause_se_puede_reanudar_y_el_dashboard_refleja_eventos(self):
        from utils.s11_live_dashboard import LiveMonitor
        panel = LiveMonitor(sources=7)
        future = panel.start(live, self.root, self.images, self.audios,
                             workers=2, batch_size=8, label="widget")
        data = panel.wait()
        self.assertEqual(data["status"], "complete")
        snap = panel.snapshot()
        self.assertEqual(snap["state"], "finished")
        self.assertEqual(snap["completed_sources"], 7)
        self.assertTrue(future.done())


if __name__ == "__main__":
    unittest.main()

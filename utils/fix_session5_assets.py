#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajustes deterministas de los assets S5 antes de validarlos."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASTRA = ROOT / "assets" / "tutoriales" / "astra-cassandra-paso-a-paso-v2.html"


def main() -> None:
    text = ASTRA.read_text(encoding="utf-8")
    # El primer candidato real (MINISTERIO DEL DEPORTE) tiene 3 noticias: nivel baja.
    text = text.replace("7,'media','pendiente'", "3,'baja','pendiente'")
    if "3,'baja','pendiente'" not in text:
        raise RuntimeError("No se pudo fijar el control 3/baja del primer candidato.")
    ASTRA.write_text(text, encoding="utf-8")
    print("[OK] Tutorial Astra: primer candidato = 3 noticias, nivel baja.")


if __name__ == "__main__":
    main()

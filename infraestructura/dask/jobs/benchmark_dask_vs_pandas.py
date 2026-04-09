import argparse
import time
from pathlib import Path

import dask
import dask.dataframe as dd
import numpy as np
import pandas as pd
from dask.distributed import Client, performance_report, wait


DATA_DIR = Path("/app/benchmark_data")
DEFAULT_REPORT = Path("/app/benchmark_report.html")


def max_rss_mb() -> float:
    # Linux: ru_maxrss is in KB.
    import resource

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def generate_part(part_idx: int, rows: int) -> str:
    rng = np.random.default_rng(5000 + part_idx)

    start = np.datetime64("2026-01-01")
    end = np.datetime64("2026-04-01")
    seconds = int((end - start) / np.timedelta64(1, "s"))

    order_ts = start + rng.integers(0, seconds, rows).astype("timedelta64[s]")
    region = rng.choice(["Norte", "Sur", "Centro", "Occidente"], size=rows)
    category = rng.choice(["Tecnologia", "Hogar", "Deportes", "Moda"], size=rows)
    customer_id = rng.integers(1, 250_000, size=rows)
    units = rng.integers(1, 10, size=rows)
    unit_price = rng.uniform(10, 700, size=rows).round(2)
    discount = rng.choice([0.0, 0.05, 0.1, 0.15, 0.2], size=rows, p=[0.4, 0.2, 0.2, 0.15, 0.05])
    shipping_cost = rng.uniform(1, 30, size=rows).round(2)

    df = pd.DataFrame(
        {
            "order_id": np.arange(part_idx * rows, (part_idx + 1) * rows),
            "order_ts": order_ts.astype("datetime64[s]"),
            "region": region,
            "category": category,
            "customer_id": customer_id,
            "units": units,
            "unit_price": unit_price,
            "discount": discount,
            "shipping_cost": shipping_cost,
        }
    )

    out = DATA_DIR / f"part_{part_idx:02d}.csv"
    df.to_csv(out, index=False)
    return str(out)


def ensure_data(parts: int, rows_per_part: int, rebuild: bool) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(DATA_DIR.glob("part_*.csv"))
    if rebuild or len(existing) != parts:
        for f in existing:
            f.unlink()
        writes = [dask.delayed(generate_part)(i, rows_per_part) for i in range(parts)]
        dask.compute(*writes)


def add_business_columns_pandas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["order_ts"] = pd.to_datetime(df["order_ts"])
    df["gross_sales"] = df["units"] * df["unit_price"]
    df["net_sales"] = df["gross_sales"] * (1 - df["discount"])
    df["profit"] = df["net_sales"] - df["shipping_cost"] - (0.55 * df["gross_sales"])
    df["is_high_value"] = df["net_sales"] > 1200
    return df.set_index("order_ts")


def add_business_columns_dask(ddf: dd.DataFrame) -> dd.DataFrame:
    ddf["order_ts"] = dd.to_datetime(ddf["order_ts"])
    ddf["gross_sales"] = ddf["units"] * ddf["unit_price"]
    ddf["net_sales"] = ddf["gross_sales"] * (1 - ddf["discount"])
    ddf["profit"] = ddf["net_sales"] - ddf["shipping_cost"] - (0.55 * ddf["gross_sales"])
    ddf["is_high_value"] = ddf["net_sales"] > 1200
    return ddf.set_index("order_ts")


def aggregate_sales_pandas(df: pd.DataFrame) -> dict:
    return {
        "by_region": df.groupby("region")[["net_sales", "profit"]].sum().sort_index(),
        "by_cat": df.groupby(["region", "category"])[["net_sales", "profit"]].mean().sort_index(),
        "hourly": df["units"].resample("1h").sum().sort_index(),
        "high_value": df.groupby("region")["is_high_value"].mean().sort_index(),
    }


def aggregate_sales_dask(ddf: dd.DataFrame) -> dict:
    return {
        "by_region": ddf.groupby("region")[["net_sales", "profit"]].sum(),
        "by_cat": ddf.groupby(["region", "category"])[["net_sales", "profit"]].mean(),
        "hourly": ddf["units"].resample("1h").sum(),
        "high_value": ddf.groupby("region")["is_high_value"].mean(),
    }


def worker_summary(client: Client) -> list[dict]:
    info = client.scheduler_info()
    rows = []
    for address, meta in info.get("workers", {}).items():
        rows.append(
            {
                "address": address,
                "threads": meta.get("nthreads", 0),
                "memory_limit_mb": meta.get("memory_limit", 0) / (1024**2),
                "memory_used_mb": meta.get("metrics", {}).get("memory", 0) / (1024**2),
            }
        )
    return rows


def validate_results(pandas_results: dict, dask_results: dict) -> None:
    pd.testing.assert_frame_equal(
        pandas_results["by_region"],
        dask_results["by_region"],
        check_exact=False,
        check_dtype=False,
        rtol=1e-6,
        atol=1e-6,
    )
    pd.testing.assert_frame_equal(
        pandas_results["by_cat"],
        dask_results["by_cat"],
        check_exact=False,
        check_dtype=False,
        rtol=1e-6,
        atol=1e-6,
    )
    pd.testing.assert_series_equal(
        pandas_results["hourly"],
        dask_results["hourly"],
        check_exact=False,
        check_dtype=False,
        rtol=1e-6,
        atol=1e-6,
    )
    pd.testing.assert_series_equal(
        pandas_results["high_value"],
        dask_results["high_value"],
        check_exact=False,
        check_dtype=False,
        rtol=1e-6,
        atol=1e-6,
    )


def normalize_materialized_results(results: dict) -> dict:
    normalized = {}
    for key, value in results.items():
        if hasattr(value, "sort_index"):
            value = value.sort_index()
        if isinstance(value.index, pd.MultiIndex):
            value.index = pd.MultiIndex.from_tuples(list(value.index), names=value.index.names)
        else:
            value.index = pd.Index(value.index.tolist(), name=value.index.name)
        normalized[key] = value
    return normalized


def run_dask(cluster_addr: str, report_path: Path) -> dict:
    client = Client(cluster_addr)
    t0 = time.perf_counter()

    with performance_report(filename=str(report_path)):
        ddf = dd.read_csv(f"{DATA_DIR}/part_*.csv", blocksize=None)
        ddf = add_business_columns_dask(ddf)

        # Fuerza un shuffle para que la clase vea intercambio de datos entre workers.
        ddf = ddf.persist()
        wait(ddf)
        ddf = ddf.set_index("order_ts").persist()
        wait(ddf)

        results = aggregate_sales_dask(ddf)
        computed = dask.compute(*results.values())

    elapsed = time.perf_counter() - t0
    materialized = normalize_materialized_results(dict(zip(results.keys(), computed, strict=True)))
    workers = worker_summary(client)
    client.close()
    return {
        "elapsed_s": elapsed,
        "workers": workers,
        "worker_count": len(workers),
        "worker_mem_mb": sum(w["memory_used_mb"] for w in workers),
        "results": materialized,
        "report_path": str(report_path),
    }


def run_pandas() -> dict:
    t0 = time.perf_counter()
    files = sorted(DATA_DIR.glob("part_*.csv"))
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)
    df = add_business_columns_pandas(df)
    results = aggregate_sales_pandas(df)

    elapsed = time.perf_counter() - t0
    df_mem_mb = df.memory_usage(deep=True).sum() / (1024**2)
    proc_peak_mb = max_rss_mb()
    return {
        "elapsed_s": elapsed,
        "df_mem_mb": df_mem_mb,
        "proc_peak_mb": proc_peak_mb,
        "results": normalize_materialized_results(results),
    }


def print_worker_table(workers: list[dict]) -> None:
    if not workers:
        print("No se detectaron workers.")
        return

    print("Detalle de workers:")
    for worker in workers:
        print(
            "  - {address} | threads={threads} | limit={memory_limit_mb:.1f} MB | used={memory_used_mb:.1f} MB".format(
                **worker
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark simple: Pandas vs Dask")
    parser.add_argument("--parts", type=int, default=6, help="Numero de archivos/particiones")
    parser.add_argument("--rows-per-part", type=int, default=250_000, help="Filas por particion")
    parser.add_argument("--cluster", default="tcp://dask-scheduler:8786", help="Direccion del scheduler Dask")
    parser.add_argument("--rebuild-data", action="store_true", help="Regenera archivos CSV")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT), help="Ruta del performance report HTML de Dask")
    parser.add_argument("--skip-pandas", action="store_true", help="No corre benchmark de Pandas")
    parser.add_argument("--skip-dask", action="store_true", help="No corre benchmark de Dask")
    args = parser.parse_args()

    total_rows = args.parts * args.rows_per_part
    print(f"Dataset objetivo: {args.parts} partes x {args.rows_per_part:,} filas = {total_rows:,} filas")
    ensure_data(args.parts, args.rows_per_part, rebuild=args.rebuild_data)
    print(f"Archivos disponibles en: {DATA_DIR}")

    p = None
    if not args.skip_pandas:
        p = run_pandas()
        print("\n[PANDAS]")
        print(f"Tiempo total: {p['elapsed_s']:.2f} s")
        print(f"Memoria DataFrame aprox: {p['df_mem_mb']:.1f} MB")
        print(f"Pico proceso (RSS): {p['proc_peak_mb']:.1f} MB")

    d = None
    if not args.skip_dask:
        d = run_dask(args.cluster, Path(args.report_path))
        print("\n[DASK]")
        print(f"Tiempo total: {d['elapsed_s']:.2f} s")
        print(f"Workers detectados: {d['worker_count']}")
        print(f"Memoria agregada workers (instante final): {d['worker_mem_mb']:.1f} MB")
        print_worker_table(d["workers"])
        print(f"Performance report: {d['report_path']}")

    if p and d:
        validate_results(p["results"], d["results"])
        speedup = p["elapsed_s"] / d["elapsed_s"] if d["elapsed_s"] else float("inf")
        print("\n[VALIDACION]")
        print("Los resultados agregados de Pandas y Dask coinciden dentro de tolerancia numerica.")
        print(f"Speedup Pandas/Dask: {speedup:.2f}x")
        if speedup > 1:
            print("En este escenario, Dask fue mas rapido que Pandas.")
        else:
            print("En este escenario, Pandas fue mas rapido; aumenta filas o workers para ver mejor el beneficio distribuido.")

    print("\nTip: mira Task Stream y Workers en http://localhost:8787 mientras corre Dask.")


if __name__ == "__main__":
    main()

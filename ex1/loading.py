import importlib
import importlib.metadata
import importlib.util
import sys

DEPENDENCIES: dict[str, str] = {
    "pandas": "Data manipulation",
    "numpy": "Numerical computation",
    "matplotlib": "Visualization",
}

PIP_SPECS: dict[str, str] = {
    "pandas": ">=2.2,<3.0",
    "numpy": ">=2.0,<3.0",
    "matplotlib": ">=3.8,<4.0",
}

POETRY_SPECS: dict[str, str] = {
    "pandas": "^2.2",
    "numpy": "^2.0",
    "matplotlib": "^3.8",
}

DATA_POINTS = 1000
WINDOW = 50
OUTPUT_FILE = "matrix_analysis.png"


def get_version(name: str) -> str | None:
    if importlib.util.find_spec(name) is None:
        return None
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def check_dependencies() -> dict[str, str | None]:
    print("Checking dependencies:")
    versions: dict[str, str | None] = {}
    for name, purpose in DEPENDENCIES.items():
        version = get_version(name)
        versions[name] = version
        if version is None:
            print(f"[MISSING] {name} - {purpose} unavailable")
        else:
            print(f"[OK] {name} ({version}) - {purpose} ready")
    return versions


def detect_manager() -> str:
    if sys.prefix == sys.base_prefix:
        return "global Python (no virtual environment)"
    if "pypoetry" in sys.prefix.lower():
        return "Poetry managed virtual environment"
    return "virtual environment (venv + pip, or Poetry in-project)"


def compare_versions(versions: dict[str, str | None]) -> None:
    print("Package versions:")
    print(f"  {'package':<12}{'installed':<12}{'pip':<14}Poetry")
    for name in DEPENDENCIES:
        installed = versions[name] or "missing"
        pip_spec = PIP_SPECS[name]
        poetry_spec = POETRY_SPECS[name]
        print(f"  {name:<12}{installed:<12}{pip_spec:<14}{poetry_spec}")


def print_manager_differences() -> None:
    print("pip vs Poetry:")
    print("  pip    : reads requirements.txt, installs into the active")
    print("           environment, no lock file, you manage the venv")
    print("  Poetry : reads pyproject.toml, resolves the whole tree,")
    print("           writes poetry.lock and manages its own venv")


def print_install_help() -> None:
    print("To load the missing programs:")
    print("  With pip:")
    print("    pip install -r requirements.txt")
    print("    python3 loading.py")
    print("  With Poetry:")
    print("    poetry install")
    print("    poetry run python loading.py")


def run_analysis() -> None:
    np = importlib.import_module("numpy")
    pd = importlib.import_module("pandas")
    matplotlib = importlib.import_module("matplotlib")
    matplotlib.use("Agg")
    plt = importlib.import_module("matplotlib.pyplot")

    print("Analyzing Matrix data...")
    rng = np.random.default_rng(42)
    ticks = np.arange(DATA_POINTS)
    noise = rng.normal(0.0, 2.0, DATA_POINTS)
    data = pd.DataFrame({
        "tick": ticks,
        "signal": np.sin(ticks / 40.0) * 10.0 + noise,
        "agents": rng.poisson(3.0, DATA_POINTS),
    })
    print(f"Processing {len(data)} data points...")

    data["trend"] = data["signal"].rolling(WINDOW, min_periods=1).mean()
    residual = data["signal"] - data["trend"]
    anomalies = data[residual.abs() > 2 * residual.std()]
    print(f"  Mean signal: {data['signal'].mean():.3f}")
    print(f"  Signal std: {data['signal'].std():.3f}")
    print(f"  Max agents in one tick: {data['agents'].max()}")
    print(f"  Anomalies detected: {len(anomalies)}")

    print("Generating visualization...")
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(data["tick"], data["signal"], color="green", alpha=0.4,
                 label="Signal")
    axes[0].plot(data["tick"], data["trend"], color="black",
                 label=f"Rolling mean ({WINDOW})")
    axes[0].scatter(anomalies["tick"], anomalies["signal"], color="red",
                    s=12, label="Anomalies")
    axes[0].set_title("Matrix signal analysis")
    axes[0].set_ylabel("Signal")
    axes[0].legend()
    axes[1].bar(data["tick"], data["agents"], color="darkgreen", width=1.0)
    axes[1].set_xlabel("Tick")
    axes[1].set_ylabel("Agents detected")
    fig.tight_layout()
    try:
        fig.savefig(OUTPUT_FILE)
    finally:
        plt.close(fig)

    print()
    print("Analysis complete!")
    print(f"Results saved to: {OUTPUT_FILE}")


def main() -> None:
    print("LOADING STATUS: Loading programs...")
    print()
    versions = check_dependencies()
    print()
    print(f"Environment: {detect_manager()}")
    print()
    compare_versions(versions)
    print()
    print_manager_differences()
    print()

    missing = [name for name, version in versions.items() if version is None]
    if missing:
        print(f"ERROR: missing dependencies: {', '.join(missing)}")
        print()
        print_install_help()
        sys.exit(1)

    try:
        run_analysis()
    except ImportError as error:
        print(f"ERROR: could not load a dependency: {error}")
        print()
        print_install_help()
        sys.exit(1)
    except OSError as error:
        print(f"ERROR: could not save {OUTPUT_FILE}: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

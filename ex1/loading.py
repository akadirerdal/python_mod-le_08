"""Exercise 1: Loading Programs - data analysis with managed packages.

Uses pandas for data manipulation, numpy for numerical computations
and data generation, and matplotlib for visualization.
Demonstrates pip vs Poetry dependency management.

Authorized modules: pandas, requests, matplotlib, numpy, sys, importlib.
"""

import importlib.metadata
import importlib.util
import sys
import pandas as pd

# Pinned requirements mirroring what pip and Poetry would use
REQUIRED: dict[str, str] = {
    "pandas": "^2.2",
    "numpy": "^2.0",
    "matplotlib": "^3.8",
}

DATA_POINTS = 1000
OUTPUT_PNG = "matrix_analysis.png"


def installed_version(name: str) -> str | None:
    """Return the installed version of a package, None if missing."""
    if importlib.util.find_spec(name) is None:
        return None
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def check_dependencies() -> dict[str, str | None]:
    """Check every required package and return installed versions."""
    report: dict[str, str | None] = {}
    for name in REQUIRED:
        report[name] = installed_version(name)
    return report


def print_dependency_report(report: dict[str, str | None]) -> None:
    """Print the dependency status report."""
    print("LOADING STATUS: Loading programs...")
    print("Checking dependencies:")
    all_ok = True
    for name in sorted(report.keys()):
        version = report[name]
        if version is not None:
            print(f"[OK] {name} ({version}) - ready")
        else:
            all_ok = False
            print(f"[MISSING] {name} - Not installed")
    return all_ok


def generate_matrix_data(n: int = DATA_POINTS) -> object:
    """Generate simulated Matrix data using numpy."""
    import numpy as np

    rng = np.random.default_rng(seed=42)
    # Simulate two transmission teams: red pill and blue pill
    red_sig = rng.normal(loc=0.0, scale=1.0, size=n)
    blue_sig = rng.normal(loc=0.5, scale=1.5, size=n)
    data = pd.DataFrame(
        {
            "red_pill_signal": red_sig,
            "blue_pill_signal": blue_sig,
            "transmission_id": range(n),
        }
    )
    return data


def analyze_data(data: object) -> None:
    """Analyze Matrix data using pandas and print summary stats."""
    import pandas as pd

    print("Analyzing Matrix data...")
    print(f"Processing {len(data)} data points...")
    if hasattr(data, "describe"):
        summary = data.describe()
        print(summary)
    else:
        print("Data summary (count, mean, std, min, max):")
        print(f"  Count: {len(data)}")


def visualize_data(data: object) -> None:
    """Generate a Matrix data visualization using matplotlib."""
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt

    red_sig = data["red_pill_signal"] if hasattr(data, "__getitem__") else []
    blue_sig = data["blue_pill_signal"] if hasattr(data, "__getitem__") else []

    plt.figure(figsize=(10, 6))
    if red_sig and blue_sig:
        plt.hist(
            [red_sig, blue_sig],
            bins=30,
            label=["Red Pill", "Blue Pill"],
            alpha=0.7,
        )
    plt.title("Matrix Transmission Signal Strengths")
    plt.xlabel("Signal amplitude")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG)
    print("Generating visualization...")
    print("Analysis complete!")
    print(f"Results saved to: {OUTPUT_PNG}")
    plt.close()


def print_manager_comparison() -> None:
    """Show the differences between pip and Poetry dependency management."""
    print()
    print("Dependency management comparison:")
    print("  pip    : uses requirements.txt with flexible version ranges")
    print("           pip install -r requirements.txt")
    print("  Poetry : uses pyproject.toml with locked dependencies")
    print("           poetry install && poetry run python loading.py")
    print()
    print("Pinned requirements (pip):")
    for name, req in sorted(REQUIRED.items()):
        print(f"    {name}{req}")
    print()
    print("Poetry pyproject.toml equivalent would lock exact")
    print("versions and create a poetry.lock for reproducibility.")


def main() -> None:
    """Entry point: check deps, analyze, visualize."""
    report = check_dependencies()
    all_ok = print_dependency_report(report)

    if not all_ok:
        print()
        print("Some dependencies are missing.")
        print("Install with pip:")
        print("  pip install -r requirements.txt")
        print()
        print("Install with Poetry:")
        print("  poetry install")
        sys.exit(1)

    # All deps available — generate and analyze data
    data = generate_matrix_data()
    analyze_data(data)
    visualize_data(data)

    print_manager_comparison()


if __name__ == "__main__":
    main()

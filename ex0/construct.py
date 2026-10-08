import os
import site
import sys


def is_virtual_env() -> bool:
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def site_packages() -> list[str]:
    try:
        paths = site.getsitepackages()
    except AttributeError:
        paths = sys.path
    filtered = [path for path in paths if path.endswith("site-packages")]
    return filtered or paths


def print_outside() -> None:
    print("MATRIX STATUS: You're still plugged in")
    print()
    print(f"Current Python: {sys.executable}")
    print("Virtual Environment: None detected")
    print()
    print("WARNING: You're in the global environment!")
    print("The machines can see everything you install.")
    print()
    print("Global package locations:")
    for path in site_packages():
        print(f"  {path}")
    print(f"  {site.getusersitepackages()} (user installs)")
    print()
    print("To enter the construct, run:")
    print("python -m venv matrix_env")
    print("source matrix_env/bin/activate # On Unix")
    print("matrix_env\\Scripts\\activate # On Windows")
    print()
    print("Then run this program again.")


def print_inside() -> None:
    print("MATRIX STATUS: Welcome to the construct")
    print()
    print(f"Current Python: {sys.executable}")
    print(f"Virtual Environment: {os.path.basename(sys.prefix)}")
    print(f"Environment Path: {sys.prefix}")
    print()
    print("SUCCESS: You're in an isolated environment!")
    print("Safe to install packages without affecting")
    print("the global system.")
    print()
    print("Package installation path:")
    for path in site_packages():
        print(path)
    print()
    print(f"Global Python base (untouched): {sys.base_prefix}")


def main() -> None:
    if is_virtual_env():
        print_inside()
    else:
        print_outside()


if __name__ == "__main__":
    main()

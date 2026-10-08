"""Exercise 0: Entering the Matrix.

Detect whether the current Python interpreter runs inside a virtual
environment and display information about the active environment,
including instructions to create a virtual environment and the
difference between global and virtual package locations.

Authorized modules: sys, os, site (and the print() function).
"""

import os
import site
import sys


def is_virtual_env() -> bool:
    """Return True when running inside a virtual environment."""
    if hasattr(sys, "real_prefix"):
        return True
    return sys.prefix != sys.base_prefix


def virtual_env_name() -> str:
    """Return the folder name of the active virtual environment."""
    return os.path.basename(sys.prefix)


def package_locations() -> list[str]:
    """Return the site-package locations for this interpreter."""
    try:
        return site.getsitepackages()
    except Exception:  # noqa: E722
        return []


def print_global_report() -> None:
    """Print the report shown outside a virtual environment."""
    print("MATRIX STATUS: You're still plugged in")
    print(f"Current Python: {sys.executable}")
    print("Virtual Environment: None detected")
    print("WARNING: You're in the global environment!")
    print("The machines can see everything you install.")
    print()
    print("To enter the construct, run:")
    print("  python -m venv matrix_env")
    print("  source matrix_env/bin/activate   # On Unix (Linux/macOS)")
    print("  matrix_env\\Scripts\\activate      # On Windows")
    print("Then run this program again.")
    print()
    print("Global package locations:")
    for path in package_locations():
        print(f"  {path}")
    user_site = site.getusersitepackages()
    print(f"  {user_site}   (user site, --user installs)")
    print("In a virtual environment, packages are installed in")
    print("the environment folder instead, leaving the global")
    print("site-packages untouched.")


def print_virtual_report() -> None:
    """Print the report shown inside a virtual environment."""
    print("MATRIX STATUS: Welcome to the construct")
    print(f"Current Python: {sys.executable}")
    print(f"Virtual Environment: {virtual_env_name()}")
    print(f"Environment Path: {sys.prefix}")
    print("SUCCESS: You're in an isolated environment!")
    print("Safe to install packages without affecting")
    print("the global system.")
    print()
    print("Package installation path:")
    for path in package_locations():
        print(f"  {path}")
    print()
    print("Global env base: {0} (system Python)".format(sys.base_prefix))
    print(
        "Global packages are NOT used from inside the construct "
        "(unless the venv was created with --system-site-packages)."
    )


def main() -> None:
    """Entry point: print the report for the current environment."""
    if is_virtual_env():
        print_virtual_report()
    else:
        print_global_report()


if __name__ == "__main__":
    main()
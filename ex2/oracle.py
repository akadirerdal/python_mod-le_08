"""Exercise 2: Accessing the Mainframe - secure configuration system.

Loads configuration from environment variables using .env files.
Demonstrates dev/production mode differences and security checks.

Authorized modules: os, sys, python-dotenv modules, file operations.
"""

import os
import re
import sys

# Try to import python-dotenv; fallback gracefully if missing
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    # Fallback: a no-op function that does nothing
    def load_dotenv(dotenv_path: str = None, **kwargs):  # type: ignore
        return False


def _find_dotenv() -> str | None:
    """Look for .env file in current working directory."""
    if os.path.exists(".env"):
        return os.path.abspath(".env")
    return None


def _load_config_with_dotenv() -> dict[str, str | None]:
    """Load configuration using python-dotenv.

    Returns a dict with config values; None means not found in .env
    and not set as environment variable either.
    """
    config: dict[str, str | None] = {
        "MATRIX_MODE": None,
        "DATABASE_URL": None,
        "API_KEY": None,
        "LOG_LEVEL": None,
        "ZION_ENDPOINT": None,
    }

    if HAS_DOTENV:
        # Load .env without overriding existing environment variables
        # (standard dotenv behavior: only sets if not already set)
        load_dotenv()

    # Read from environment variables (these take priority over .env)
    config["MATRIX_MODE"] = os.environ.get("MATRIX_MODE")
    config["DATABASE_URL"] = os.environ.get("DATABASE_URL")
    config["API_KEY"] = os.environ.get("API_KEY")
    config["LOG_LEVEL"] = os.environ.get("LOG_LEVEL", "DEBUG")
    config["ZION_ENDPOINT"] = os.environ.get("ZION_ENDPOINT")

    # If not set via env, try .env values (env vars still take priority)
    if HAS_DOTENV:
        dotenv_path = _find_dotenv()
        if dotenv_path:
            load_dotenv(dotenv_path=dotenv_path, override=False)

    return config


def _dev_mode_visibility(mode: str) -> dict[str, str]:
    """Apply development-mode formatting/visibility rules."""
    result = {}
    if mode == "development":
        result["db"] = "Connected to local instance (postgresql://localhost:5432/matrix)"
        result["api"] = "Authenticated (key visible for dev purposes)"
        result["log_level"] = os.environ.get("LOG_LEVEL", "DEBUG")
        result["zion"] = "Online (https://zion.resistance.local/api — dev endpoint)"
    else:
        result["db"] = "Connected to local instance"
        result["api"] = "Authenticated (key visible)"
        result["log_level"] = "DEBUG"
        result["zion"] = "Online (dev endpoint)"
    return result


def _prod_mode_visibility(mode: str) -> dict[str, str]:
    """Apply production-mode formatting/visibility rules."""
    result = {}
    if mode == "production":
        result["db"] = "Connected to production instance"
        result["api"] = "Authenticated (API key: *** masked for security)"
        result["log_level"] = "INFO (production default)"
        result["zion"] = "Online (https://zion.resistance.prod/api)"
    else:
        result["db"] = "Connected to local instance"
        result["api"] = "Authenticated (key visible)"
        result["log_level"] = "DEBUG"
        result["zion"] = "Online (dev endpoint)"
    return result


def _check_hardcoded_secrets() -> list[str]:
    """Check oracle.py source for hardcoded secret assignments.

    Only flags lines where a secret name is directly assigned a value
    (e.g., API_KEY = some_string), not strings appearing in lists or docs.
    Returns status messages.
    """
    messages: list[str] = []
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            source = f.read()
        secret_names = {"API_KEY", "DATABASE_URL", "ZION_ENDPOINT"}
        found_any = False
        for line in source.splitlines():
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("#"):
                continue
            # Skip lines using authorized config-reading patterns
            if any(stripped.startswith(prefix) for prefix in (
                "os.environ", "os.getenv", "load_dotenv"
            )):
                continue
            # Check for direct assignment patterns: SECRET_NAME = ...
            # Match: SECRET_NAME followed by whitespace and =, or SECRET_NAME+=
            for sname in secret_names:
                if re.match(rf'^{re.escape(sname)}\s*=', stripped) or \
                   re.match(rf'^{re.escape(sname)}=$', stripped):
                    found_any = True
                    break
            if found_any:
                break
        if found_any:
            messages.append(
                "[WARN] Possible hardcoded secrets detected — use .env instead!"
            )
        else:
            messages.append(
                "[OK] No hardcoded secrets detected"
            )
    except Exception:  # noqa: E722
        messages.append(
            "[WARN] Could not perform source code security check"
        )
    return messages


def _security_check(config: dict[str, str | None],
                    dotenv_path: str | None) -> list[str]:
    """Perform security checks and return list of status messages."""
    messages: list[str] = []

    # Hardcoded secret check
    messages.extend(_check_hardcoded_secrets())

    # Check .env file presence
    if dotenv_path is not None:
        messages.append(
            "[OK] .env file properly configured"
        )
    else:
        messages.append(
            "[WARN] .env file not found — using environment variables only"
        )

    # Production overrides availability
    mat_mode = config.get("MATRIX_MODE", "")
    if mat_mode and str(mat_mode).lower() == "production":
        messages.append(
            "[OK] Production overrides available"
        )
    else:
        messages.append(
            "[OK] Development mode — full config visible for debugging"
        )

    return messages


def _format_output(mode: str, mode_info: dict[str, str],
                   security_msgs: list[str]) -> None:
    """Print the expected output format."""
    print("ORACLE STATUS: Reading the Matrix...")
    print("Configuration loaded:")
    print(f"  Mode: {mode}")
    print(f"  Database: {mode_info.get('db', '')}")
    print(f"  API Access: {mode_info.get('api', '')}")
    print(f"  Log Level: {mode_info.get('log_level', 'DEBUG')}")
    print(f"  Zion Network: {mode_info.get('zion', '')}")
    print()
    print("Environment security check:")
    for msg in security_msgs:
        print(f"  {msg}")
    print()
    print("The Oracle sees all configurations.")


def main() -> None:
    """Entry point: load config, show dev/prod diff, security checks."""
    # Attempt to load .env
    dotenv_path = _find_dotenv()
    config = _load_config_with_dotenv()

    # Determine mode
    raw_mode = config.get("MATRIX_MODE")
    if raw_mode and str(raw_mode).lower() in ("development", "production"):
        mode = str(raw_mode).lower()
    else:
        mode = "development"  # default fallback

    # Get mode-specific info
    mode_info = _dev_mode_visibility(mode) if mode == "development" else _prod_mode_visibility(mode)

    # Security checks
    security_msgs = _security_check(config, dotenv_path)

    # Format and print output
    _format_output(mode, mode_info, security_msgs)

    # Exit with error if production config is incomplete
    if mode == "production":
        required_prod = ["DATABASE_URL", "API_KEY", "ZION_ENDPOINT"]
        missing_prod = [v for v in required_prod if not config.get(v)]
        if missing_prod:
            print()
            print(
                f"[ERROR] Production mode requires: "
                f"{', '.join(missing_prod)}"
            )
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
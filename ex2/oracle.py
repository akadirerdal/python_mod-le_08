import os
import sys

try:
    from dotenv import dotenv_values, load_dotenv
except ImportError:
    print("ORACLE STATUS: Connection lost")
    print("ERROR: python-dotenv is not installed.")
    print("Install it with: pip install -r requirements.txt")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
GITIGNORE_FILE = os.path.join(BASE_DIR, ".gitignore")

KEYS = ("MATRIX_MODE", "DATABASE_URL", "API_KEY", "LOG_LEVEL",
        "ZION_ENDPOINT")
REQUIRED = ("DATABASE_URL", "API_KEY", "ZION_ENDPOINT")
SECRETS = ("DATABASE_URL", "API_KEY")
MODES = ("development", "production")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
DEFAULT_LOG_LEVEL = {"development": "DEBUG", "production": "WARNING"}


def load_config() -> tuple[dict[str, str | None], dict[str, str]]:
    from_shell = {key for key in KEYS if os.environ.get(key)}
    file_values: dict[str, str | None] = {}
    if os.path.isfile(ENV_FILE):
        try:
            file_values = dict(dotenv_values(ENV_FILE))
            load_dotenv(ENV_FILE, override=False)
        except (OSError, UnicodeDecodeError) as error:
            print(f"[WARN] Could not read .env file: {error}")

    config: dict[str, str | None] = {}
    sources: dict[str, str] = {}
    for key in KEYS:
        config[key] = os.environ.get(key) or None
        if key in from_shell:
            sources[key] = "environment variable"
        elif file_values.get(key):
            sources[key] = ".env file"
        else:
            sources[key] = "missing"
    return config, sources


def resolve_mode(config: dict[str, str | None], sources: dict[str, str],
                 warnings: list[str]) -> str:
    raw = config["MATRIX_MODE"]
    if raw is not None and raw.lower() in MODES:
        return raw.lower()
    if raw is None:
        warnings.append("MATRIX_MODE not set, defaulting to development")
    else:
        warnings.append(f"Unknown MATRIX_MODE '{raw}', "
                        "defaulting to development")
    sources["MATRIX_MODE"] = "default"
    return "development"


def resolve_log_level(config: dict[str, str | None], sources: dict[str, str],
                      mode: str, warnings: list[str]) -> str:
    raw = config["LOG_LEVEL"]
    if raw is not None and raw.upper() in LOG_LEVELS:
        level = raw.upper()
        if mode == "production" and level == "DEBUG":
            warnings.append("DEBUG logging is not recommended in production")
        return level
    default = DEFAULT_LOG_LEVEL[mode]
    if raw is None:
        warnings.append(f"LOG_LEVEL not set, defaulting to {default}")
    else:
        warnings.append(f"Unknown LOG_LEVEL '{raw}', "
                        f"defaulting to {default}")
    sources["LOG_LEVEL"] = "default"
    return default


def mask_url(url: str) -> str:
    if "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if "@" in rest:
        rest = "***@" + rest.rsplit("@", 1)[1]
    return f"{scheme}://{rest}"


def describe_database(url: str | None, mode: str) -> str:
    if not url:
        return "Not configured"
    local = any(host in url for host in ("localhost", "127.0.0.1", "sqlite"))
    place = "local instance" if local else "remote instance"
    if mode == "development":
        return f"Connected to {place} ({mask_url(url)})"
    return f"Connected to {place}"


def describe_api(key: str | None, mode: str) -> str:
    if not key:
        return "Disabled (no API key)"
    if mode == "development":
        return f"Authenticated (key: {key[:4]}{'*' * 8})"
    return "Authenticated"


def describe_zion(url: str | None, mode: str) -> str:
    if not url:
        return "Offline (no endpoint)"
    if not url.startswith("https://"):
        return f"Online (insecure: {url})"
    if mode == "development":
        return f"Online ({url})"
    return "Online"


def check_hardcoded_secrets(config: dict[str, str | None]) -> str:
    try:
        with open(__file__, "r", encoding="utf-8") as file:
            source = file.read()
    except OSError:
        return "[WARN] Could not scan source for hardcoded secrets"
    for key in SECRETS:
        value = config[key]
        if value is not None and len(value) >= 8 and value in source:
            return f"[WARN] {key} value is hardcoded in oracle.py"
    return "[OK] No hardcoded secrets detected"


def check_env_file() -> str:
    if not os.path.isfile(ENV_FILE):
        return "[WARN] No .env file found (cp .env.example .env)"
    try:
        with open(GITIGNORE_FILE, "r", encoding="utf-8") as file:
            ignored = ".env" in [line.strip() for line in file]
    except OSError:
        ignored = False
    if not ignored:
        return "[WARN] .env file is not listed in .gitignore"
    return "[OK] .env file properly configured"


def check_overrides(sources: dict[str, str]) -> str:
    overridden = [key for key in KEYS
                  if sources[key] == "environment variable"]
    if overridden:
        return f"[OK] Production overrides active: {', '.join(overridden)}"
    return "[OK] Production overrides available"


def main() -> None:
    print("ORACLE STATUS: Reading the Matrix...")
    print()

    config, sources = load_config()
    warnings: list[str] = []
    mode = resolve_mode(config, sources, warnings)
    log_level = resolve_log_level(config, sources, mode, warnings)
    missing = [key for key in REQUIRED if not config[key]]
    for key in missing:
        warnings.append(f"{key} is not set")

    print("Configuration loaded:")
    print(f"Mode: {mode}")
    print(f"Database: {describe_database(config['DATABASE_URL'], mode)}")
    print(f"API Access: {describe_api(config['API_KEY'], mode)}")
    print(f"Log Level: {log_level}")
    print(f"Zion Network: {describe_zion(config['ZION_ENDPOINT'], mode)}")
    print()

    if mode == "development":
        print("Configuration sources (development only):")
        for key in KEYS:
            print(f"  {key}: {sources[key]}")
    else:
        print("Production mode: secrets hidden, debug details disabled")
    print()

    if warnings:
        print("Configuration warnings:")
        for warning in warnings:
            print(f"[WARN] {warning}")
        print()

    print("Environment security check:")
    print(check_hardcoded_secrets(config))
    print(check_env_file())
    print(check_overrides(sources))
    print()

    if mode == "production" and missing:
        print(f"[ERROR] Production mode requires: {', '.join(missing)}")
        print("The Oracle cannot see the full Matrix.")
        sys.exit(1)
    print("The Oracle sees all configurations.")


if __name__ == "__main__":
    main()

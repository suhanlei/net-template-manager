import re
from packaging.version import Version


def parse_version(v: str) -> tuple[int, int, int]:
    """Parse a semver string like '1.2.3' into (major, minor, patch)."""
    ver = Version(v)
    return ver.major, ver.minor, ver.micro


def increment_version(current: str, change_type: str) -> str:
    """Increment a semver string based on change type."""
    major, minor, patch = parse_version(current)
    if change_type == "major":
        return f"{major + 1}.0.0"
    elif change_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def validate_semver(v: str) -> bool:
    """Check if a string is a valid semver."""
    try:
        Version(v)
        return True
    except Exception:
        return False

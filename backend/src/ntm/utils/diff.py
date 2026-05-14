import difflib


def unified_diff(content_old: str, content_new: str, filename: str = "config", context_lines: int = 3) -> str:
    """Generate unified diff between two content strings."""
    lines_old = content_old.splitlines(keepends=True)
    lines_new = content_new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        lines_old,
        lines_new,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=context_lines,
    )
    return "".join(diff)

def mask_name(full_name: str) -> str:
    """Nguyen Van Anh → N. V. Anh (keep last word, abbreviate the rest)."""
    parts = str(full_name).strip().split()
    if len(parts) <= 1:
        return full_name
    masked = [p[0] + "." for p in parts[:-1]]
    masked.append(parts[-1])
    return " ".join(masked)


def mask_name_series(series):
    return series.apply(mask_name)

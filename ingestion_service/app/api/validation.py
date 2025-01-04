def validate_mac(mac: str) -> bool:
    import re
    return bool(re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", mac))

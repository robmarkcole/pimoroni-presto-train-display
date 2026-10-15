"""Normalise RDM LDBWS JSON into a compact renderer-facing model."""


def _get(mapping, *names, default=None):
    if not isinstance(mapping, dict):
        return default
    for name in names:
        if name in mapping:
            return mapping[name]
    lowered = {str(key).lower(): value for key, value in mapping.items()}
    for name in names:
        key = name.lower()
        if key in lowered:
            return lowered[key]
    return default


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _unwrap_board(payload):
    board = payload
    for _ in range(4):
        if not isinstance(board, dict):
            break
        nested = _get(
            board,
            "GetDepBoardWithDetailsResult",
            "getDepBoardWithDetailsResult",
            "GetStationBoardResult",
            "stationBoard",
            "result",
        )
        if not isinstance(nested, dict):
            break
        board = nested
    return board if isinstance(board, dict) else {}


def _service_list(board):
    services = _get(board, "trainServices", "services", "departures", default=[])
    if isinstance(services, dict):
        services = _get(services, "service", "trainService", "items", default=[])
    return [item for item in _as_list(services) if isinstance(item, dict)]


def _location_name(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return _get(value, "locationName", "name", "crs", default="") or ""
    for item in _as_list(value):
        name = _location_name(item)
        if name:
            return name
    return ""


def _calling_points(service):
    groups = _get(
        service,
        "subsequentCallingPoints",
        "callingPoints",
        "subsequentCallingPoint",
        default=[],
    )
    points = []
    for group in _as_list(groups):
        if isinstance(group, dict):
            group = _get(group, "callingPoint", "callingPoints", "items", default=group)
        for point in _as_list(group):
            if not isinstance(point, dict):
                continue
            name = _get(point, "locationName", "name", "crs", default="") or ""
            if name:
                points.append(
                    {
                        "name": name,
                        "scheduled": _get(point, "st", "scheduledTime", default="") or "",
                        "expected": _get(point, "et", "estimatedTime", default="") or "",
                    }
                )
    return points


def _normalise_status(service, scheduled):
    cancelled = bool(_get(service, "isCancelled", "cancelled", default=False))
    estimated = _get(service, "etd", "estimatedDeparture", "expectedDeparture", default="") or ""
    if str(estimated).lower() == "cancelled":
        cancelled = True
    if cancelled:
        return "Cancelled", "cancelled", ""
    if not estimated or str(estimated).lower() == "on time":
        return "On time", "on_time", scheduled
    if str(estimated).lower() == "delayed":
        return "Delayed", "delayed", ""
    if estimated == scheduled:
        return "On time", "on_time", estimated
    return "Exp %s" % estimated, "delayed", estimated


def normalise_board(payload):
    board = _unwrap_board(payload)
    services = []
    for raw in _service_list(board):
        scheduled = _get(raw, "std", "scheduledDeparture", "scheduledTime", default="") or ""
        status, status_kind, estimated = _normalise_status(raw, scheduled)
        destination = _location_name(_get(raw, "destination", "destinations", default=""))
        platform_hidden = bool(
            _get(raw, "platformIsHidden", "platformSuppressed", default=False)
            or _get(board, "platformsAreHidden", default=False)
        )
        platform = "" if platform_hidden else str(_get(raw, "platform", default="") or "")
        services.append(
            {
                "id": str(_get(raw, "serviceID", "serviceId", "id", default="") or ""),
                "scheduled": scheduled,
                "estimated": estimated,
                "destination": destination or "Destination unavailable",
                "platform": platform,
                "platform_hidden": platform_hidden,
                "operator": _get(raw, "operator", "operatorName", default="") or "",
                "cancelled": status_kind == "cancelled",
                "status": status,
                "status_kind": status_kind,
                "cancel_reason": _get(raw, "cancelReason", "cancellationReason", default="") or "",
                "delay_reason": _get(raw, "delayReason", default="") or "",
                "calling_points": _calling_points(raw),
            }
        )

    return {
        "station": _get(board, "locationName", "stationName", default="") or "",
        "crs": _get(board, "crs", "locationCrs", default="") or "",
        "generated_at": _get(board, "generatedAt", "generated_at", default="") or "",
        "services": services,
    }

from dataclasses import dataclass, field


@dataclass
class TemporalResponse:
    """A temporary response object used during request processing.
    
    This is useful for accumulating response metadata (status code, headers)
    before creating the final framework-specific response.
    """
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)


__all__ = ["TemporalResponse"]
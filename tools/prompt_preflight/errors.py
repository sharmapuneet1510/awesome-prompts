"""Exceptions shared by the Prompt Preflight modules."""


class ModelUnavailable(Exception):
    """The local model cannot give a usable answer right now.

    Raised for every model-tier failure: not configured, refused host, server down,
    timeout, HTTP error, invalid JSON, or an off-schema reply. Callers fail open.
    """

import os

_GCP_PROJECT = os.environ.get("SNOONU_GCP_PROJECT")
_client = None

def _secret_manager_client():
    global _client
    if _client is None:
        from google.cloud import secretmanager
        _client = secretmanager.SecretManagerServiceClient()
    return _client

def get_secret(name: str, default: str | None = None) -> str | None:
    """Resolve a secret by name.

    In GCP (SNOONU_GCP_PROJECT set), reads the latest version from Secret Manager —
    failures raise rather than silently falling back, since a misconfigured secret
    in production should fail loudly, not run with a wrong default.
    Otherwise reads from the environment variable of the same name.
    """
    if _GCP_PROJECT:
        path = f"projects/{_GCP_PROJECT}/secrets/{name}/versions/latest"
        response = _secret_manager_client().access_secret_version(name=path)
        return response.payload.data.decode("utf-8")
    return os.environ.get(name, default)

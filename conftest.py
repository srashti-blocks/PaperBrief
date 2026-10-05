import os
import tempfile
import pytest

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DB_PATH"] = _tmp.name
os.environ.pop("GEMINI_API_KEY", None)

@pytest.fixture(autouse=True)
def _no_rate_limit():
    from main import limiter
    limiter.enabled = False
    yield
    limiter.enabled = True

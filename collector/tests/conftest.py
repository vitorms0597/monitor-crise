import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture():
    def load(name):
        path = FIXTURES / name
        return json.loads(path.read_text()) if path.suffix == ".json" else path.read_text()
    return load

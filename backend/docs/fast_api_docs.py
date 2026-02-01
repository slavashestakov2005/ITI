"""Генерация документации как это делает FastAPI."""

import json
import os
import sys

sys.path.insert(0, os.path.abspath("../../backend"))


from main import app  # noqa: E402

openapi_data = app.openapi()
with open("openapi.json", "w") as api_file:
    json.dump(openapi_data, api_file, indent=2)

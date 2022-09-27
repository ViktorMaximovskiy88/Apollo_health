import newrelic.agent

newrelic.agent.initialize("./backend/app/newrelic.ini")

import sys
from pathlib import Path

import uvicorn

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
    from backend.common.core.config import is_local

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=is_local)

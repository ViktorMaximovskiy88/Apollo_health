import logging
import sys
from pathlib import Path

import newrelic.agent
import uvicorn

newrelic.agent.initialize(Path(__file__).parent / "newrelic.ini")

# disable uvicorn logging
logging.getLogger("uvicorn.error").propagate = False
logging.getLogger("uvicorn.access").propagate = False


if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.joinpath("../..").resolve()))
    from backend.common.core.config import is_local

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=is_local)

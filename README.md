# Apollo Source Hub

## Overview

Source Hub is an application that focuses on the management, collection, analysis and assessment of documents. Specifically/primarily PDFs from payer/insurance healthcare companies.

Apollo is the name of the project to modernize the existing infrastructure at MMIT that fulfills this purpose.

## Technology

### Backend

- Python
- MongoDB
- FastAPI
- Playwright

### Frontend

- React
- Redux Toolkit
- Ant Design

## Services

### App (backend/app)

Responsible for handling requests from the frontend, performing CRUD, initiating work for the scraper.

### Scrape Worker (backend/scrapeworker)

Responsible for downloading documents and assigning an initial document type, effective date etc.

### Parse Worker (backend/parseworker)

Responsible for extracting content for structured documents.

### Scheduler (backend/scheduler)

Responsible for running jobs on a schedule, scaling infrastructure to meet demand, and failing/rescheduling abandoned tasks.

## Development

Hi developer. See the [development](/docs/DEVELOPMENT.md) readme.

## FAQs

**Q:** Upon starting the frontend project my browser URL just says `https://undefined/authorize?redirect_uri=xxxx`. What gives?

**A:** Currently the frontend app queries the backend for its env config. If the backend isnt running you will get redirected to the above.

> **FIX** Ensure your backend is running on the expected host:port (usually `localhost:8000`) and navigate to the frontend at `localhost:3000`. If the backend is running and you still get redirected, refer to the "Common Issues" section of `DEVELOPMENT.md` for instructions on updating your `etc/hosts` file.

**Q:** I run `poetry install` on my Mac M1 and get errors. Whats the deal?

**A:** Apple. Seriously though, you will need to set some env vars for builds.

> **FIX** Add these flags to your current shell or current command. Shown here we will set them in the shell then run poetry install in the same shell.

```bash
# AFAIK this is m1 only (we really shouldnt need the exports)
PIP_CONSTRAINT="build-constraints.txt" CFLAGS="-mavx -DWARN(a)=(a) -I /opt/homebrew/opt/protobuf/include" LDFLAGS="-L/opt/homebrew/opt/protobuf/lib" poetry install
```

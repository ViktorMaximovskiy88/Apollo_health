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

These instructions are based on Ubuntu Linux. They should be portable to Windows (via WSL2) and Mac.

### Base Install

```bash
# Install base packages
apt-get update
apt-get install -y locales make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl zip llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git \
    neovim htop lsof sudo software-properties-common poppler-utils gcc \
    gfortran libblas-dev liblapack-dev

# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Install PyEnv and Python
curl -fsSL https://pyenv.run | bash
echo "export PATH=\"\$HOME/.pyenv/bin:\$HOME/.pyenv/shims:\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc
export PATH="$HOME/.pyenv/bin:$HOME/.pyenv/shims:$HOME/.local/bin:$PATH"
pyenv install 3.10.3
pyenv global 3.10.3

# Install NVM and Node/Yarn
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
source ~/.nvm/nvm.sh
nvm install node 18
npm install yarn -g

# Install Poetry
curl -sSL https://install.python-poetry.org | python3

# Create and Clone Repo
mkdir -p workspace
cd workspace
git clone git@ssh.dev.azure.com:v3/mmitdev/Apollo/Apollo
cd Apollo

# Create Virtual Env
python -m venv .venv
source .venv/bin/activate

# Build Frontend
(
    cd frontend && \
    yarn install && \
    yarn build
)

# Build Backend
(
    cd backend && \
    poetry install && \
    playwright install chromium && \
    playwright install-deps
)
```

### Starting Services

Each service should run in it's own terminal. Use your editors built in terminal management for pane splitting or a tool like tmux.

```bash
# Before starting, make sure:
# - You are in the Apollo folder
# - Docker Desktop is open

# Start Local Mongo/Minio/Redis
sudo docker compose -f ./Docker/docker-compose-dev.yaml up
```

```bash
# Webserver
python backend/app/main.py
```

```bash
# Scrape Worker
python backend/scrapeworker/main.py
```

```bash
# Parse Worker
python backend/parseworker/main.py
```

```bash
# Parse Worker
python backend/scheduler/main.py
```

```bash
# Frontend

cd frontend

# start the app
yarn start
```

If everything has gone well, go to http://localhost:3000/login and you should see the Source Hub login screen.

The first time you start the app, if no admin account exists, one will be created with a random password. That password will be displayed in the Python Terminal session, so copy the credentials and attempt a login. You might see 401 error at this point.

Login by going to http://localhost:3000/login page with automatically generated user. This should address 401 error.
If you're in and no errors, create a new user with your own email and password on the users page, then login by going to http://localhost:3000/login and using your new credentials.

If that succeeds, try creating a site. I recommend Molina HealthCare OH Drug at https://www.molinahealthcare.com/providers/oh/duals/drug/formulary.aspx. Once created, go into it and click the 'Run Collection' button and hope for the best, watching the logs for activity/errors.

### Windows Install

# Installers

- Install node using Installer from https://nodejs.org/en/download/. This should install npm
- Install Docker Desktop from https://docs.docker.com/desktop/windows/install/. The same Install will be used in WSL environment
- Install 10.3.4 Python for Windows from https://www.python.org/downloads/. If you have any other older version installed, make sure that 10.3.4 becomes the default version. Check version by running 'python --version' command. This might require changing PATH environment variable
- Install Visual Studio Code
- Install Git

```bash
# Install Yarn
npm install yarn -g

# Install Poetry
pip install poetry

# Create and Clone Repo
## Open Command Prompt in directory where you want to install the project.
git clone https://mmitdev@dev.azure.com/mmitdev/Apollo/_git/Apollo
cd Apollo

# Build Frontend
## Last step will generate 'build' directory inside 'frontend' directory, which is required to run server code
cd frontend
yarn install
yarn build
yarn run build

# Create Virtual Env and activate it
## Before you do this step, check again that python version is 3.10.4.  Make sure that you are in 'Apollo' directory
cd ..
python -m venv .venv
call .venv\Scripts\activate.bat


# Build Backend
cd backend
poetry install && playwright install chromium && playwright install-deps
```

### Starting Services

Each service should run in it's own terminal. Use your editors built in terminal management for pane splitting or a tool like tmux.

```bash
# Before starting, make sure:
# - You are in the Apollo folder
# - Docker Desktop is open

# Start Local Mongo/Minio/Redis
docker compose -f ./Docker/docker-compose-dev.yaml up
```

```bash
# Webserver
python backend/app/main.py
```

```bash
# Scrape Worker
python backend/scrapeworker/main.py
```

```bash
# Parse Worker
python backend/parseworker/main.py
```

```bash
# Parse Worker
python backend/scheduler/main.py
```

```bash
# Frontend
cd frontend
yarn start
```

# WSL2

In case we run into problems running system on Windows, we checked an option running using WSL2
Follow instructions in https://code.visualstudio.com/docs/remote/wsl-tutorial up to 'Python development' section
Follow https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers to run Docker containers. You will be running all docker containers from Windows terminal
Then follow above WSL2 instructions to install all required components. You might need to add 'sudo' to some commands.  
Note: I was able to clone git repository only using HTTPS command from Windows instructions. I was not able to start VS Code from WSL terminal.
Instead I started VS Code on Windows, used 'Remote WSL' extension to switch to Ubuntu and then selected Ubuntu directory where project was installed
Confirm that python version is 3.10.4 before you generate virtual environment
At some point I had a problem with PATH. It was fixed by manually updating .bashrc file. PATH definition at the end of the file had single instead of double quotes. We believe it was caused by some incorrect Export PATH command that is no longer part of this file

# macOS (intel?)

# PYCLD3 Deps

```bash
# linux might not need the env vars for building...
brew install protobuf
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
export CFLAGS='-I /opt/homebrew/opt/protobuf/include'
export LDFLAGS=-L/opt/homebrew/opt/protobuf/lib
```

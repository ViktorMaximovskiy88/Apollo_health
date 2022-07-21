# Development Setup

Assumptions will be made regarding package managers and setup. Conform.
Supporting:

- Debian based Linux distros
- MacOS M1 and Intel

## Pre-reqs

Before we get to app setup and running. You will need these:

- os base packages (varies by OS)
- Docker
- pyenv
- python
- poetry
- nvm
- node
- yarn

### Linux setup

```bash
# Install base packages
apt-get update
apt-get install -y locales make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl zip llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git \
    neovim htop lsof sudo software-properties-common poppler-utils gcc \
    gfortran libblas-dev liblapack-dev \
    g++ protobuf-compiler libprotobuf-dev libmagic1

# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Install PyEnv and Python
curl -fsSL https://pyenv.run | bash
echo "export PATH=\"\$HOME/.pyenv/bin:\$HOME/.pyenv/shims:\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc
export PATH="$HOME/.pyenv/bin:$HOME/.pyenv/shims:$HOME/.local/bin:$PATH"
pyenv install 3.10.3
pyenv global 3.10.3

# Install Poetry
curl -sSL https://install.python-poetry.org | python3

# Install NVM and Node/Yarn
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
source ~/.nvm/nvm.sh
nvm install node 18
npm install yarn -g
```

### MacOS setup

```sh

# Install base packages

xcode-select --install

# brew is apt more or less
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install gnupg coreutils awscli protobuf libmagic

# Install Docker
brew install docker
brew install --cask docker
curl -fsSL https://get.docker.com | sudo sh

# Install PyEnv and Python
brew install pyenv
source ~/.zshrc
pyenv install 3.10.3
pyenv global 3.10.3

# Install Poetry
curl -sSL https://install.python-poetry.org | python3

# Install NVM and Node/Yarn
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
source ~/.zshrc
nvm install node 18
npm install yarn -g
```

## Application Setup

### Create and Clone Repo

```bash
mkdir -p workspace
cd workspace
git clone git@ssh.dev.azure.com:v3/mmitdev/Apollo/Apollo
cd Apollo
```

### Create Virtual Env

```bash
python -m venv .venv
source .venv/bin/activate
```

### Initial Setup Frontend

```bash
cd frontend
# yarn install node deps
yarn install
yarn build
```

### Initial Setup Backend

```bash
source .venv/bin/activate

export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1

# poetry install python deps
PIP_CONSTRAINT=build-constraints.txt CFLAGS="-mavx -DWARN(a)=(a) -I /opt/homebrew/opt/protobuf/include" \
    LDFLAGS="-L/opt/homebrew/opt/protobuf/lib" \
    poetry install

playwright install chromium
playwright install-deps

```

## Running the services

Each service should run in it's own terminal. Use your editors built in terminal management for pane splitting or a tool like tmux.

```bash
# Before starting, make sure:
# - You are in the Apollo folder
# - Docker Desktop is open

# Start Local Mongo/Minio/Redis
cd Apollo
docker compose -f ./Docker/docker-compose-dev.yaml up

# Webserver
source .venv/bin/activate
python backend/app/main.py

# Scrape Worker
source .venv/bin/activate
python backend/scrapeworker/main.py

# Parse Worker
source .venv/bin/activate
python backend/parseworker/main.py

# Parse Worker
source .venv/bin/activate
python backend/scheduler/main.py

# Frontend
cd frontend
yarn start
```

## Now what?

If everything has gone well, go to http://localhost:3000 and you should be redirected to our Auth0 SSO login page. Upon login you should see the Sourcehub app.

If that succeeds, try creating a site. I recommend Molina HealthCare OH Drug at https://www.molinahealthcare.com/providers/oh/duals/drug/formulary.aspx. Once created, go into it and click the 'Run Collection' button and hope for the best, watching the logs for activity/errors.

## Testing

### Frontend Tests

```bash
cd frontend
yarn test
```

### Backend Tests

```bash
# In virtual env
python -m pytest
```

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

# Webserver
python backend/app/main.py

# Scrape Worker
python backend/scrapeworker/main.py

# Parse Worker
python backend/parseworker/main.py

# Parse Worker
python backend/scheduler/main.py

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

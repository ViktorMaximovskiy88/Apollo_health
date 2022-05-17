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
echo "export PATH='\$HOME/.pyenv/bin:\$HOME/.pyenv/shims:\$HOME/.local/bin:\$PATH'" >> ~/.bashrc
export PATH="$HOME/.pyenv/bin:$HOME/.pyenv/shims:$PATH"
pyenv install 3.10.3
pyenv global 3.10.3

# Install NVM and Node/Yarn
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
source ~/.nvm/nvm.sh
nvm install node 18
npm install yarn

# Install Poetry
curl -sSL https://install.python-poetry.org | python3

# Create and Clone Repo
mkdir -p workspace
cd workspace
git clone git@ssh.dev.azure.com:v3/mmitdev/Apollo/Apollo
cd Apollo

# Create Virtual Env
python -m venv venv
. venv/bin/activate

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
# Frontend
cd frontend
yarn start
```
If everything has gone well, http://localhost:3000 should show up with the Source Hub login screen.

The first time you start the app, if no admin account exists, one will be created with a random password. That password will be displayed in the logs, so copy it the credentials and attempt a login.

If you're in, create a new user with your own email and password on the users page, then login by going to http://localhost:3000/login and using your new credentials.

If that succeeds, try creating a site. I recommend Molina HealthCare OH Drug at https://www.molinahealthcare.com/providers/oh/duals/drug/formulary.aspx. Once created, go into it and click the 'Run Collection' button and hope for the best, watching the logs for activity/errors.

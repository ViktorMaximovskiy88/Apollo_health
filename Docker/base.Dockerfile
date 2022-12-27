FROM ubuntu:20.04

RUN apt-get update && apt-get install -y locales && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG=en_US.utf8 DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git \
    neovim htop lsof sudo software-properties-common poppler-utils \
    gfortran libblas-dev liblapack-dev \
    g++ protobuf-compiler libprotobuf-dev libmagic1 \
    libmagickwand-dev antiword

RUN sed -i 's/rights="none" pattern="PDF"/rights="read | write" pattern="PDF"/g' /etc/ImageMagick-6/policy.xml

ARG UNAME=user
ARG HOME_DIR=/home/${UNAME}/

RUN useradd -m -s /bin/bash ${UNAME} && \
    echo "ALL ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    echo "${UNAME}:${UNAME}" | chpasswd && \
    adduser ${UNAME} sudo

USER ${UNAME}

RUN curl https://pyenv.run | bash && \
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init --path)"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc

ENV PATH="${HOME_DIR}/.pyenv/bin:${HOME_DIR}/.pyenv/shims:${HOME_DIR}/.local/bin:$PATH"

RUN pyenv install 3.10.3 && pyenv global 3.10.3

RUN curl -sSL https://install.python-poetry.org | python3 -

CMD ["/bin/bash"]

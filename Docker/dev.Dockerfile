FROM sourcehub-base:latest

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
RUN bash -lc "source ~/.nvm/nvm.sh && nvm install node 18 && npm install -g yarn"

RUN sudo apt-get install -y ripgrep fzf htop jq httpie fd-find pv moreutils tmux
RUN echo "set-option -g prefix C-a\nunbind C-b\nbind C-a send-prefix\nbind-key s split-window -hn\nbind-key v split-window -v\nbind h select-pane -L\nbind j select-pane -D\nbind k select-pane -U\nbind l select-pane -R" > ~/.tmux.conf

CMD ["/bin/bash"]

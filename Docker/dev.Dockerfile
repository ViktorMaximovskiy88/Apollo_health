FROM sourcehub-base:latest

RUN sudo apt-get install -y ripgrep fzf htop mosh jq httpie bat exa duf fd-find pv moreutils

CMD ["/bin/bash"]
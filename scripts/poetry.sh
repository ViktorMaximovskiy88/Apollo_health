#!/usr/bin/env bash


CMD=${1:?please specify install or update }
PIP_CONSTRAINT="build-constraints.txt" CFLAGS="-mavx -DWARN(a)=(a) -I /opt/homebrew/opt/protobuf/include" LDFLAGS="-L/opt/homebrew/opt/protobuf/lib" poetry $CMD
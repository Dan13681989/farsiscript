#!/bin/bash
if [ "$1" = "repl" ]; then
    python3 -m farsiscript.main repl
elif [ "$1" = "fmt" ]; then
    python3 -m farsiscript.main fmt "$@"
elif [ "$1" = "debug" ]; then
    python3 -m farsiscript.main debug "$@"
elif [ "$1" = "install" ]; then
    python3 -m farsiscript.main install "$@"
else
    python3 -m farsiscript.compiler "$@"
fi

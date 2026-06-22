#!/bin/bash
case "$1" in
    run)      python3 -m farsiscript.main run "${@:2}" ;;
    compile)  python3 -m farsiscript.compiler "${@:2}" ;;
    repl)     python3 -m farsiscript.main repl ;;
    fmt)      python3 -m farsiscript.main fmt "${@:2}" ;;
    debug)    python3 -m farsiscript.main debug "${@:2}" ;;
    install)  python3 -m farsiscript.main install "${@:2}" ;;
    check)    python3 -m farsiscript.main check "${@:2}" ;;
    turtle)   python3 -m farsiscript.turtle_cli "${@:2}" ;;
    database) python3 -m farsiscript.database_cli "${@:2}" ;;
    regex)    python3 -m farsiscript.main run lib/regex.fs "${@:2}" ;;
    test)     python3 -m farsiscript.main run "${@:2}" ;;
    gui)      python3 -m farsiscript.main run "${@:2}" ;;
    *)        echo "Unknown command: $1" ;;
esac

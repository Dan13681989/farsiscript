import sys, os, subprocess, json, urllib.request

LIB_DIR = os.path.expanduser("~/.farsiscript/lib")
REGISTRY_URL = "https://raw.githubusercontent.com/Dan13681989/farsiscript/main/registry/registry.json"

def load_registry():
    with urllib.request.urlopen(REGISTRY_URL) as r:
        return json.loads(r.read())

def install(pkg_name):
    os.makedirs(LIB_DIR, exist_ok=True)
    registry = load_registry()
    info = registry["packages"].get(pkg_name)
    if not info:
        print(f"Package '{pkg_name}' not found.")
        return
    target_dir = os.path.join(LIB_DIR, pkg_name)
    if os.path.exists(target_dir):
        print(f"Package '{pkg_name}' already installed.")
        return
    subprocess.run(["git", "clone", info["repo"], target_dir])
    print(f"Package '{pkg_name}' installed.")

def list_packages():
    registry = load_registry()
    for name, info in registry["packages"].items():
        print(f"{name} ({info['version']}) - {info['repo']}")

def main():
    if len(sys.argv) < 2:
        print("Usage: fs install <command>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "install":
        if len(sys.argv) < 3:
            print("Usage: fs install install <package>")
        else:
            install(sys.argv[2])
    elif cmd == "list":
        list_packages()
    else:
        print(f"Unknown command: {cmd}")

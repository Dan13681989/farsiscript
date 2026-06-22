#!/usr/bin/env python3
"""Simple package manager for FarsiScript libraries."""
import sys
import os
import subprocess

LIB_DIR = os.path.expanduser("~/.farsiscript/lib")

def install(url):
    os.makedirs(LIB_DIR, exist_ok=True)
    repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
    target = os.path.join(LIB_DIR, repo_name)
    if os.path.exists(target):
        print(f"Package '{repo_name}' already installed.")
        return
    subprocess.run(["git", "clone", url, target])
    print(f"Package '{repo_name}' installed to {target}")

def list_packages():
    if not os.path.isdir(LIB_DIR):
        print("No packages installed.")
        return
    for name in os.listdir(LIB_DIR):
        print(name)

def main():
    if len(sys.argv) < 2:
        print("Usage: fs install <url>")
        sys.exit(1)
    command = sys.argv[1]
    if command == 'install':
        if len(sys.argv) < 3:
            print("Usage: fs install <url>")
        else:
            install(sys.argv[2])
    elif command == 'list':
        list_packages()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()

import sys, json, re

if len(sys.argv) < 2:
    sys.exit(1)
cmd = sys.argv[1]
args = sys.argv[2:]

try:
    if cmd == "match":
        pattern, text = args[0], args[1]
        m = re.search(pattern, text)
        print(json.dumps(m.group() if m else None))
    elif cmd == "findall":
        pattern, text = args[0], args[1]
        matches = re.findall(pattern, text)
        print(json.dumps(matches))
    elif cmd == "replace":
        pattern, repl, text = args[0], args[1], args[2]
        result = re.sub(pattern, repl, text)
        print(result)
    elif cmd == "split":
        pattern, text = args[0], args[1]
        parts = re.split(pattern, text)
        print(json.dumps(parts))
except Exception as e:
    print(f"Error: {e}")

import sys, turtle

if len(sys.argv) < 2:
    print("Usage: turtle_helper.py <command_file>")
    sys.exit(1)

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            exec(line)
        except Exception as e:
            print(f"Error: {e}")

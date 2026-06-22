import sys, sqlite3, json

if len(sys.argv) < 2:
    print("Usage: sqlite_helper.py <command_file>")
    sys.exit(1)

DB_FILE = "__farsidb__.sqlite"

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""
        try:
            if cmd == "open":
                DB_FILE = arg
                conn = sqlite3.connect(DB_FILE)
                conn.close()
            elif cmd == "exec":
                conn = sqlite3.connect(DB_FILE)
                statements = arg.split(';')
                for stmt in statements:
                    stmt = stmt.strip()
                    if not stmt:
                        continue
                    cur = conn.cursor()
                    cur.execute(stmt)
                    if stmt.upper().lstrip().startswith("SELECT"):
                        rows = cur.fetchall()
                        print(json.dumps(rows, ensure_ascii=False))
                    else:
                        conn.commit()
                conn.close()
            elif cmd == "close":
                pass
        except Exception as e:
            print(f"Error: {e}")

import sys, tkinter as tk

if len(sys.argv) < 2:
    sys.exit(1)
cmd = sys.argv[1]
args = sys.argv[2:]

if cmd == "window":
    win = tk.Tk()
    win.title(args[0] if args else "FarsiScript")
    win.geometry("400x300")
    win.mainloop()
elif cmd == "label":
    root = tk.Tk()
    root.title("FarsiScript")
    lbl = tk.Label(root, text=args[0] if args else "Hello")
    lbl.pack()
    root.mainloop()
elif cmd == "button":
    root = tk.Tk()
    root.title("FarsiScript")
    btn = tk.Button(root, text=args[0] if args else "Click")
    btn.pack()
    root.mainloop()

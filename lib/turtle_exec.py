import sys, turtle

if len(sys.argv) < 2:
    sys.exit(1)

cmd = sys.argv[1]
arg = sys.argv[2] if len(sys.argv) > 2 else None

try:
    if cmd == 'forward':
        turtle.forward(float(arg))
    elif cmd == 'right':
        turtle.right(float(arg))
    elif cmd == 'left':
        turtle.left(float(arg))
    elif cmd == 'penup':
        turtle.penup()
    elif cmd == 'pendown':
        turtle.pendown()
    elif cmd == 'done':
        turtle.done()
except Exception as e:
    print(f"Turtle error: {e}")

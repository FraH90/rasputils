import debugpy
from main import *

# Allow other computers to attach to debugpy at this IP address and port.
debugpy.listen(("0.0.0.0", 5678))

# Pause the program until a remote debugger is attached
print("Waiting for debugger attach")
debugpy.wait_for_client()
print("Debugger attached")

# The rest of your program continues here
main()
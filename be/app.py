import sys
import os
this_path = os.path.dirname(__file__)
root_path = os.path.dirname(this_path)
sys.path.append(root_path)
from be import serve

if __name__ == "__main__":
    serve.be_run()

#!/usr/bin/env python
import os
import logging

os.path.basename(frame.f_code.co_filename)

def tracefunc(frame, event, arg):

      if event == "call":
          indent[0] += 2
          print("-" * indent[0] + "> call function", frame.f_code.co_name)
      elif event == "return":
          print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
          indent[0] -= 2
      return tracefunc

# import sys
# sys.setprofile(tracefunc)

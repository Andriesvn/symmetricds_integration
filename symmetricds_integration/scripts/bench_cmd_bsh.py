#!/usr/bin/env python3
import sys
import subprocess
import os

args = ["bench"]
i = 1
while i < len(sys.argv):
  args.append(sys.argv[i])
  i += 1

environ = os.environ.copy(); environ['PATH'] += os.pathsep + os.pathsep.join(['/home/frappe/.local/bin'])
wd = '/workspace/development/frappe-bench/'
list_files = subprocess.run(args, env=environ, cwd=wd)

print("The exit code was: %d" % list_files.returncode)
import os
import subprocess

def exec_jasshelper(path, commonj_path, blizzardj_path, output_path, entry_script=False, script_only=False, optimize=True, debug=False):
    """Execute the JassHelper program with options."""

    path = os.path.abspath(path)
    commonj_path = os.path.abspath(commonj_path)
    blizzardj_path = os.path.abspath(blizzardj_path)
    output_path = os.path.abspath(output_path)

    cmd = [path]

    if debug:
      # Note: --debug automatically sets --nooptimize
      cmd.append("--debug")
    elif not optimize:
      cmd.append("--nooptimize")

    if script_only:
      cmd.append("--scriptonly")

    cmd.extend([commonj_path, blizzardj_path])

    if entry_script:
      cmd.append(os.path.abspath(entry_script))

    cmd.append(output_path)

    print("Calling JassHelper...")
    print("args: " + " ".join(str(arg) for arg in cmd))

    proc = subprocess.Popen(cmd, cwd=os.path.dirname(output_path))
    proc.communicate()

    return proc.returncode == 0

def makedirs_ifnotexists(directory):
  try:
    os.makedirs(directory)
  except FileExistsError:
    pass

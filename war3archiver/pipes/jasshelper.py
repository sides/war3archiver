import os
import war3archiver.utils as utils

from ..liquid import Liquid

class JassHelperPipe():
  def __init__(self, options):
    pass

  def transform(self, build, liquids):
    jassliquids = []

    for liquid in liquids:
      entry_path = os.path.join(build['etcdir'], 'temp%s' % liquid.filename)
      out_path = os.path.join(build['etcdir'], 'temp%s_out' % liquid.filename)

      # Begin by writing the liquid's contents to disk for JassHelper
      with open(entry_path, 'ab') as entry_file, liquid.open() as liquid_stream:
        for line in liquid_stream:
          entry_file.write(line)

      # Run JassHelper on the result
      success = utils.exec_jasshelper(
        build['patch']['jasshelper_path'],
        build['patch']['commonj'].source,
        build['patch']['blizzardj'].source,
        output_path=out_path,
        entry_script=entry_path,
        script_only=True)

      if not success:
        continue

      jassliquids.append(Liquid('war3map.j', lambda: open(out_path, 'rb')))

    return jassliquids

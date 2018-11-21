import os
import war3archiver.utils as utils

from ..liquid import Liquid
from ..transform import PipeTransformer

class JassHelperPipe(PipeTransformer):
  def __init__(self, options):
    pass

  def gate(self, build, liquid):
    entry_path = os.path.join(build['etcdir'], 'temp%s' % liquid.name)
    out_path = os.path.join(build['etcdir'], 'temp_out%s' % liquid.name)

    # Begin by writing the liquid's contents to disk for JassHelper
    liquid.write_to(entry_path)

    # Run JassHelper on the result
    success = utils.exec_jasshelper(
      build['patch']['jasshelper_path'],
      build['patch']['commonj'].source,
      build['patch']['blizzardj'].source,
      output_path=out_path,
      entry_script=entry_path,
      script_only=True)

    if not success:
      return None

    return Liquid('war3map.j', lambda: open(out_path, 'rb'))

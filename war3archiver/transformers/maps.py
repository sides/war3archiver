import os

from war3structs.storage import MPQ
from .common import PipeTransformer
from ..liquid import Liquid

class MapExtractorPipe(PipeTransformer):
  def gate(self, build, liquid):
    map_liquids = []
    map_path = os.path.join(build['etcdir'], 'temp%s' % liquid.name)

    # Begin by writing the liquid's contents to disk
    liquid.write_to(map_path)

    # Create folder to extract map files to
    map_dir = os.path.join(build['etcdir'], 'temp%s' % liquid.stem)
    os.makedirs(map_dir)

    # Open the result as an MPQ and extract files
    map_mpq = MPQ(map_path)

    for found_file in map_mpq.find('*'):
      try:
        out_path = os.path.join(map_dir, found_file.filename)
        found_file.extract(out_path)
        map_liquids.append(Liquid(out_path))
      except Exception:
        pass

    map_mpq.close()

    return map_liquids

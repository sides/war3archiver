import os
import war3archiver.utils as utils

from ..liquid import Liquid
from ..blizzard import MPQ

class MapExtractorPipe():
  def __init__(self, options):
    pass

  def transform(self, build, liquids):
    map_liquids = []

    for liquid in liquids:
      map_path = os.path.join(build['etcdir'], 'temp%s' % liquid.filename)

      # Begin by writing the liquid's contents to disk
      with open(map_path, 'a+b') as entry_file, liquid.open() as liquid_stream:
        for line in liquid_stream:
          entry_file.write(line)

      # Create folder to extract map files to
      map_dir = os.path.join(build['etcdir'], 'temp%s' % liquid.filename_without_ext)
      utils.makedirs_ifnotexists(map_dir)

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

import os

from .common import SourceTransformer, SinkTransformer
from ..liquid import Liquid
from ..mixer import Mixer

class FileIOSource(SourceTransformer):
  """FileIOSource class

  Creates a liquid from a file on disk.
  """

  def open(self, build):
    return Liquid(self.options.get('entry'))

class MergeIOSink(SinkTransformer):
  """MergeIOSink class

  Writes liquids to a target directory on disk, merging destination files
  with existing ones if they exist in a Warcraft III aware manner.
  """

  def __init__(self, options):
    super().__init__(options)
    self.mixer = Mixer()

  def drain(self, build, liquid):
    with open(os.path.join(self.options.get('output'), liquid.name), 'w+b') as output_file, liquid.open() as liquid_stream:
      output_file.write(liquid_stream.read())

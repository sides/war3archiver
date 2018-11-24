import os

from .common import SourceTransformer, SinkTransformer
from ..liquid import Liquid

class FileIOSource(SourceTransformer):
  """FileIOSource class

  Creates a liquid from a file on disk.
  """

  def open(self, build):
    return Liquid(self.options.get('entry'))

class MergeSink(SinkTransformer):
  """MergeSink class

  Writes liquids to a target directory on disk, merging destination files
  with existing ones if they exist in a Warcraft III aware manner.
  """

  def drain(self, build, liquid):
    with open(os.path.join(self.options.get('output'), liquid.name), 'w+b') as output_file, liquid.open() as liquid_stream:
      output_file.write(liquid_stream.read())

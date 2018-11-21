import os

from ..liquid import Liquid
from ..transform import SourceTransformer, SinkTransformer

class FileIOSource(SourceTransformer):
  """FileIOSource class

  Creates a liquid from a file on disk.
  """

  def __init__(self, options):
    self.entry_path = options['entry']

  def open(self, build):
    return Liquid(self.entry_path)

class MergeSink(SinkTransformer):
  """MergeSink class

  Writes liquids to a target directory on disk, merging destination files
  with existing ones if they exist in a Warcraft III aware manner.
  """

  def __init__(self, options):
    self.output_path = options['output']

  def drain(self, build, liquid):
    with open(os.path.join(self.output_path, liquid.name), 'w+b') as output_file, liquid.open() as liquid_stream:
      output_file.write(liquid_stream.read())

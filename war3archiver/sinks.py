import os

"""
  Sinks

  Sinks must have a `drain` method that takes in an array of liquids.
"""

class MergeSink():
  """MergeSink class.

  Writes liquids to a target directory on disk, merging destination files
  with existing ones if they exist in a Warcraft III aware manner.
  """

  def __init__(self, options):
    self.outputdir = options['output']

  def drain(self, build, liquids):
    for liquid in liquids:
      with open(os.path.join(self.outputdir, liquid.filename), 'w+b') as output_file, liquid.open() as liquid_stream:
        output_file.write(liquid_stream.read())

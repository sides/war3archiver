from .liquid import Liquid

"""
  Sources

  Sources must have an `open` method that returns a liquid.
"""

class FileIOSource():
  """FileIOSource class.

  Creates a liquid from a file on disk.
  """

  def __init__(self, options):
    self.entry_path = options['entry']

  def open(self, build):
    return Liquid(self.entry_path)

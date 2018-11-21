import os

class Liquid():
  """Liquid class.

  A liquid is an in-memory representation of a file whose data can be
  read through a stream. It should be treated as immutable.
  """

  def __init__(self, source, reader=None):
    self._source = source
    self._filename = os.path.basename(self._source)

    splitext = os.path.splitext(self._filename)

    self._filename_without_ext = splitext[0]
    self._fileext = splitext[1].lstrip('.')

    self._reader = reader if not reader is None else lambda: open(self._source, 'rb')
    self._cached_contents = None

  @property
  def source(self):
    return self._source

  @property
  def filename(self):
    return self._filename

  @property
  def filename_without_ext(self):
    return self._filename_without_ext

  @property
  def fileext(self):
    return self._fileext

  def open(self):
    return self._reader()

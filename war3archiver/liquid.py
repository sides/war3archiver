import io

from pathlib import Path

class Liquid():
  """Liquid class

  A liquid is an in-memory representation of a file whose data can be
  read through a stream. It should be treated as immutable and a liquid
  will typically have a short lifespan.
  """

  def __init__(self, source, reader=None):
    self._source = source

    path = Path(source)
    self._name = path.name
    self._stem = path.stem
    self._suffix = path.suffix.lstrip('.')

    self._reader = reader if not reader is None else lambda: open(self._source, 'rb')
    self._cached_contents = None

  @property
  def source(self):
    """Get the liquid's source"""
    return self._source

  @property
  def name(self):
    """Get the liquid's natural name"""
    return self._name

  @property
  def stem(self):
    """Get the liquid's natural name without an extension"""
    return self._stem

  @property
  def suffix(self):
    """Get the liquid's natural extension (without the dot)"""
    return self._suffix

  @property
  def contents(self):
    """Get the liquid's entire contents

    This recklessly loads the liquid's entire contents to memory and
    stores them. Use `open` for processing big files.
    """

    if not self._cached_contents is None:
      return self._cached_contents

    with self.open() as stream:
      self._cached_contents = stream.read()

    self._reader = lambda: io.BytesIO(self._cached_contents)

    return self._cached_contents

  def write_to(self, path):
    """Write the liquid's contents to a file on disk"""
    Path(path).write_bytes(self.contents)

  def open(self):
    """Open the liquid's stream for reading"""
    return self._reader()

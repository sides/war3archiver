import os

from war3structs import MapFile, MetadataFile
from war3structs.storage import MPQ

class PackedFile():
  def __init__(self, filename, packname=None):
    filename = os.path.abspath(filename)

    if packname is None:
      packname = os.path.basename(filename)

    self.filename = filename
    self.packname = packname

class Packer():
  """Packer class

  A packer is responsible for creating a WC3 compatible map archive and
  writing it to disk. It is only concerned with local files that should
  be included as-is.
  """

  _mpq_internals = ['(listfile)', '(attributes)', '(signature)']

  def __init__(self, dest):
    self._files = []
    self._dest = dest

  def _getmetadata(self):
    metadata_file = next(
      (packed for packed in self._files if packed.packname == 'war3map.w3i'),
      None)

    if metadata_file is None:
      return False

    return MetadataFile.parse_file(metadata_file.filename)

  def add(self, file):
    if not isinstance(file, PackedFile):
      file = PackedFile(file)

    # Just silently ignore these, they could come from add_dir, and
    # it's not a big deal.
    if file.packname in Packer._mpq_internals:
      return

    self._files.append(file)

  def add_dir(self, scandir):
    for rootdir, subdirs, filenames in os.walk(scandir):
      for filename in filenames:
        fullpath = os.path.join(rootdir, filename)
        relpath = os.path.relpath(fullpath, scandir)

        self.add(PackedFile(fullpath, relpath))

  def pack(self):
    dest_dir = os.path.dirname(self._dest)
    temp_dest = os.path.join(dest_dir, '.temp_' + os.path.basename(self._dest))
    mpq_contents = ''
    metadata = self._getmetadata()

    if not metadata:
      raise Exception('No metadata file (war3map.w3i) found, can\'t pack')

    if os.path.isfile(temp_dest):
      os.remove(temp_dest)

    # Create the MPQ part
    # StormLib exceptions should be descriptive enough, just run it
    mpq = MPQ(temp_dest)
    try:
      try:
        for packed in self._files:
          # We're gonna replace files if, for some reason, duplicate
          # packnames are being added. Last one added wins.
          mpq.add(packed.filename, packed.packname, replace=True)
      finally:
        mpq.close()

      with open(temp_dest, 'rb') as mpqfile:
          mpq_contents = mpqfile.read()
    finally:
      os.remove(temp_dest)

    # Create the map
    try:
      contents = MapFile.build(dict(
        header = dict(
          file_id = b'HM3W',
          placeholder = 0,
          name = metadata.name,
          flags = metadata.flags,
          players_count = metadata.players_count
        ),
        mpq = mpq_contents
      ))
    except Exception as ex:
      raise Exception('Failed to build map archive: %s' % ex)

    with open(self._dest, 'wb') as dest_file:
      dest_file.write(contents)

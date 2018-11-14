# StormLib MPQ implementation
#
# Originally by Vjeux <vjeuxx@gmail.com> (WTFPL)
# https://github.com/vjeux/pyStormLib
#
# This is an updated version (with write) for the war3archiver
# https://github.com/warlockbrawl/war3archiver
#

import os
import glob
import sys

from ctypes import (
  byref,
  c_void_p,
  c_char_p,
  c_uint,
  c_uint64,
  create_string_buffer
)
from .stormlib import (
  Storm,
  StormOpenArchiveFlag,
  StormCreateArchiveFlag,
  StormFile
)

class MPQFile(StormFile):
  def __init__(self, mpq):
    self.mpq = mpq

  def contents(self):
    return self.mpq.read(self.filename)

  def extract(self, target=None):
    return self.mpq.extract(self.filename, target)

  def rename(self, newpath):
    return self.mpq.rename(self.filename, newpath)

  def remove(self):
    return self.mpq.remove(self.filename)

class MPQ():
  def __init__(self, filename, readonly=True):
    """Open or create the MPQ archive"""

    self.mpq_h = c_void_p()

    if os.path.exists(filename):
      flags = 0
      if readonly:
        flags |= StormOpenArchiveFlag.STREAM_FLAG_READ_ONLY

      Storm.SFileOpenArchive(filename.encode('utf-8'), 0, flags, byref(self.mpq_h))
    else:
      Storm.SFileCreateArchive(filename.encode('utf-8'), 0, 4096, byref(self.mpq_h))

  def close(self):
    """Close the MPQ archive"""

    Storm.SFileCloseArchive(self.mpq_h)
    self.mpq_h = None

  def find(self, mask='*'):
    """List all the files matching the mask"""

    found = set([])

    # Initial Find
    file = MPQFile(self)
    find_h = Storm.SFileFindFirstFile(self.mpq_h, mask.encode('utf-8'), byref(file), None)
    if not find_h:
      return

    yield file
    found.add(file)

    # Go through the results
    file = MPQFile(self)
    while Storm.TrySFileFindNextFile(find_h, byref(file)):
      if not str(file) or file in found:
        break

      yield file
      found.add(file)
      file = MPQFile(self)

    Storm.SFileFindClose(find_h)

  def has(self, path):
    """Does the MPQ have the file?"""

    # Handle argument
    if isinstance(path, StormFile):
      path = path.filename

    return Storm.TrySFileHasFile(self.mpq_h, path.encode('utf-8'))

  def read(self, path):
    """Return the file content"""

    # Handle argument
    if isinstance(path, StormFile):
      path = path.filename

    # Open the file
    file_h = c_void_p()
    Storm.SFileOpenFileEx(self.mpq_h, path.encode('utf-8'), 0, byref(file_h))

    # Get the size
    high = c_uint()
    low = Storm.SFileGetFileSize(file_h, byref(high))
    size = high.value * pow(2, 32) + low

    # Read the File
    data = create_string_buffer(size)
    read = c_uint()
    Storm.SFileReadFile(file_h, byref(data), size, byref(read), None)

    # Close and return
    Storm.SFileCloseFile(file_h)
    return data.raw

  def write(self, path, data):
    """Write data to a new file"""

    size = len(data)
    data = c_char_p(data)
    file_h = c_void_p()

    Storm.SFileCreateFile(self.mpq_h, path.encode('utf-8'), 0, size, 0, 0, byref(file_h))
    Storm.SFileWriteFile(file_h, byref(data), size, 0)
    Storm.SFileFinishFile(file_h)

  def rename(self, path, newpath):
    """Rename a file"""

    if isinstance(path, StormFile):
      path = path.filename

    Storm.SFileRenameFile(self.mpq_h, path.encode('utf-8'), newpath.encode('utf-8'))

  def remove(self, path):
    """Remove a file from the mpq"""

    if isinstance(path, StormFile):
      path = path.filename

    Storm.SFileRemoveFile(self.mpq_h, path.encode('utf-8'), 0)

  def extract(self, mpq_path, local_path=None):
    """Extract the file"""

    # Handle arguments
    if isinstance(mpq_path, StormFile):
      mpq_path = mpq_path.filename

    if local_path is None:
      local_path = mpq_path

    # Create the directories
    local_path = local_path.replace('\\', '/')
    try:
      os.makedirs(os.path.dirname(local_path))
    except Exception:
      pass

    # Extract!
    Storm.SFileExtractFile(self.mpq_h, mpq_path.encode('utf-8'), local_path.encode('utf-8'), 0)

  def add(self, local_path, mpq_path=None):
    """Add a local file to the mpq"""

    if mpq_path is None:
      mpq_path = os.path.basename(local_path)
    elif isinstance(mpq_path, StormFile):
      mpq_path = mpq_path.filename

    Storm.SFileAddFileEx(self.mpq_h, local_path.encode('utf-8'), mpq_path.encode('utf-8'), 0, 0, 0)

  def patch(self, path, prefix=''):
    """Add MPQ as patches"""

    # Handle arguments
    path_list = sorted(glob.glob(path)) if isinstance(path, str) else path

    # Add the patches
    for path in path_list:
      Storm.SFileOpenPatchArchive(self.mpq_h, path.encode('utf-8'), prefix.encode('utf-8'), 0)

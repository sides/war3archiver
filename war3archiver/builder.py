import os
import shutil

from importlib import import_module
from .liquid import Liquid
from .transformers import FileIOSource, MergeSink
from .packer import Packer

class BuildConfig():
  def __init__(self, conf):
    self.output_dir = self._extract_dir(conf, 'output', './build')
    self.pipelines = self._extract_pipelines(conf['pipelines']) if 'pipelines' in conf else []

  def _extract_dir(self, conf, attr, default=None):
    if attr in conf:
      if not isinstance(conf[attr], str):
        return conf[attr]['dir']
      else:
        return conf[attr]
    else:
      return default

  def _extract_pipelines(self, pipelinesconf):
    pipelines = []

    for pipelineconf in pipelinesconf:
      if not 'source' in pipelineconf:
        continue

      transformers = []

      if isinstance(pipelineconf['source'], str):
        transformers.append(FileIOSource({ 'entry': pipelineconf['source'] }))
      else:
        transformers.append(self._extract_transformer(pipelineconf['source']))

      if 'pipes' in pipelineconf:
        for pipeconf in pipelineconf['pipes']:
          transformers.append(self._extract_pipe(pipeconf))

      if 'sink' in pipelineconf:
        if isinstance(pipelineconf['sink'], str):
          transformers.append(MergeSink({ 'output': pipelineconf['sink'] }))
        else:
          transformers.append(self._extract_transformer(pipelineconf['sink']))
      else:
        transformers.append(MergeSink({ 'output': os.path.join(self.output_dir, 'work') }))

      pipelines.append(transformers)

    return pipelines

  def _extract_transformer(self, conf):
    if isinstance(conf, str):
      name = conf
      options = {}
    else:
      name = conf['transformer']
      options = conf['options'] if 'options' in conf else {}

    mod_parts = os.path.splitext(name)
    mod = import_module(mod_parts[0])
    transformer_class = getattr(mod, mod_parts[1].lstrip('.'))
    transformer = transformer_class(options)

    return transformer

def build(config):
  """Builds a map based on the config"""

  os.makedirs(config.output_dir, exist_ok=True)

  build = {
    'workdir': os.path.join(config.output_dir, 'work'),
    'patch': {
      'commonj': Liquid('./patch/data/common.j'),
      'blizzardj': Liquid('./patch/data/blizzard.j'),
      'jasshelper_path': './patch/bin/jasshelper.exe'
    }
  }

  os.makedirs(build['workdir'], exist_ok=True)

  for index, pipeline in enumerate(config.pipelines):
    build['etcdir'] = os.path.join(config.output_dir, 'etc%s' % index)
    os.makedirs(build['etcdir'])

    liquids = []
    for transformer in pipeline:
      liquids = transformer.transform(build, liquids)

  w3x = Packer(os.path.join(config.output_dir, 'map.w3x'))
  w3x.add_dir(build['workdir'])
  w3x.pack()

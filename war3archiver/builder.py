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

      if isinstance(pipelineconf['source'], str):
        source = FileIOSource({ 'entry': pipelineconf['source'] })
      else:
        source = FileIOSource(pipelineconf['source'])

      pipes = []
      if 'pipes' in pipelineconf:
        for pipeconf in pipelineconf['pipes']:
          pipe = self._extract_pipe(pipeconf)

          if not pipe:
            continue

          pipes.append(pipe)

      if 'sink' in pipelineconf:
        if isinstance(pipelineconf['sink'], str):
          sink = MergeSink({ 'output': pipelineconf['sink'] })
        else:
          sink = MergeSink(pipelineconf['sink'])
      else:
        sink = MergeSink({ 'output': os.path.join(self.output_dir, 'work') })

      pipelines.append({
        'source': source,
        'pipes': pipes,
        'sink': sink })

    return pipelines

  def _extract_pipe(self, pipeconf):
    if not 'name' in pipeconf:
      return False

    mod_parts = os.path.splitext(pipeconf['name'])
    mod = import_module(mod_parts[0])
    pipe_class = getattr(mod, mod_parts[1].lstrip('.'))
    pipe = pipe_class(pipeconf['options'] if pipeconf['options'] else {})

    return pipe

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
    liquids = pipeline['source'].transform(build, [])

    build['etcdir'] = os.path.join(config.output_dir, 'etc%s' % index)
    os.makedirs(build['etcdir'])

    for pipe in pipeline['pipes']:
      liquids = pipe.transform(build, liquids)

    pipeline['sink'].transform(build, liquids)

  w3x = Packer(os.path.join(config.output_dir, 'map.w3x'))
  w3x.add_dir(build['workdir'])
  w3x.pack()

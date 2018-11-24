class Transformer():
  """Transformer class

  A transformer transforms liquids in some way. It takes in liquids, or
  doesn't, and returns either new liquids, the same liquids or no
  liquids at all. It is the base class for sources, pipes and sinks.
  """

  def __init__(self, options):
    self.options = options

  def transform(self, build, liquids):
    pass

class SourceTransformer(Transformer):
  """SourceTransformer class

  A transformer that doesn't want to take any liquids in, but instead
  returns a single one. Has an abstract `open` method for this.
  """

  def open(self, build):
    pass

  def transform(self, build, liquids):
    return [self.open(build)]

class SinkTransformer(Transformer):
  """SinkTransformer class

  A transformer that drains all incoming liquids, effectively ending a
  pipeline. Has an abstract `drain` method for this.
  """

  def drain(self, build, liquid):
    pass

  def transform(self, build, liquids):
    for liquid in liquids:
      self.drain(build, liquid)

    return []

class PipeTransformer(Transformer):
  """PipeTransformer class

  A transformer that gates incoming liquids and transforms them (or
  not) one by one. Has an abstract `gate` method for this.
  """

  def gate(self, build, liquid):
    pass

  def transform(self, build, liquids):
    transformed = []

    for liquid in liquids:
      l = self.gate(build, liquid)

      if l is None:
        continue

      if isinstance(l, list):
        transformed.extend(l)
      else:
        transformed.append(l)

    return transformed

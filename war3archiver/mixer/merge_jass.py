import re
import war3archiver.utils as utils

from war3structs.plaintext import JassParser

def merge_jass(ljass, rjass):
  """Merge JASS scripts

  Right-hand IDs will be concatenated to the left-hand script which is
  then returned. IDs that exist in both will be replaced by the right-
  hand's IDs unless specified otherwise via comment flags.
  """

  destination = JassParser.parse(ljass)
  incoming = JassParser.parse(rjass)

  comments = JassParser.parse_comments(rjass)

  # Go through each node that needs merging
  for id_ in set(destination).intersection(set(incoming)):
    inc_symbol = incoming[id_]

    if id_ in ['main', 'config']:
      # Merge main and config by default
      strategy = 'merge'
    else:
      strategy = 'rename'

    # Get a potential override from comments
    if inc_symbol.line in comments:
      match = re.match(r'^/// merge:(.+)', comments[inc_symbol.line])

      if not match is None:
        strategy = match[1]

        if strategy == 'merge':
          if id_ != 'main' and id_ != 'config':
            raise Exception('Merge strategy "merge" may only be performed on the main or config functions: "%s" given (line %s)' % (
              inc_symbol.id, inc_symbol.line))
        elif strategy == 'win' or strategy == 'lose':
          dest_symbol = destination[id_]
          if not type(dest_symbol) is type(inc_symbol):
            raise Exception('Merge strategy "%s" may only be performed on the same type of node: "%s" and "%s" differ for "%s" (line %s)' % (
              strategy, type(dest_symbol), type(inc_symbol), inc_symbol.id, inc_symbol.line))
        elif strategy != 'rename' and strategy != 'ignore':
          raise Exception('Unknown merge strategy "%s" (line %s)' % (strategy, inc_symbol.line))

    # Merge the nodes
    if strategy == 'rename':
      destination.rename(id_, id_ + '__merged_1')
      incoming.rename(id_, id_ + '__merged_2')
    elif strategy == 'win':
      destination[id_] = inc_symbol
      del incoming[id_]
    elif strategy == 'lose':
      del incoming[id_]
    elif strategy == 'merge':
      dest_symbol = destination[id_]

      suffix = 1
      for func in [dest_symbol, inc_symbol]:
        for local in func.locals:
          func.rename_local(local.id, local.id + '__merged_%s' % suffix)

        suffix += 1

      dest_symbol.locals += inc_symbol.locals
      dest_symbol.statements += inc_symbol.statements

      del incoming[id_]

  # Concat the rest
  destination.types += incoming.types
  destination.natives += incoming.natives
  destination.globals += incoming.globals
  destination.functions += incoming.functions

  # Move main and config to bottom
  if 'main' in destination:
    main = destination['main']
    destination.replace(main, None)
    destination.functions += [main]
  if 'config' in destination:
    config = destination['config']
    destination.replace(config, None)
    destination.functions += [config]

  return JassParser.build(destination)

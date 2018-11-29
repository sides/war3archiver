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
    incoming_node = incoming[id_]
    lineno = incoming_node.id.line

    if id_ in ['main', 'config']:
      # Merge main and config by default
      strategy = 'merge'
    else:
      strategy = 'rename'

    # Get a potential override from comments
    if lineno in comments:
      match = re.match(r'^/// merge:(.+)', comments[lineno])

      if not match is None:
        strategy = match[1]

        if strategy == 'merge':
          if id_ != 'main' and id_ != 'config':
            raise Exception('Merge strategy "merge" may only be performed on the main or config functions: "%s" given (line %s)' % (
              incoming_node.id.value, lineno))
        elif strategy == 'win' or strategy == 'lose':
          destination_node = destination[id_]
          if not type(destination_node) is type(incoming_node):
            raise Exception('Merge strategy "%s" may only be performed on the same type of node: "%s" and "%s" differ for "%s" (line %s)' % (
              strategy, destination_node.data, incoming_node.data, incoming_node.id.value, lineno))
        elif strategy != 'rename' and strategy != 'ignore':
          raise Exception('Unknown merge strategy "%s" (line %s)' % (strategy, lineno))

    # Merge the nodes
    if strategy == 'rename':
      destination.rename(id_, id_ + '__merged_1')
      incoming.rename(id_, id_ + '__merged_2')
    elif strategy == 'win':
      destination[id_] = incoming_node
      del incoming[id_]
    elif strategy == 'lose':
      del incoming[id_]
    elif strategy == 'merge':
      destination_node = destination[id_]

      suffix = 1
      for func in [destination_node, incoming_node]:
        for local in func.locals:
          func.rename_local(local.id.value, local.id.value + '__merged_%s' % suffix)

        suffix += 1

      destination_node.locals += incoming_node.locals
      destination_node.statements += incoming_node.statements

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

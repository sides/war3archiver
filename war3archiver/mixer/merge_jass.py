import re
import war3archiver.utils as utils

from war3structs.plaintext import JassParser

def merge_jass(ljass, rjass):
  """Merge JASS scripts

  Right-hand IDs will be concatenated to the left-hand script which is
  then returned. IDs that exist in both will be replaced by the right-
  hand's IDs unless specified otherwise via comment flags.
  """

  l_ast = JassParser.parse(ljass)
  r_ast = JassParser.parse(rjass)

  l_comments = JassParser.parse_comments(ljass)
  r_comments = JassParser.parse_comments(rjass)

  l_ids = set(l_ast)
  r_ids = set(r_ast)

  # Go through each node that needs merging
  for id_ in l_ids.intersection(r_ids):
    r_node = r_ast[id_]
    lineno = r_node.id.line

    if id_ in ['main', 'config']:
      # Merge main and config by default
      strategy = 'merge'
    else:
      strategy = 'rename'

    # Get a potential override from comments
    if lineno in r_comments:
      match = re.match(r'^/// merge:(.+)', r_comments[lineno])

      if not match is None:
        flags = utils.parse_one_liner_flags(match[1])

        if 'rename' in flags:
          strategy = 'rename'
        elif 'lose' in flags:
          strategy = 'lose'
        elif 'win' in flags:
          strategy = 'win'
        elif 'merge' in flags:
          if id_ not in ['main', 'config']:
            raise Exception('Merge strategy "merge" may only be performed on the main or config functions, "%s" given (line %s)' % (
              r_node.id.value, lineno))

          strategy = 'merge'

    # Merge the nodes
    if strategy == 'rename':
      l_ast.rename(id_, id_ + '__merged_1')
      r_ast.rename(id_, id_ + '__merged_2')
    elif strategy == 'win':
      l_ast[id_] = r_node
      del r_ast[id_]
    elif strategy == 'lose':
      del r_ast[id_]
    elif strategy == 'merge':
      l_node = l_ast[id_]

      suffix = 1
      for func in [l_node, r_node]:
        for local in func.locals:
          func.rename_local(local.id.value, local.id.value + '__merged_%s' % suffix)

        suffix += 1

      l_node.locals += r_node.locals
      l_node.statements += r_node.statements

      del r_ast[id_]

  # Concat the rest
  l_ast.types += r_ast.types
  l_ast.natives += r_ast.natives
  l_ast.globals += r_ast.globals
  l_ast.functions += r_ast.functions

  # Move main and config to bottom
  if 'main' in l_ast:
    main_ = l_ast['main']
    l_ast.replace(main_, None)
    l_ast.functions += [main_]
  if 'config' in l_ast:
    config = l_ast['config']
    l_ast.replace(config, None)
    l_ast.functions += [config]

  return JassParser.build(l_ast)

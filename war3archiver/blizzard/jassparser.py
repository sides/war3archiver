import re
import io

from importlib import import_module

class JassParser():
  _build_space_before = [
    'TAKES', 'RETURNS',
    'THEN',
    'AND', 'OR'
  ]

  _build_space_after = [
    'CONSTANT', 'NATIVE' 'KTYPE', 'TYPE', 'ARRAY',
    'FUNCTION', 'TAKES', 'RETURNS',
    'SET', 'CALL', 'LOCAL', 'EXITWHEN', 'DEBUG',
    'IF', 'ELSEIF', 'ELSE', 'RETURN',
    'AND', 'OR', 'NOT'
  ]

  def __init__(self):
    # TODO this is dumb
    self.jparser = import_module('war3structs.jass').JassParser

  def parse(self, text):
    """Get the AST of JASS code"""

    return self.jparser.parse(text)

  def parse_comments(self, text):
    """Get comments present in the text by their line numbers"""

    lineno = 1
    comments = {}

    for line in text.splitlines():
      comment_index = line.find('//')
      quote_index = line.find('"')

      if quote_index < comment_index:
        # Remove the quote in case the // is inside it
        line = re.sub(r'"(\\"|\\\\|[^"])*"', '', line)
        comment_index = line.find('//')

      if comment_index != -1:
        comments[lineno] = line[comment_index:]

      lineno += 1

    return comments

  def build(self, ast):
    """Build a JASS script from an AST"""

    stream = io.StringIO('')

    with stream:
      for token in ast.scan_values(lambda p: True):
        if token.type == 'NEWLINE':
          val = '\n'
        else:
          if token.type in JassParser._build_space_before:
            val = ' '
          else:
            val = ''
          val += token.value
          if token.type in JassParser._build_space_after:
            val += ' '

        stream.write(val)

      return stream.getvalue()

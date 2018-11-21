import argparse
import json

from .builder import BuildConfig, build

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', default='./war3archiver.config.json')

  args = parser.parse_args()

  with open(args.config, 'r') as json_file:
    config = json.load(json_file)

  build(BuildConfig(config))

if __name__ == '__main__':
  main()

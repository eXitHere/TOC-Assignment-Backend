#!/usr/bin/python

import sys

if __name__ == "__main__":
  # print('Number of arguments:', len(sys.argv), 'arguments.')
  # print('Argument List:', str(sys.argv))
  inp = sys.argv[1]

  print('{ "data": "' + inp + '"}')
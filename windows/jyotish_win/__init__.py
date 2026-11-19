"""The Windows edition of Gaurav Jyotish.

Everything that can be tested without a window lives in this package: the engine bridge and the local
storage. The window itself (main.py) is deliberately thin, because a GUI cannot be exercised in CI and
anything untested should be as small as possible.
"""

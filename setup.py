from setuptools import find_packages, setup

setup(name="zen",
      version="0.1",
      description="A compiler for zen language",
      author="Mitchell Goff",
      author_email='mitchellgoffpc@gmail.com',
      platforms=["any"],  # or more specific, e.g. "win32", "cygwin", "osx"
      license="BSD",
      packages=find_packages())

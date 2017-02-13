import sys
from setuptools import setup, find_packages
from servicebook import __version__


with open('requirements.txt') as f:
    deps = [dep for dep in f.read().split('\n') if dep.strip() != ''
            and not dep.startswith('-e')]
    install_requires = deps


setup(name='servicebook',
      version=__version__,
      packages=find_packages(),
      description="Mozilla QA Service Book",
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      servicebook = servicebook.server:main
      servicebook-import = servicebook.db:main
      """)

from setuptools import setup
import os

version = '0.1.5'

description = "A tool for collecting data from git repositories."
cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README.md')).read()
except:
    long_description = description

setup(
    name = "gitwalker",
    version = version,
    url = 'https://github.com/alexsparrow/gitwalker',
    license = 'GPL',
    description = description,
    long_description = long_description,
    author = 'Alex Sparrow',
    author_email = 'alspar@gmail.com',
    packages = ['gitwalker'],
    scripts = ["scripts/gitwalk_plot"],
    package_data = {"gitwalker":["bin/texcount.pl"]},
    install_requires = ['setuptools'],
    entry_points="""
[console_scripts]
gitwalk = gitwalker.main:main
""",
    # classifiers=[
    #     'Development Status :: 4 - Beta',
    #     'Environment :: Console',
    #     'Intended Audience :: Developers',
    #     'Intended Audience :: System Administrators',
    #     'License :: OSI Approved :: BSD License',
    #     'Operating System :: MacOS :: MacOS X',
    #     'Operating System :: POSIX',
    #     'Programming Language :: Python',
    #     'Topic :: Software Development :: Bug Tracking',
    # ],
)

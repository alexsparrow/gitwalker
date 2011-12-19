What is this?
-------------------
_gitwalker_ is a tool for collecting data from git repositories. It automates
the process of checking out each revision, running some command and logging the
output to a JSON file. Commands are specified in the form of Python classes.

What can it do?
-------------------
Currently _gitwalker_ supports two built in commands:

 * A LaTeX word count
 * du disk usage command

Its straightforward to add additional commands - see the file `tools.py`

The included script `plotter.py` uses the
[matplotlib](http://matplotlib.sourceforge.net/index.html) framework to produce
time-series graphs overlaying multiple data files.

Usage
--------------------
To word count a git-tracked LaTeX project across all commits:

    ./gitwalker.py --wordcount myfile.tex --out wordcount.json /path/to/project

This will clone the repository at `/path/to/project` to a temporary directory
before checking out each revision and running a word count on the file
myfile.tex in the repository. The results will be output to the file `wordcount.json`

*gitwalker* also supports incremental update of a previously produced log file. To add newly committed revisions,

    ./gitwalker.py --in wordcount.json --wordcount myfile.tex --out wordcount.json /path/to/project

There is an attached script to plot a number of such output files on the same
axes using matplotlib. e.g.

    ./plotter.py --plot file1.json me red --plot you.json you blue wordcount/wordcount

Will plot the files `file1.json` and `file2.json` on the same axes using the
specified labels and colours. The value will be dug out from the JSON file via
the path format at the end of the command line - in this case `wordcount/wordcount`. One could also run

`./plotter.py --plot file1.json me red --plot you.json you blue wordcount/nfigures`

to plot the number of LaTeX figures present in each commit.

Todo
--------------------
* Add git-notes option
* Shell command plugin
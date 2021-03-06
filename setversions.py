"""
Product Information Index - Set Versions

This program should be run before 'git add'. It will update modified files
with the next version number based on the number of git commits that exists
of the file.

The script does not support git branches directly. If you for example create
a branch on version 5 then you should update this script to write versions
on the form 5.x.

A second branch on version 5 should have version numberson on the form 5.0.x,
see https://formallanguage.blogspot.com/2019/05/version-numbers.html for a
more extensive explanation of my view on version numbers.

This method of version updating works well for demonstration purposes in this
setting with the Pii tracker, but is not how I typically would do it. I would
leave the version blank in Git and use a delivery script that exported the
files and updated the version in the files based on the number of Git commits
and branch. I would have a tracker.py with direct access to the files in Git
instead of the local copy.

MIT License

Copyright (c) 2020 Marcus T. Andersson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import pysed.main

__author__ = "Marcus T. Andersson"
__copyright__ = "Copyright 2020, Marcus T. Andersson"
__credits__ = ["Marcus T. Andersson"]
__license__ = "MIT"
__version__ = "5"
__maintainer__ = "Marcus T. Andersson"

version = {}
stream = os.popen("git log --name-only --pretty=format:")
commits = stream.read().split("\n")
for commit in commits:
	if commit in version.keys():
		version[commit] += 1
	else:
		version[commit] = 1

stream = os.popen("git ls-files -m")
files = stream.read().split("\n")
for file in files:
	if file in version.keys():
		next_version = version[file] + 1
	else:
		next_version = 1
	if os.path.isfile(file):
		print(file, next_version)
		with open(file) as f:
			data = f.read()
			f.close()
			if file[-3:] == ".py":
				sed = pysed.main.Pysed(["", "", "", ""], data, file, True)
				sed.pattern = '^__version__ = .*'
				sed.repl = f'__version__ = "{next_version}"'
				sed.replaceText()
			elif file[-3:] == ".js":
				sed = pysed.main.Pysed(["", "", "", ""], data, file, True)
				sed.pattern = '^ . @version       .*'
				sed.repl = f' * @version       {next_version}'
				sed.replaceText()
			elif file[-4:] == ".txt":
				sed = pysed.main.Pysed(["", "", "", ""], data, file, True)
				sed.pattern = '^Version: .*'
				sed.repl = f'Version: {next_version}'
				sed.replaceText()

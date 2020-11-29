#
# Product Information Index
#
# MIT License
#
# Copyright (c) 2020 Marcus T. Andersson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import pysed.main

__author__ = "Marcus T. Andersson"
__copyright__ = "Copyright 2020, Marcus T. Andersson"
__credits__ = ["Marcus T. Andersson"]
__license__ = "MIT"
__version__ = "2"
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

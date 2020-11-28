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

__author__ = "Marcus T. Andersson"
__copyright__ = "Copyright 2020, Marcus T. Andersson"
__credits__ = ["Marcus T. Andersson"]
__license__ = "MIT"
__version__ = "8"
__maintainer__ = "Marcus T. Andersson"

import pii
import hashlib
import datetime
import os
import uuid
import sqlite3

###
### Tracker functions

def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def trackFile(path, contenttype):
	statements = []
	c = pii.conn.cursor()
	c.execute("""select file.l from FileEcn file
					left join PathEScn1 path on (file.l = path.l)
					where path.r = ?
					limit 1""", (path, ))
	mutable = None
	for row in c:
		mutable = row[0]
	c.close()
	if not mutable:
		mutable = str(uuid.uuid4())
		statements += pii.relate([mutable, "EntityE"])
		statements += pii.relate([mutable, "IdentityES", os.path.basename(path)])		
		statements += pii.relate([mutable, "FileE"])
		statements += pii.relate([mutable, "PathES", path])
		statements += pii.relate([mutable, "MutableE"])

	sha = sha256sum(path)

	c = pii.conn.cursor()
	c.execute("""select constant.l from ConstantEcn constant
					left join ShaEScn1 sha on (constant.l = sha.l)
					left join ContentTypeEScn1 contenttype on (constant.l = contenttype.l)
					where sha.r = ?
					and contenttype.r = ?
					limit 1""", (sha, contenttype))
	constant = None
	for row in c:
		constant = row[0]
	c.close()
	if not constant:
		mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
		constant = str(uuid.uuid4())
		statements += pii.relate([constant, "EntityE"])
		statements += pii.relate([constant, "IdentityES", "{} {}".format(os.path.basename(path), mtime)])		
		statements += pii.relate([constant, "ConstantE"])
		statements += pii.relate([constant, "ShaES", sha])
		statements += pii.relate([constant, "ContentTypeES", contenttype])
		statements += pii.relate([constant, "CreationTimeES", mtime])
		statements += pii.relate([constant, "ContentEB", sqlite3.Binary(open(path, "rb").read())])

	c = pii.conn.cursor()
	c.execute("""select content.l, content.r from ContentEEcnn content 
					where content.l = ?
					and content.r = ?
					limit 1""", (mutable, constant))
	content = None
	for row in c:
		content = row[0]
	c.close()
	if not content:
		statements += pii.relate([mutable, "ContentEE", constant])

	return (statements, mutable, constant)

###
### Track project

statements = []

(stmts, mutable, constant) = trackFile("./pii.py", "text/plain; charset=UTF-8")
statements += stmts
(stmts, mutable, constant) = trackFile("./model.py", "text/plain; charset=UTF-8")
statements += stmts
(stmts, mutable, constant) = trackFile("./presentation.py", "text/plain; charset=UTF-8")
statements += stmts
(stmts, mutable, constant) = trackFile("./tracker.py", "text/plain; charset=UTF-8")
statements += stmts
(stmts, mutable, constant) = trackFile("./q_files.py", "text/plain; charset=UTF-8")
statements += stmts

pii.execute(statements)

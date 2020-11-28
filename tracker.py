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
__version__ = "9"
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

def findEntity(role, rel, value):
	entity = None
	c = pii.conn.cursor()
	c.execute(f"""select role.l from {role}cn role
					join {rel} rel on (role.l = rel.l)
					where rel.r = ?
					limit 1""", (value, ))
	for row in c:
		entity = row[0]
	c.close()
	return entity

def findFile(path):
	return findEntity("FileS", "PathEScn1", path)

def findArtifact(name):
	return findEntity("ArtifactE", "IdentityEScn1", name)

def newFile(path):
	statements = []
	mutable = str(uuid.uuid4())
	statements += pii.relate([mutable, "EntityE"])
	statements += pii.relate([mutable, "IdentityES", os.path.basename(path)])		
	statements += pii.relate([mutable, "FileE"])
	statements += pii.relate([mutable, "PathES", path])
	statements += pii.relate([mutable, "MutableE"])
	return (statements, mutable)	

def trackFile(path, contenttype, mutable=None):
	statements = []
	if not mutable:
		mutable = findFile(path)
	if not mutable:
		(stmts, mutable) = newFile(path)
		statements += stmts

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

def pythonProperty(path, property):
	with open(path) as f:
		line = f.readline()
		while line:
			if line[0:len(property)] == property:
				exec(line)
				return locals()[property]
			line = f.readline()
	return None

# trackPythonFile() differs from trackFile() as it creates a new
# entity for each new version of the file it finds. The version is
# specified with the Python variable __version__ found in the file.
# It also parses the import statements and adds dependencies
def trackPythonFile(path):
	statements = []
	vnr = pythonProperty(path, "__version__")
	moduleName = os.path.basename(path)[0:-3]
	artifact = findArtifact(moduleName)
	if not artifact:
		artifact = str(uuid.uuid4())
		statements += pii.relate([artifact, "EntityE"])
		statements += pii.relate([artifact, "IdentityES", moduleName])		
		statements += pii.relate([artifact, "ArtifactE"])

	c = pii.conn.cursor()
	c.execute("""select version.l from VersionEcn version
					join VersionNumberEScn1 vnr on (version.l = vnr.l)
					join VersionEE vrel on (version.l = vrel.r)
					where vrel.l = ?
					and vnr.r = ?
					limit 1""", (artifact, vnr))
	mutable = None
	for row in c:
		mutable = row[0]
	c.close()
	if not mutable:
		(stmts, mutable) = newFile(path)
		statements += stmts
		statements += pii.relate([mutable, "VersionE"])
		statements += pii.relate([mutable, "VersionNumberES", vnr])
		statements += pii.relate([artifact, "VersionEE", mutable])
	(stmts, mutable, constant) = trackFile(path, "text/plain; charset=UTF-8", mutable=mutable)
	statements += stmts

	return statements

###
### Track project

statements = []

statements += trackPythonFile("./pii.py")
statements += trackPythonFile("./model.py")
statements += trackPythonFile("./presentation.py")
statements += trackPythonFile("./tracker.py")
statements += trackPythonFile("./q_files.py")

pii.execute(statements)

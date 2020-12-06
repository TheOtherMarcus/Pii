"""
Product Information Index- Tracker

This file tracks the changes in the Pii product itself.

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

__author__ = "Marcus T. Andersson"
__copyright__ = "Copyright 2020, Marcus T. Andersson"
__credits__ = ["Marcus T. Andersson"]
__license__ = "MIT"
__version__ = "21"
__maintainer__ = "Marcus T. Andersson"

import pii
import hashlib
import datetime
import os
import uuid
import sqlite3

# This updates the version of changed files.
import setversions

###
### Tracker functions

def sha256sum(filename, value=False):
    h  = hashlib.sha256()
    if value:
    	h.update(filename.encode())
    else:
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
	return findEntity("FileE", "PathEScn1", path)

def findArtifact(name):
	return findEntity("ArtifactE", "IdentityEScn1", name)

def findMutable(name):
	return findEntity("MutableE", "IdentityEScn1", name)

def findVersion(artifact, vnr):
	c = pii.conn.cursor()
	c.execute("""select version.l from VersionEcn version
					join VersionEScn1 vnr on (version.l = vnr.l)
					join VersionEE vrel on (version.l = vrel.r)
					where vrel.l = ?
					and vnr.r = ?
					limit 1""", (artifact, vnr))
	version = None
	for row in c:
		version = row[0]
	c.close()
	return version

def getContent(constant):
	content = None
	c = pii.conn.cursor()
	c.execute(f"""select content.r from ContentEBcn1 content
					where content.l = ?
					limit 1""", (constant, ))
	for row in c:
		content = row[0]
	c.close()
	return content

def getCreationTime(constant):
	mtime = None
	c = pii.conn.cursor()
	c.execute(f"""select content.r from CreationTimeEScn1 content
					where content.l = ?
					limit 1""", (constant, ))
	for row in c:
		mtime = row[0]
	c.close()
	return mtime

def newMutable(label, id):
	statements = []
	mutable = str(uuid.uuid4())
	statements += pii.relate([mutable, "EntityE"])
	statements += pii.relate([mutable, "LabelES", label])
	statements += pii.relate([mutable, "IdentityES", id])
	statements += pii.relate([mutable, "MutableE"])
	return (statements, mutable)	

def newFile(path, label, id):
	statements = []
	basename = os.path.basename(path)
	(stmts, mutable) = newMutable(label, f"{id} [in file] {basename}")
	statements += stmts
	statements += pii.relate([mutable, "FileE"])
	statements += pii.relate([mutable, "PathES", path])
	return (statements, mutable)	

def newArtifact(label, id):
	statements = []
	artifact = str(uuid.uuid4())
	statements += pii.relate([artifact, "EntityE"])
	statements += pii.relate([artifact, "LabelES", label])
	statements += pii.relate([artifact, "IdentityES", id])		
	statements += pii.relate([artifact, "ArtifactE"])
	return (statements, artifact)

def newPythonArtifact(label, id):
	(statements, artifact) = newArtifact(label, id)
	statements += pii.relate([artifact, "IntegratedE"])
	statements += pii.relate([artifact, "ModuleE"])
	return (statements, artifact)

def newJavascriptArtifact(label, id):
	(statements, artifact) = newArtifact(label, id)
	return (statements, artifact)

def newSpecificationArtifact(label, id):
	(statements, artifact) = newArtifact(label, id)
	statements += pii.relate([artifact, "SpecificationE"])
	return (statements, artifact)

def newRequirementArtifact(label, id):
	(statements, artifact) = newSpecificationArtifact(label, id)
	statements += pii.relate([artifact, "RequirementE"])
	return (statements, artifact)

def role(entity, roles):
	if not entity:
		raise PiiException("role(): entity is null")
	statements = []
	if isinstance(roles, str):
		roles = [roles]
	c = pii.conn.cursor()
	c.execute("""select role.r from RoleEScnn role 
					where role.l = ?""", (entity, ))
	existing = []
	for row in c:
		existing += [row[0]]
	c.close()
	for role in roles:
		if not role in existing:
			statements += pii.relate([entity, role])
	return statements

def link(l, rel, r, card="cnn"):
	if not l:
		raise PiiException("link(): l is null")
	if not r:
		raise PiiException("link(): r is null")
	statements = []
	c = pii.conn.cursor()
	c.execute(f"""select rel.l, rel.r from {rel}{card} rel 
					where rel.l = ?
					and rel.r = ?
					limit 1""", (l, r))
	lnk = None
	for row in c:
		lnk = row[0]
	c.close()
	if not lnk:
		statements += pii.relate([l, rel, r])
	return statements

def trackFile(path, label, id, contenttype, mutable=None):
	statements = []
	if not mutable:
		mutable = findFile(path)
	if not mutable:
		(stmts, mutable) = newFile(path, label, id)
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
		statements += pii.relate([constant, "LabelES", mtime])
		basename = os.path.basename(path)
		statements += pii.relate([constant, "IdentityES", f"{id} [in file] {basename} [at] {mtime}"])		
		statements += pii.relate([constant, "ConstantE"])
		statements += pii.relate([constant, "ShaES", sha])
		statements += pii.relate([constant, "ContentTypeES", contenttype])
		statements += pii.relate([constant, "CreationTimeES", mtime])
		statements += pii.relate([constant, "ContentEB", sqlite3.Binary(open(path, "rb").read())])

	statements += link(mutable, "ContentEE", constant)

	return (statements, mutable, constant)

def trackEmbedded(value, label, id, contenttype, mtime, mutable=None):
	statements = []
	if not mutable:
		mutable = findMutable(id)
	if not mutable:
		(stmts, mutable) = newMutable(label, id)
		statements += stmts

	sha = sha256sum(value, value=True)

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
		constant = str(uuid.uuid4())
		statements += pii.relate([constant, "EntityE"])
		statements += pii.relate([constant, "LabelES", mtime])		
		statements += pii.relate([constant, "IdentityES", f"{id} [at] {mtime}"])		
		statements += pii.relate([constant, "ConstantE"])
		statements += pii.relate([constant, "ShaES", sha])
		statements += pii.relate([constant, "ContentTypeES", contenttype])
		statements += pii.relate([constant, "CreationTimeES", mtime])
		statements += pii.relate([constant, "ContentEB", sqlite3.Binary(value.encode())])
		statements += pii.relate([constant, "EmbeddedE"])

	statements += link(mutable, "ContentEE", constant)

	return (statements, mutable, constant)

# trackVersion() differs from trackFile() as it creates a new
# entity for each new version of the file it finds.
def trackVersion(path, vnr, label, id, newArtifactFn, contentType):
	statements = []
	artifact = findArtifact(id)
	if not artifact:
		(stmts, artifact) = newArtifactFn(label, id)
		statements += stmts

	mutable = findVersion(artifact, vnr)
	if not mutable:
		(stmts, mutable) = newFile(path, f"v{vnr}", f"{label} [version] {vnr}")
		statements += stmts
		statements += pii.relate([mutable, "VersionE"])
		statements += pii.relate([mutable, "VersionES", vnr])
		statements += pii.relate([artifact, "VersionEE", mutable])
	(stmts, mutable, constant) = trackFile(path, f"v{vnr}", f"{label} [version] {vnr}", contentType, mutable=mutable)
	statements += stmts

	return (statements, artifact, mutable, constant)

def trackEmbeddedVersion(value, vnr, req, title, newArtifactFn, contentType, mtime):
	statements = []
	artifact = findArtifact(f"{req}: {title}")
	if not artifact:
		(stmts, artifact) = newArtifactFn(f"{req}", f"{req}: {title}")
		statements += pii.relate([artifact, "EmbeddedE"])
		statements += stmts

	mutable = findVersion(artifact, vnr)
	if not mutable:
		(stmts, mutable) = newMutable(f"v{vnr}", f"{req}/v{vnr}: {title}")
		statements += stmts
		statements += role(mutable, ["VersionE", "EmbeddedE"])
		statements += link(mutable, "VersionES", vnr)
	statements += link(artifact, "VersionEE", mutable)
	(stmts, mutable, constant) = trackEmbedded(value, f"v{vnr}", f"{req}/v{vnr}: {title}", contentType, mtime, mutable=mutable)
	statements += stmts

	return (statements, artifact, mutable, constant)

def pythonProperty(path, property):
	with open(path) as f:
		line = f.readline()
		while line:
			if line[0:len(property)] == property:
				exec(line)
				return locals()[property]
			line = f.readline()
	return None

def pythonImports(path):
	imports = []
	with open(path) as f:
		line = f.readline()
		while line:
			if line[0:7] == "import " or line[0:5] == "from ":
				imports += [line.split(" ")[1].rstrip()]
			line = f.readline()
	return imports

def trackPythonFile(path):
	vnr = pythonProperty(path, "__version__")
	moduleName = os.path.basename(path)[0:-3] + " / python"
	(statements, artifact, mutable, constant) = trackVersion(path, vnr, moduleName, moduleName, newPythonArtifact, "text/plain; charset=UTF-8")

	imports = pythonImports(path)
	for imp in imports:
		imp = imp + " / python"
		module = findArtifact(imp)
		if not module:
			(stmts, module) = newPythonArtifact(imp, imp)
			statements += stmts

		statements += link(artifact, "ModuleEE", module)

	return statements

def javascriptProperty(path, property):
	property = " * " + property
	with open(path) as f:
		line = f.readline()
		while line:
			if line[0:len(property)] == property:
				return "".join(line.split(" ")[3:]).strip()
			line = f.readline()
	return None

def trackJavascriptFile(path):
	vnr = javascriptProperty(path, "@version")
	moduleName = os.path.basename(path)[0:-3] + " / javascript"
	(statements, artifact, mutable, constant) = trackVersion(path, vnr, moduleName, moduleName, newJavascriptArtifact, "text/plain; charset=UTF-8")
	return statements

def textProperty(path, property):
	property = property + ": "
	with open(path) as f:
		line = f.readline()
		while line:
			if line[0:len(property)] == property:
				return "".join(line.split(" ")[1:]).strip()
			line = f.readline()
	return None

def textTitle(path):
	with open(path) as f:
		line = f.readline()
		while line:
			line = line.strip()
			if len(line)> 0:
				return line
			line = f.readline()
	return path

def trackSpecification(path):
	vnr = textProperty(path, "Version")
	title = textTitle(path)
	return trackVersion(path, vnr, title, title, newSpecificationArtifact, "text/plain; charset=UTF-8")

def parseRequirement(line):
	vstart = line.find("/v")
	if line[0] == "R" and vstart > 1:
		return (line.split("/")[0], line.split(":")[0].split("v")[1], "".join(line.split(" ")[1:]))
	else:
		return (None, None, None)

def trackRequirement(container_artifact, container_mutable, container_constant, req, vnr, title, body):
	mtime = getCreationTime(container_constant)
	(statements, artifact, mutable, constant) = trackEmbeddedVersion(body, vnr, req, title, newSpecificationArtifact, "text/plain; charset=UTF-8", mtime)
	statements += link(container_artifact, "EmbeddedEE", artifact)
	statements += link(container_mutable, "EmbeddedEE", mutable)
	statements += link(container_constant, "EmbeddedEE", constant)
	return statements

def trackRequirements(container_artifact, container_mutable, container_constant):
	statements = []
	statements += role(container_artifact, "ContainerE")
	statements += role(container_mutable, "ContainerE")
	statements += role(container_constant, "ContainerE")
	content = getContent(container_constant).decode("utf-8")
	req = None
	body = ""
	for line in content.split("\n"):
		line = line.strip()
		if len(line) > 0 and not req:
			(req, vnr, title) = parseRequirement(line)
		elif req:
			if len(line) > 0:
				body += line + "\n"
			else:
				statements += trackRequirement(container_artifact, container_mutable, container_constant, req, vnr, title, body)
				req = None
				body = ""

	return statements

###
### Track Pii project

pii.execute(trackPythonFile("./pii.py"))
pii.execute(trackPythonFile("./model.py"))
pii.execute(trackPythonFile("./presentation.py"))
pii.execute(trackPythonFile("./tracker.py"))
pii.execute(trackPythonFile("./q_files.py"))
pii.execute(trackPythonFile("./q_spec.py"))
pii.execute(trackPythonFile("./setversions.py"))
pii.execute(trackJavascriptFile("./pii.js"))

piipy = findArtifact("pii / python")
piijs = findArtifact("pii / javascript")
pii.execute(link(piipy, "ModuleEE", piijs))
pii.execute(link(piijs, "ModuleEE", piipy))

(stmts, artifact, mutable, constant) = trackSpecification("./requirements.txt")
pii.execute(stmts)
pii.execute(trackRequirements(artifact, mutable, constant))

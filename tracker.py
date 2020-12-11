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
__version__ = "26"
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

def findArtifact(name):
	return findEntity("ArtifactE", "IdentityEScn1", name)

def findSpecificationVersion(id):
	c = pii.conn.cursor()
	c.execute("""select spec.l, version.l from SpecificationEcn spec
					join VersionEEc1n vrel on (spec.l = vrel.l)
					join VersionEcn version on (version.l = vrel.r)
					join IdentityEScnn id on (version.l = id.l)
					where id.r like ?
					limit 1""", (id + "%", ))
	version = None
	spec = None
	for row in c:
		spec = row[0]
		version = row[1]
	c.close()
	return (spec, version)

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

def addRoles(entity, roles):
	if not entity:
		raise PiiException("addRoles(): entity is null")
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

def weakLLink(l, rel, r, card="cnn"):
	if not l:
		raise PiiException("weakLLink(): l is null")
	if not r:
		raise PiiException("weakLLink(): r is null")
	statements = []
	c = pii.conn.cursor()
	c.execute(f"""select rel.l, rel.r from {rel}{card} rel 
					where rel.l = ?
					limit 1""", (l, ))
	lnk = None
	for row in c:
		lnk = row[0]
	c.close()
	if not lnk:
		statements += pii.relate([l, rel, r])
	return statements

def trackFile(path, label, id, contenttype, mutable=None):
	basename = os.path.basename(path)
	if not mutable:
		(statements, mutable) = findOrCreate(
			["EntityE", "MutableE", "FileE"], [],
			[("LabelES", label), ("IdentityES", f"{id} [in file] {basename}"), ("PathES", path)], [],
			[], [])
	else:
		statements = addRoles(mutable, "FileE")
		statements += link(mutable, "PathES", path)
		statements += link(mutable, "IdentityES", f"{id} [in file] {basename}")

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
		(statements, mutable) = findOrCreate(
			["EntityE", "MutableE"], [],
			[("LabelES", label), ("IdentityES", id)], [],
			[], [])
	else:
		statements = []

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

def findOrCreate(roles, extra_roles, lvalues, extra_lvalues, rvalues, extra_rvalues):
	statements = []
	data = []
	conditions = []
	query = f"select role.l from {roles[0]}cn role "
	for (i, role) in enumerate(roles[1:]):
		query += f"join {role}cn role{i} on (role{i}.l = role.l) "
	for (i, (rel, value)) in enumerate(lvalues):
		query += f"join {rel}cn1 lvalue{i} on (lvalue{i}.l = role.l) "
		conditions += [f"lvalue{i}.r = ? "]
		data += [value]
	for (i, (rel, value)) in enumerate(rvalues):
		query += f"join {rel}c1n rvalue{i} on (rvalue{i}.r = role.l) "
		conditions += [f"rvalue{i}.l = ? "]
		data += [value]
	for (i, condition) in enumerate(conditions):
		query += "where " if i == 0 else "and "
		query += condition
	query += "limit 1"
	c = pii.conn.cursor()
	c.execute(query, data)
	found = None
	for row in c:
		found = row[0]
	c.close()
	if not found:
		found = str(uuid.uuid4())
		for role in roles:
			statements += pii.relate([found, role])
		for (rel, value) in lvalues:
			statements += pii.relate([found, rel, value])
		for (rel, value) in rvalues:
			statements += pii.relate([value, rel, found])
	statements += addRoles(found, extra_roles)
	for (rel, value) in extra_lvalues:
		statements += link(found, rel, value)
	for (rel, value) in extra_rvalues:
		statements += link(value, rel, found)
	return (statements, found)

# trackVersion() differs from trackFile() as it creates a new
# entity for each new version of the file it finds.
def trackVersion(path, vnr, label, id, roles, extra_roles, contentType):
	(statements, artifact) = findOrCreate(
		["EntityE", "ArtifactE"] + roles, extra_roles,
		[("LabelES", label), ("IdentityES", id)], [],
		[], [])
	(stmts, mutable) = findOrCreate(
		["EntityE", "MutableE", "VersionE"], [],
		[("VersionES", vnr)], [],
		[("VersionEE", artifact)], [])
	statements += stmts
	(stmts, mutable, constant) = trackFile(path, f"v{vnr}", f"{label} [version] {vnr}", contentType, mutable=mutable)
	statements += stmts
	return (statements, artifact, mutable, constant)

def trackEmbeddedRequirement(value, vnr, req, title, contentType, mtime):
	(statements, artifact) = findOrCreate(
		["EntityE", "ArtifactE", "SpecificationE", "EmbeddedE"], [],
		[("LabelES", f"{req}"), ("IdentityES", f"{req}: {title}")], [],
		[], [])
	(stmts, mutable) = findOrCreate(
		["EntityE", "MutableE", "VersionE", "EmbeddedE", "SpecificationE"], [],
		[("VersionES", vnr)], [],
		[("VersionEE", artifact)], [])
	statements += stmts
	(stmts, mutable, constant) = trackEmbedded(value, f"v{vnr}", f"{req}/v{vnr}: {title}", contentType, mtime, mutable=mutable)
	statements += stmts
	return (statements, artifact, mutable, constant)

def trackGitVersions(path, label):
	statements = []
	artifact = findArtifact(label)
	stream = os.popen(f"git log --date=iso-strict {path}")
	log = stream.read().split("\n")
	vnr = 0
	lvalues = []
	parsingComment = False
	for line in log:
		if parsingComment:
			comment += line[4:] + "\n"
		if line[0:len("commit ")] == "commit ":
			vnr += 1
			lvalues = [("CommitES", line.split(" ")[1])]
		elif line[0:len("Author: ")] == "Author: ":
			lvalues += [("AuthorES", " ".join(line.split(" ")[1:]).strip())]
		elif line[0:len("Date: ")] == "Date: ":
			lvalues += [("DateET", " ".join(line.split(" ")[1:]).strip())]
		elif line == "":
			if parsingComment:
				parsingComment = False
				lvalues += [("CommentEB", comment.encode())]
				(stmts, version) = findOrCreate(
					["EntityE", "VersionE"],
					["GitVersionE"],
					[("VersionES", vnr)],
					lvalues,
					[("VersionEE", artifact)],
					[])
				statements += stmts
				statements += weakLLink(version, "LabelES", f"v{vnr}")
				statements += weakLLink(version, "IdentityES", f"{label} [git version] {vnr}")
				statements += weakLLink(version, "ContentTypeES", f"text/plain; charset=UTF-8")
			else:
				comment = ""
				parsingComment = True
	return statements

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
	moduleName = os.path.basename(path)[0:-3] + "/python"
	(statements, artifact, mutable, constant) = trackVersion(path, vnr, moduleName, moduleName, ["ModuleE", "IntegratedE"], [], "text/plain; charset=UTF-8")

	imports = pythonImports(path)
	for imp in imports:
		imp = imp + "/python"
		(stmts, module) = findOrCreate(
			["EntityE", "ModuleE", "IntegratedE", "ArtifactE"], [],
			[("LabelES", imp), ("IdentityES", imp)], [],
			[], [("ModuleEE", artifact)])
		statements += stmts

	requirements = pythonProperty(path, "__implements__")
	if requirements:
		statements += addRoles(artifact, "ImplementationE")
		statements += addRoles(mutable, "ImplementationE")
		for req in requirements:
			(spec_artifact, spec_version) = findSpecificationVersion(req)
			if spec_artifact:
				statements += link(spec_artifact, "ImplementationEE", artifact)
			if spec_version:
				statements += link(spec_version, "ImplementationEE", mutable)

	return statements

def javascriptProperty(path, property):
	property = " * " + property
	with open(path) as f:
		line = f.readline()
		while line:
			if line[0:len(property)] == property:
				return " ".join(line.split(" ")[3:]).strip()
			line = f.readline()
	return None

def trackJavascriptFile(path):
	vnr = javascriptProperty(path, "@version")
	moduleName = os.path.basename(path)[0:-3] + "/javascript"
	(statements, artifact, mutable, constant) = trackVersion(path, vnr, moduleName, moduleName, [], [], "text/plain; charset=UTF-8")

	requirements = javascriptProperty(path, "@implements").split(", ")
	if requirements:
		statements += addRoles(artifact, "ImplementationE")
		statements += addRoles(mutable, "ImplementationE")
		for req in requirements:
			(spec_artifact, spec_version) = findSpecificationVersion(req)
			if spec_artifact:
				statements += link(spec_artifact, "ImplementationEE", artifact)
			if spec_version:
				statements += link(spec_version, "ImplementationEE", mutable)

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
	return trackVersion(path, vnr, title, title, ["SpecificationE"], [], "text/plain; charset=UTF-8")

def parseRequirement(line):
	vstart = line.find("/v")
	if line[0] == "R" and vstart > 1:
		return (line.split("/")[0], line.split(":")[0].split("v")[1], "".join(line.split(" ")[1:]))
	else:
		return (None, None, None)

def trackRequirement(container_artifact, container_mutable, container_constant, req, vnr, title, body):
	mtime = getCreationTime(container_constant)
	(statements, artifact, mutable, constant) = trackEmbeddedRequirement(body, vnr, req, title, "text/plain; charset=UTF-8", mtime)
	statements += link(container_artifact, "EmbeddedEE", artifact)
	statements += link(container_mutable, "EmbeddedEE", mutable)
	statements += link(container_constant, "EmbeddedEE", constant)
	return statements

def trackRequirements(container_artifact, container_mutable, container_constant):
	statements = []
	statements += addRoles(container_artifact, "ContainerE")
	statements += addRoles(container_mutable, "ContainerE")
	statements += addRoles(container_constant, "ContainerE")
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

(stmts, artifact, mutable, constant) = trackSpecification("./requirements.txt")
pii.execute(stmts)
pii.execute(trackRequirements(artifact, mutable, constant))

pii.execute(trackPythonFile("./pii.py"))
pii.execute(trackPythonFile("./model.py"))
pii.execute(trackPythonFile("./presentation.py"))
pii.execute(trackPythonFile("./tracker.py"))
pii.execute(trackPythonFile("./q_files.py"))
pii.execute(trackPythonFile("./q_spec.py"))
pii.execute(trackPythonFile("./setversions.py"))
pii.execute(trackJavascriptFile("./pii.js"))

pii.execute(trackGitVersions("./pii.py", "pii/python"))
pii.execute(trackGitVersions("./model.py", "model/python"))
pii.execute(trackGitVersions("./presentation.py", "presentation/python"))
pii.execute(trackGitVersions("./tracker.py", "tracker/python"))
pii.execute(trackGitVersions("./q_files.py", "q_files/python"))
pii.execute(trackGitVersions("./q_spec.py", "q_spec/python"))
pii.execute(trackGitVersions("./setversions.py", "setversions/python"))
pii.execute(trackGitVersions("./pii.js", "pii/javascript"))

piipy = findArtifact("pii/python")
piijs = findArtifact("pii/javascript")
pii.execute(addRoles(piipy, ["ModuleE", "IntegratedE"]))
pii.execute(addRoles(piijs, ["ModuleE", "IntegratedE"]))
pii.execute(link(piipy, "ModuleEE", piijs))
pii.execute(link(piijs, "ModuleEE", piipy))

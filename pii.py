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

import sqlite3
import datetime
import os
import uuid
import hashlib

dbfile = 'pii.sqlite3'
newdb = False

if not os.path.isfile(dbfile):
	newdb = True

# Open database in autocommit mode by setting isolation_level to None.
conn = sqlite3.connect('pii.sqlite3', isolation_level=None)

# Set journal mode to WAL.
conn.execute('pragma journal_mode=wal')

# Mapping from designation letter to sqlite3 column type
dbtype = {"S": "TEXT", "T": "TEXT", "B": "BLOB", "I": "INTEGER", "R": "REAL", "E": "TEXT"}

def role(name):
	left_type = dbtype[name[-1:]]
	statements = []
	statements += [(f"CREATE TABLE IF NOT EXISTS {name} (l {left_type}, t TEXT, a TEXT)", ())]
	statements += [(f"CREATE VIEW IF NOT EXISTS {name}c1 AS select l, t from (select l, t, a from (select l, t, a from {name} order by t desc) group by l) where a='T'", ())]
	return statements

def relation(name):
	left_type = dbtype[name[-2:-1]]
	right_type = dbtype[name[-1:]]
	statements = []
	statements += [(f"CREATE TABLE IF NOT EXISTS {name} (l {left_type}, r {right_type}, t TEXT, a TEXT)", ())]
	statements += [(f"CREATE VIEW IF NOT EXISTS {name}cnn AS select l, r, t from (select l, r, t, a from (select l, r, t, a from {name} order by t desc) group by l, r) where a='T'", ())]
	statements += [(f"CREATE VIEW IF NOT EXISTS {name}cn1 AS select l, r, t from (select l, r, t from {name}cnn order by t desc) group by l", ())]
	statements += [(f"CREATE VIEW IF NOT EXISTS {name}c1n AS select l, r, t from (select l, r, t from {name}cnn order by t desc) group by r", ())]
	statements += [(f"CREATE VIEW IF NOT EXISTS {name}c11x AS select l, r, t from {name}c1n INTERSECT select l, r, t from {name}cn1", ())]
	statements += [(f"CREATE VIEW IF NOT EXISTS {name}c11 AS select l, r, t from {name}c11x UNION select l, r, t from (select l, r, t from {name}cn1 where r not in (select r from {name}c11x) order by t) group by r UNION select l, r, t from (select l, r, t from {name}c1n where l not in (select l from {name}c11x) order by t) group by l", ())]
	return statements

def relate(tuple_triplet, associate=True):
	statements = []
	a = "T" if associate else "F"
	now = datetime.datetime.now().isoformat()
	if len(tuple_triplet) == 1:
		schema = tuple_triplet[0].split(" -- ")
		if len(schema) == 2 or len(schema) == 3:
			statements += role(schema[0])
			statements += relation(schema[1])
			statements += [(f"INSERT INTO LeftSS (l, r, t, a) values (?, ?, ?, ?)", (schema[0], schema[1], now, a))]
			if len(schema) == 3:
				statements += role(schema[2])
				statements += [(f"INSERT INTO RightSS (l, r, t, a) values (?, ?, ?, ?)", (schema[1], schema[2], now, a))]
		elif len(schema) < 2:
			raise PiiError(f"Too few arcs ( -- ): {tuple_triplet[0]}")
		elif len(schema) > 3:
			raise PiiError(f"Too many arcs ( -- ): {tuple_triplet[0]}")
	elif len(tuple_triplet) == 2:
		l = tuple_triplet[0]
		rel = tuple_triplet[1]
		statements += [(f"INSERT INTO {rel} (l, t, a) values (?, ?, ?)", (l, now, a))]
		statements += [(f"INSERT INTO RoleES (l, r, t, a) values (?, ?, ?, ?)", (l, rel, now, a))]
	elif len(tuple_triplet) == 3:
		l = tuple_triplet[0]
		rel = tuple_triplet[1]
		r = tuple_triplet[2]
		statements += [(f"INSERT INTO {rel} (l, r, t, a) values (?, ?, ?, ?)", (l, r, now, a))]
	else:
		raise PiiError("Too many items: {tuple_triplet}")
	return statements

def execute(statements):
	for (s, v) in statements:
		print(s, "<--", v)
		conn.execute(s, v)

def close():
	conn.close()

def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def trackFile(path, mimetype):
	statements = []
	c = conn.cursor()
	c.execute("""select file.l from FileEc1 file
					left join PathEScn1 path on (file.l = path.l)
					where path.r = ?
					limit 1""", (path, ))
	mutable = None
	for row in c:
		mutable = row[0]
	c.close()
	if not mutable:
		mutable = str(uuid.uuid4())
		statements += relate([mutable, "EntityE"])
		statements += relate([mutable, "IdentityES", os.path.basename(path)])		
		statements += relate([mutable, "FileE"])
		statements += relate([mutable, "PathES", path])
		statements += relate([mutable, "MutableE"])

	sha = sha256sum(path)

	c = conn.cursor()
	c.execute("""select constant.l from ConstantEc1 constant
					left join ShaEScn1 sha on (constant.l = sha.l)
					left join MimeTypeEScn1 mimetype on (constant.l = mimetype.l)
					where sha.r = ?
					and mimetype.r = ?
					limit 1""", (sha, mimetype))
	constant = None
	for row in c:
		constant = row[0]
	c.close()
	if not constant:
		mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
		constant = str(uuid.uuid4())
		statements += relate([constant, "EntityE"])
		statements += relate([constant, "IdentityES", "{} {}".format(os.path.basename(path), mtime)])		
		statements += relate([constant, "ConstantE"])
		statements += relate([constant, "ShaES", sha])
		statements += relate([constant, "MimeTypeES", mimetype])
		statements += relate([constant, "CreationTimeES", mtime])
		statements += relate([constant, "ValueEB", sqlite3.Binary(open(path, "rb").read())])

	c = conn.cursor()
	c.execute("""select content.l, content.r from ContentEEcnn content 
					where content.l = ?
					and content.r = ?
					limit 1""", (mutable, constant))
	content = None
	for row in c:
		content = row[0]
	c.close()
	if not content:
		statements += relate([mutable, "ContentEE", constant])

	return (statements, mutable, constant)

if newdb:
	# Core schema
	execute(relation("RoleES"))
	execute(relation("LeftSS"))
	execute(relation("RightSS"))

if __name__ == '__main__':
	conn.close()

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
import json
import webbrowser
import random
import threading
import http.server
import socketserver

dbfile = 'pii.sqlite3'
newdb = False

if not os.path.isfile(dbfile):
	newdb = True

# Open database in autocommit mode by setting isolation_level to None.
conn = sqlite3.connect('pii.sqlite3', isolation_level=None)
webconn = None # Opens in webserver thread

# Set journal mode to WAL.
conn.execute('pragma journal_mode=wal')

# JSON Encoder
jenc = json.JSONEncoder()

# Mapping from designation letter to sqlite3 column type
dbtype = {"S": "TEXT", "T": "TEXT", "B": "BLOB", "I": "INTEGER", "R": "REAL", "E": "TEXT"}

###
### Basic database schema creation

def unary_rel(name):
	left_type = dbtype[name[-1:]]
	statements = []
	statements += [(f"CREATE TABLE IF NOT EXISTS {name} (l {left_type}, t TEXT, a TEXT)", ())]
	statements += [(f"CREATE VIEW IF NOT EXISTS {name}c1 AS select l, t from (select l, t, a from (select l, t, a from {name} order by t desc) group by l) where a='T'", ())]
	return statements

def binary_rel(name):
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

###
### Domain model definition

def model(relation, associate=True):
	statements = []
	a = "T" if associate else "F"
	now = datetime.datetime.now().isoformat()
	schema = relation.split(" -- ")
	if len(schema) == 2 or len(schema) == 3:
		statements += unary_rel(schema[0])
		statements += binary_rel(schema[1][:-3])
		statements += [(f"INSERT INTO LeftSS (l, r, t, a) values (?, ?, ?, ?)", (schema[0], schema[1], now, a))]
		if len(schema) == 3:
			statements += unary_rel(schema[2])
			statements += [(f"INSERT INTO RightSS (l, r, t, a) values (?, ?, ?, ?)", (schema[1], schema[2], now, a))]
	elif len(schema) < 2:
		raise PiiError(f"Too few arcs ( -- ): {relation}")
	elif len(schema) > 3:
		raise PiiError(f"Too many arcs ( -- ): {relation}")
	return statements

###
### Relate entities and values

def relate(tuple_triplet, associate=True):
	statements = []
	a = "T" if associate else "F"
	now = datetime.datetime.now().isoformat()
	if len(tuple_triplet) == 2:
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
		raise PiiError("Too few/many items: {tuple_triplet}")
	return statements

###
### Database access

def execute(statements):
	for (s, v) in statements:
		print(s, "<--", v)
		conn.execute(s, v)

def close():
	conn.close()

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

###
### Model Serialization

def value2serial(t, v, rel, l):
	serial = ""
	if t == "E":
		serial += v
	if t == "S":
		serial += jenc.encode(v)
	if t == "R":
		serial += jenc.encode(v)
	if t == "I":
		serial += jenc.encode(v)
	if t == "B":
		serial += jenc.encode("/entity/" + l + "/" + rel)
	if t == "T":
		serial += v
	return serial

def cursor2serial(rel, c):
	serial = ""
	for row in c:
		l = None
		r = None
		if len(row) == 1:
			l = rel[-1:]
		elif len(row) == 2:
			l = rel[-2:-1]
			r = rel[-1:]
		elif len(row) < 1:
			raise PiiError(f"Too few columns: {row}")
		elif len(row) > 2:
			raise PiiError(f"Too many columns: {row}")

		serial += value2serial(l, row[0], rel, row[0])
		serial += f" -- {rel}"
		if r:
			serial += " -- "
			serial += value2serial(r, row[1], rel, row[0])
		serial += "\n"
	return serial

def entity2serial(e, conn):
	serial = ""

	c = conn.cursor()
	c.execute("""select role.l, role.r from RoleEScnn role
					where role.l = ?""", (e, ))
	serial += cursor2serial("RoleES", c)
	c.close()

	c = conn.cursor()
	c.execute("""select lft.r from RoleEScnn role
					join LeftSScnn lft on (lft.l = role.r)
					where role.l = ?""", (e, ))
	rels = []
	for row in c:
		rels += [row[0]]
	c.close()

	c = conn.cursor()
	c.execute("""select role.l, color.r from ColorSScn1 color
					join RoleEScnn role on (color.l = role.r)
					where role.l = ?""", (e, ))
	serial += cursor2serial("ColorES", c)
	c.close()		

	c = conn.cursor()
	c.execute("""select role.l, shape.r from ShapeSScn1 shape
					join RoleEScnn role on (shape.l = role.r)
					where role.l = ?""", (e, ))
	serial += cursor2serial("ShapeES", c)
	c.close()		

	for rel in rels:
		# Find the relations the entity is part of
		c = conn.cursor()
		c.execute(f"""select rel.l, rel.r from {rel} rel
						where rel.l = ?""", (e, ))
		serial += cursor2serial(rel[:-3], c)
		c.close()		

		# Find the identity of related entities
		c = conn.cursor()
		c.execute(f"""select rel.r, id.r from {rel} rel
						join IdentityEScnn id on (rel.r = id.l)
						where rel.l = ?""", (e, ))
		serial += cursor2serial("IdentityES", c)
		c.close()		

		c = conn.cursor()
		c.execute(f"""select rel.r, color.r from ColorSScn1 color
						join RoleEScnn role on (color.l = role.r)
						join {rel} rel on (role.l = rel.r)
						where rel.l = ?""", (e, ))
		serial += cursor2serial("ColorES", c)
		c.close()		

		c = conn.cursor()
		c.execute(f"""select rel.r, shape.r from ShapeSScn1 shape
						join RoleEScnn role on (shape.l = role.r)
						join {rel} rel on (role.l = rel.r)
						where rel.l = ?""", (e, ))
		serial += cursor2serial("ShapeES", c)
		c.close()		

	return serial

###
### Web application

memfiles = {"/pii": ("text/html; charset=UTF-8", """
<!DOCTYPE html>
<html style="height:100%%;">
  <head>
    <title>Product Information Index</title>
    <script type="text/javascript" src="vis-network.min.js"></script>
    <script type="text/javascript" src="pii.js"></script>
  <head/>
  <body style="height:100%%;">
    <div id="mynetwork" style="height:100%%;"></div>
    <script> httpGetAsync('http://localhost:%d/query', parse_relations); </script>
  </body>
</html>
""")}

class HttpHandler(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		global memfiles, webconn

		if not webconn:
			webconn = sqlite3.connect('pii.sqlite3', isolation_level=None)

		if self.path.startswith("/entity/"):
			parts = self.path.split("/")
			if len(parts) == 3:
				self.send_response(200)
				self.send_header("Content-Type", "text/plain; charset=UTF-8")
				self.end_headers()
				self.wfile.write(entity2serial(parts[2], webconn).encode())

			elif len(parts) == 4 and parts[3] == "ValueEB":
				c = webconn.cursor()
				c.execute("""select mimetype.r, value.r
								from MimeTypeEScn1 mimetype, ValueEBcn1 value
								where value.l = mimetype.l and mimetype.l = ?""", (parts[2], ))
				row = c.fetchone()
				self.send_response(200)
				self.send_header("Content-Type", row[0])
				self.end_headers()
				self.wfile.write(row[1])
				c.close()
				
		elif self.path in memfiles.keys():
			self.send_response(200)
			#self.send_header("Content-Type", memfiles[self.path][0])
			self.end_headers()
			self.wfile.write(memfiles[self.path][1].encode())

		else:
			http.server.SimpleHTTPRequestHandler.do_GET(self)

httpd = None

def webserver(webport):
	global httpd

	httpd = socketserver.TCPServer(('', webport), HttpHandler)
	httpd.serve_forever()
	httpd.server_close()
	print("webserver: closed")

def serve(serial):
	global memfiles, httpd, wss_loop

	webport = random.randint(1025, 9999)

	memfiles["/pii"] = (memfiles["/pii"][0], memfiles["/pii"][1] % webport)
	memfiles["/query"] = ("text/plain; charset=UTF-8", serial)
	print(serial)

	web_thread = threading.Thread(target=webserver, args=(webport, ))
	web_thread.start()

	url = f"http://localhost:{webport}/pii"
	print(f"url: {url}")
	webbrowser.open(url)

	input()
	print("webserver: stopping")
	httpd.shutdown()

###
### Pii initialization

if newdb:
	# Core schema
	execute(binary_rel("RoleES"))
	execute(binary_rel("ShapeSS"))
	execute(binary_rel("ColorSS"))
	execute(binary_rel("LeftSS"))
	execute(binary_rel("RightSS"))

if __name__ == '__main__':
	conn.close()

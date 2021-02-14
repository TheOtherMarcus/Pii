"""
Product Information Index

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

import core

__author__ = "Marcus T. Andersson"
__copyright__ = "Copyright 2021, Marcus T. Andersson"
__credits__ = ["Marcus T. Andersson"]
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "Marcus T. Andersson"
__implements__ = []

memfiles = {"/pii": ("text/html; charset=UTF-8", """
<!DOCTYPE html>
<html style="height:100%%;">
  <head>
    <title>Product Information Index</title>
    <script type="text/javascript" src="vis-network.min.js"></script>
    <script type="text/javascript" src="core.js"></script>
  <head/>
  <body style="height:100%%;">
    <form style="position:fixed; z-index: 1; top: 10px; right: 12px;" action="javascript:void(0);">
      <button id="delete" type="button" style="background-color: lightsteelblue; border-color: lightsteelblue;"
      	onclick="javascript:delete_selected();" onmouseup="javascript:document.getElementById('delete').blur();"> &#128465; </button>
      &nbsp; &#65372; &nbsp;
      &#128269; <input id="search" type="text" oninput="javascript:srch(document.getElementById('search').value);"/>
    </form>
    <div id="mynetwork" style="height:100%%;"></div>
    <script> httpGetAsync('http://localhost:%d/query', parse_relations); </script>
  </body>
</html>
""")}

def serve(serial):
	global memfiles

	print(serial)

	webport = 4747

	memfiles["/pii"] = (memfiles["/pii"][0], memfiles["/pii"][1] % webport)
	memfiles["/query"] = ("text/plain; charset=UTF-8", serial)

	core.serve(webport, memfiles, f"http://localhost:{webport}/pii")

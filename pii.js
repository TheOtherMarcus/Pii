/**
 * Product Information Index - Vis Web Client
 *
 * This file implements the Vis graph visualization of Pii data.
 *
 * MIT License
 *
 * Copyright (c) 2020 Marcus T. Andersson
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * @author        Marcus T. Andersson
 * @copyright     Copyright 2020, Marcus T. Andersson
 * @license       MIT
 * @version       15
 */

nodes = [];
edges = [];
network = null;
click = 0;

function findNode(id) {
	var found = null;
	for (node of nodes) {
		if (node.id == id) {
			found = node;
			break;
		}
	}
	if (found == null) {
		found = {id: id, font: { multi: "html", size: 12 }, label: " \n\n", shape: "dot" };
		nodes.push(found)
	}
	return found;
}

function replaceRow(rows, prop, value) {
	for (i = 0; i < rows.length; i++) {
		if (prop + ":" == rows[i].slice(0, prop.length+1)) {
			rows[i] = prop + ": " + value;
			break;
		}
	}
}

function findRow(rows, prop) {
	for (i = 0; i < rows.length; i++) {
		if (prop + ":" == rows[i].slice(0, prop.length+1)) {
			return rows[i].slice(prop.length+2, rows[i].length);
		}
	}
	rows.push(prop + ": ");
	return "";
}

function addNodeProp(node, rows, key, text) {
	if (key == "RoleES") {
		text = text.slice(0, -1);
	}
	if (key.slice(-1, key.length) == "B") {
		node.link = text;
		node.shapeProperties = { borderDashes: [5, 5] };
	}
	rowtext = findRow(rows, prop);
	if (rowtext.length == 0) {
		rowtext = text;
	}
	else if (rowtext.slice(0, 1) != "[") {
		rowtext = "[ " + text + ", " + rowtext + " ]";
	}
	else {
		rowtext = "[ " + text + ", " + rowtext.slice(2, rowtext.length);			
	}
	replaceRow(rows, prop, rowtext);
}

function addNodeText(id, key, text) {
	node = findNode(id);
	prop = key.slice(0, -2);
	rows = node.label.split("\n");
	rows.pop()
	if (key == "LabelES") {
		if (node.shape == "dot") {
			rows[0] = "<b>" + text + "</b>";
		}
	}
	else if (key == "IdentityES") {
		node.title = text;
		if (node.shape != "dot") {
			rows[0] = "<b>" + text + "</b>";
		} 
	}
	else if (key == "ShapeES") {
		node.shape = text;
		if (node.title) {
			rows[0] = "<b>" + node.title + "</b>";
		}
	}
	else if (key == "ColorES") {
		node.color = {background: text, border: "black"}
	}
	else {
		addNodeProp(node, rows, key, text);
	}
	node.label = ""
	for (row of rows) {
		node.label += row + "\n";
	}
	console.log(node.label);
}

function findEdge(id1, label, id2) {
	var found = null;
	label = label.slice(0, -2);
	for (edge of edges) {
		if (edge.from == id1 && edge.to == id2 && edge.label == label) {
			found = edge;
			break;
		}
	}
	if (found == null) {
		found = {from: id1, to: id2, arrows: "to", label: label, font: { size: 12, align: "horizontal" } };
		edges.push(found);
	}
	return found;
}

function parse_relations(text) {
	var lines = text.split("\n");
	for (line of lines) {
		parts = line.split(" -- ");
		console.log(parts)
		if (parts.length == 3) {
			findNode(parts[0]);
			if (parts[2].charAt(0) == "\"") {
				addNodeText(parts[0], parts[1], eval(parts[2]));
			}
			else {
				findNode(parts[2]);
				findEdge(parts[0], parts[1], parts[2]);
			}
		}
	}
	if (!network) {
		newNetwork();
	}
	else {
		network.setData({nodes: nodes, edges: edges});
	}
}

function parse_relations_and_move(nodeid) {
	return function (text) {
		parse_relations(text);
		window.setTimeout(function() {
			movement = {position: {x: network.body.nodes[nodeid].x, y: network.body.nodes[nodeid].y}, scale: 1, animation: { duration: 1000, easingFunction: "easeInOutQuad" } }
			console.log(movement)
			network.moveTo(movement);
		}, 200);
	};
}

function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function newNetwork() {
	var container = document.getElementById("mynetwork");
	var data = {
		nodes: nodes,
		edges: edges,
	};
	var options = {
		/*layout: {
	        hierarchical: {
	          direction: "UD",
	          shakeTowards: "leaves",
	          sortMethod: "hubsize"
	        },
	      },*/
		//physics: { hierarchicalRepulsion: { avoidOverlap: 1 }, },
		physics: {
            forceAtlas2Based: {
              gravitationalConstant: -26,
              centralGravity: 0.001,
              springLength: 230,
              springConstant: 0.18,
            },
            maxVelocity: 146,
            solver: "forceAtlas2Based",
            timestep: 0.35,
            stabilization: { iterations: 150 },
          },
		interaction: { navigationButtons: true },
	};
	network = new vis.Network(container, data, options);
	network.on("click", function (params) {
		click = 1;
		nodeid = params.nodes[0]
		node = findNode(nodeid);
		if (params.event.srcEvent.altKey) {
			if (node.link && node.link.length > 0) {
				window.open(node.link);
			}
		}
		else if (params.nodes.length > 0) {
			movement = {position: {x: network.body.nodes[nodeid].x, y: network.body.nodes[nodeid].y}, animation: { duration: 1000, easingFunction: "easeInOutQuad" } }
			window.setTimeout(function() {
				if (click == 1) {
					network.moveTo(movement);
				}
			}, 200);
		}
	});
	network.on("doubleClick", function (params) {
		click = 2;
		if (params.nodes.length > 0) {
			nodeid = params.nodes[0]
			node = findNode(nodeid);
			rows = node.label.split("\n");
			if (findRow(rows, "Role").length == 0) {
				node.label = " \n\n";
				httpGetAsync("entity/" + nodeid, parse_relations_and_move(nodeid));
			}
			else {
				movement = {position: {x: network.body.nodes[nodeid].x, y: network.body.nodes[nodeid].y}, scale: 1, animation: { duration: 1000, easingFunction: "easeInOutQuad" } }
				network.moveTo(movement);
			}
		}
	});
}

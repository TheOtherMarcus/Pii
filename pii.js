nodes = []
edges = []

function addNode(id) {
	var found = null;
	for (node of nodes) {
		if (node.id == id) {
			found = node;
			break;
		}
	}
	if (found == null) {
		found = {id: id, font: { multi: "html", size: 12 }, label: " \n\n", shape: "box"};
		nodes.push(found)
	}
	return found;
}

function replaceRow(rows, key, value) {
	for (i = 0; i < rows.length; i++) {
		console.log(key + ":");
		console.log(rows[i].slice(0, key.length+1));
		if (key + ":" == rows[i].slice(0, key.length+1)) {
			rows[i] = value;
			break;
		}
	}
}

function addNodeText(id, key, text) {
	node = addNode(id);
	rows = node.label.split("\n");
	rows.pop()
	if (key == "IdentityES") {
		rows[0] += "<b>" + text + "</b>";
	}
	else if (key == "RoleES") {
		if (node[key]) {
			node[key].push(text.slice(0, -1));
		}
		else {
			node[key] = [text.slice(0, -1)];
			rows.push(key.slice(0, -2) + ": ")
		}
		value = key.slice(0, -2) + ": [ "
		for (v of node[key]) {
			value += v + ", "
		}
		value += "]"
		replaceRow(rows, key.slice(0, -2), value)
	}
	else {
		rows.push(key.slice(0, -2) + ": " + text);
	}
	node.label = ""
	for (row of rows) {
		node.label += row + "\n";
	}
	console.log(node.label);
}

function addEdge(id1, label, id2) {
	edges.push({from: id1, to: id2, label: label.slice(0, -2), font: { size: 12, align: "horizontal" } });
}

function parse_relations(text) {
	var lines = text.split("\n");
	for (line of lines) {
		parts = line.split(" -- ");
		console.log(parts)
		if (parts.length == 3) {
			addNode(parts[0]);
			if (parts[2].charAt(0) == "\"") {
				addNodeText(parts[0], parts[1], eval(parts[2]));
			}
			else {
				addNode(parts[2]);
				addEdge(parts[0], parts[1], parts[2]);
			}
		}
	}
	// create a network
	var container = document.getElementById("mynetwork");
	var data = {
		nodes: nodes,
		edges: edges,
	};
	var options = {
		layout: {
            hierarchical: {
              direction: "UD",
              sortMethod: "directed",
            },
          },
		physics: { hierarchicalRepulsion: { avoidOverlap: 1 }, },
		interaction: { navigationButtons: true },
	};
	network = new vis.Network(container, data, options);
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

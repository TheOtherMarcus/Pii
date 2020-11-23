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
		found = {id: id, font: { size: 12 }, label: "\n|\n\n", shape: "box"};
		nodes.push(found)
	}
	return found;
}

function addNodeText(id, key, text) {
	node = addNode(id);
	rows = node.label.split("\n");
	rows.pop()
	if (key == "IdentityES") {
		rows[0] += text;
	}
	else if (key == "RoleES") {
		rows[1] += text + "|";
	}
	else {
		rows.push(key + ": " + text);
	}
	node.label = ""
	for (row of rows) {
		node.label += row + "\n";
	}
	console.log(node.label);
}

function addEdge(id1, label, id2) {
	edges.push({from: id1, to: id2, label: label, font: { size: 12, align: "horizontal" } });
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

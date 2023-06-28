// Create a new network instance
var allNodes = [
{% for res in storyRelationsResult['results']['bindings'] %}
{ id:"{{res['representation']['value']}}", label:"{{res['reprLabel']['value']}}", classLabel:"{{res['classLabel']['value']}}"},
{ id:"{{res['representation2']['value']}}", label:"{{res['reprLabel2']['value']}}", classLabel:"{{res['classLabel2']['value']}}"},
{% endfor %}
]

var uniqueNodes = Array.from(new Set(allNodes.map(JSON.stringify)), JSON.parse);

var container = document.getElementById("network")
var data = {
  nodes: uniqueNodes,

  edges: [

 {% for res in storyRelationsResult['results']['bindings'] %}
   { from:  "{{res['representation']['value']}}", to: "{{res['representation2']['value']}}" , label:"{{res['relLabel']['value']}}"},
 {% endfor %}
  ]
};


// Set colors based on classLabel value
data.nodes.forEach(function(node) {
var color;
if (node.classLabel === "Personaggio") {
 color = "#7FB77E";
} else if (node.classLabel === "Oggetto inanimato") {
 color = "#F7F6DC";
} else if (node.classLabel === "Luogo ideale") {
 color = "#B1D7B4";
} else if (node.classLabel === "Evento") {
 color = "#FFC090";
} else {
 color = "gray";
}
node.color = color;
});

var options = {
  layout: {
      hierarchical: false, // Disable hierarchical layout
      randomSeed: 2, // Set a random seed for consistent results
      improvedLayout: true, // Enable improved layout algorithm
    },
physics: {
 barnesHut: {
   gravitationalConstant: -2000,
   centralGravity: 0.3,
   springLength: 250,
   springConstant: 0.05,
   damping: 0.09,
   avoidOverlap: 0
 },
 maxVelocity: 50,
 minVelocity: 0.1,
 solver: "barnesHut",
 stabilization: {
   iterations: 250
 }
}
};

// Create the legend dynamically
var legendContainer = document.getElementById("legend");
var legendItems = {};

data.nodes.forEach(function(node) {
  if (!legendItems[node.classLabel]) {
    legendItems[node.classLabel] = node.color;
  }
});

for (var classLabel in legendItems) {
  var legendItem = document.createElement("span");
  legendItem.className = "legend-item";

  var legendColor = document.createElement("span");
  legendColor.className = "legend-color";
  legendColor.style.backgroundColor = legendItems[classLabel];

  var legendLabel = document.createElement("span");
  legendLabel.innerText = classLabel;

  legendItem.appendChild(legendColor);
  legendItem.appendChild(legendLabel);

  legendContainer.appendChild(legendItem);

}

var network = new vis.Network(container, data, options);

// Zoom In function
function zoomIn() {
  var scale = network.getScale();
  network.moveTo({
    scale: scale * 1.1, // Increase the scale by 10%
    animation: true, // Enable animation
    animationDuration: 1000 // Animation duration in milliseconds
  });
}

// Zoom Out function
function zoomOut() {
  var scale = network.getScale();
  network.moveTo({
    scale: scale * 0.9, // Decrease the scale by 10%
    animation: true, // Enable animation
    animationDuration: 1000 // Animation duration in milliseconds
  });
}

// Reset Zoom function
function resetZoom() {
network.moveTo({
 scale: 0.7, // Set the scale to the default value (1)
 animation: true, // Enable animation
 animationDuration: 1000 // Animation duration in milliseconds
});
}

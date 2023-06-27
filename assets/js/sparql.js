const yasqe = new Yasqe(document.getElementById("yasqe"));

// Set the response in the Yasgui results table
const yasr = new Yasr(document.getElementById("yasr"));
// Set the query text
yasqe.setValue("SELECT DISTINCT ?subject ?predicate ?object WHERE { ?subject ?predicate ?object . }");

// Get the "play" button element
var playButton = document.getElementsByClassName("yasqe_queryButton");

// Add event listener to the "play" button
Array.from(playButton).forEach(function(button) {
  button.addEventListener("click", function() {

    var query = yasqe.getValue();

    // Make an HTTP POST request to the backend
    fetch('./process_query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ string: query })
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error(response.status + ' ' + response.statusText);
        }
      })
      .then(data => {
        // Handle the response from the backend
        if (typeof data === 'object') {

					// Show the Yasr results
          document.getElementById("yasr").style.display = "block";
          // If the response is a JSON object, draw the results in Yasr
          yasr.draw();
          yasr.setResponse({
            data: data,
            contentType: "application/sparql-results+json",
            status: 200,
            executionTime: 1000 // ms
          });
          // Draw results with the current plugin
          yasr.draw();
          // Check whether a result has been drawn
          yasr.somethingDrawn();

          // Select a plugin
          yasr.selectPlugin("table");

          // Hide the error paragraph if it was previously displayed
          var errorParagraph = document.getElementById("error-paragraph");
          errorParagraph.style.display = "none";

        } else {
          // If the response is a string, show an error message in the HTML
          var errorParagraph = document.getElementById("error-paragraph");
          errorParagraph.textContent = "Error: " + data;
          errorParagraph.style.display = "block";

          // Hide the Yasr results
          document.getElementById("yasr").style.display = "none";
        }
      })
      .catch(error => {
        // Handle any error that occurred during the request
        var errorParagraph = document.getElementById("error-paragraph");
        errorParagraph.textContent = "Error: " + error.message;
        errorParagraph.style.display = "block";

        // Hide the Yasr results
        document.getElementById("yasr").style.display = "none";
      });
  });
});

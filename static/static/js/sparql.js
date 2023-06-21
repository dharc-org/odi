
const yasgui = new Yasgui(document.getElementById("yasgui"));



var query = "SELECT ?s WHERE {?s ?p ?o} LIMIT 10"

// Make an HTTP POST request to the backend
fetch('/process_query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ string: query })
})
  .then(response => response.json())
  .then(data => {
    // Handle the response from the backend
    console.log(data.response);

    // Set the response in the Yasgui results table
    yasr.setResponse({
				data: data,
				contentType: "application/sparql-results+json",
				status: 200,
				executionTime: 1000 // ms
    });
		// Check whether a result has been drawn
	yasgui.yasr.somethingDrawn()

  })

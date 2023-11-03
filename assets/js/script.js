/*
  ==========================
  |    ENABLE POPOVERS     |
  ==========================
*/

var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl)
})

/*
  ==========================
  |     BREADCRUMBS       |
  ==========================
*/

function toCamelCase(text) {
  return text.replace(/(?:^\w|[A-Z]|\b\w)/g, function(match, index) {
    return index === 0 ? match.toLowerCase() : match.toUpperCase();
  }).replace(/\s+/g, '');
}

function breadcrumbs() {

  const previousPageUrl = document.referrer;

  const linkElements = previousPageUrl.split('/');
  const category = linkElements[3]
  const pageName = linkElements[4].replaceAll('-', ' ')
  const pageName2 = pageName.replaceAll(/([a-z])([A-Z])/g, '$1 $2');
  const pageName3 = pageName2.replaceAll('tuttelealtrestorie', 'Tutte le altre storie');
  const pageName4 = decodeURIComponent(pageName3)

  if (pageName4 != '') {
  var breadcrumbHTML = '<div class="btn btn-light">Ritorna a: <a href=\"' + previousPageUrl + '\">'+ category + ' > ' + pageName4 + '</a></div>';
  }
  else {
    var breadcrumbHTML = ''
  }
  // Render the breadcrumbs
  var breadcrumbsContainer = document.getElementById('breadcrumbs');
  breadcrumbsContainer.innerHTML = breadcrumbHTML;
}

window.onload = breadcrumbs;

/*
  ==========================
  |    INDEXES FILTERS      |
  ==========================
*/

document.addEventListener('DOMContentLoaded', function() {
  // Check if the elements with class 'list-group-item1' and 'search-result-item' exist on the page
  var listGroupItem1Elements = document.querySelectorAll('.list-group-item1');
  var searchResultItemElements = document.querySelectorAll('.search-result-item');

  if (listGroupItem1Elements.length > 0 && searchResultItemElements.length > 0) {
    // Attach event handlers for the first set of elements
    listGroupItem1Elements.forEach(function(element) {
      element.addEventListener('click', function() {
        var selectedCategory = element.dataset.category;
        // Rest of your event handling code for the first set of elements
      });
    });
  }

  // Check if the elements with class 'list-group-item2' and 'search-result-item2' exist on the page
  var listGroupItem2Elements = document.querySelectorAll('.list-group-item2');
  var searchResultItem2Elements = document.querySelectorAll('.search-result-item2');

  if (listGroupItem2Elements.length > 0 && searchResultItem2Elements.length > 0) {
    // Attach event handlers for the second set of elements
    listGroupItem2Elements.forEach(function(element) {
      element.addEventListener('click', function() {
        var selectedCategory2 = element.dataset.category;
        // Rest of your event handling code for the second set of elements
      });
    });
  }
});

/*
  ==========================
  |     IMAGE VIEWER       |
  ==========================
*/

// Get all the modal elements
var modals = document.querySelectorAll(".modal");

// Get all the trigger elements (images)
var triggerImages = document.querySelectorAll(".image-click");

// Loop through all the trigger elements and attach a click event handler
for (var i = 0; i < triggerImages.length; i++) {
  triggerImages[i].addEventListener("click", function() {
    var modal = this.closest("div").querySelector(".modal");
    var modalImg = modal.querySelector(".modal-content");
    var captionText = modal.querySelector("#caption");
    modal.style.display = "block";
    modalImg.src = this.src;
    captionText.innerHTML = this.alt;
  });
}

// Get all the close buttons
var closeButtons = document.querySelectorAll(".close");

// Loop through all the close buttons and attach a click event handler
for (var i = 0; i < closeButtons.length; i++) {
  closeButtons[i].addEventListener("click", function() {
    var modal = this.closest(".modal");
    modal.style.display = "none";
  });
}

/*
  ==========================
  |     NETWORK TOOLS      |
  ==========================
*/

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

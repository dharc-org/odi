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
  // FIRST FILTER IN INDEXES (CARDS)
  var listGroupItems = document.querySelectorAll('.list-group-item1');
  var searchResultItems = document.querySelectorAll('.search-result-item');

  listGroupItems.forEach(function(item) {
    item.addEventListener('click', function() {
      var selectedCategory = item.getAttribute('data-category');

      searchResultItems.forEach(function(resultItem) {
        resultItem.style.display = 'block';
        if (selectedCategory !== 'all' && !resultItem.classList.contains(selectedCategory)) {
          resultItem.style.display = 'none';
        }
      });

      // Button for resetting filters
      var resetFiltersButton = document.getElementById('resetFiltersButton');
      resetFiltersButton.addEventListener('click', function() {
        searchResultItems.forEach(function(resultItem) {
          resultItem.style.display = 'block';
        });
        listGroupItems.forEach(function(listItem) {
          listItem.classList.remove('active');
        });
      });
    });
  });

  // SECOND FILTER IN INDEXES (MEANINGS)
  var listGroupItems2 = document.querySelectorAll('.list-group-item2');
  var searchResultItems2 = document.querySelectorAll('.search-result-item2');

  listGroupItems2.forEach(function(item) {
    item.addEventListener('click', function() {
      var selectedCategory2 = item.getAttribute('data-category');

      searchResultItems2.forEach(function(resultItem) {
        resultItem.style.display = 'block';
        if (selectedCategory2 !== 'all' && !resultItem.classList.contains(selectedCategory2)) {
          resultItem.style.display = 'none';
        }
      });

      // Button for resetting filters
      var resetFiltersButton2 = document.getElementById('resetFiltersButton2');
      resetFiltersButton2.addEventListener('click', function() {
        searchResultItems2.forEach(function(resultItem) {
          resultItem.style.display = 'block';
        });
        listGroupItems2.forEach(function(listItem) {
          listItem.classList.remove('active');
        });
      });
    });
  });
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


/*
  =================================
  |  SEARCH BAR IN DATA TABLES    |
  =================================
*/

// Get the search bar and list items
 const searchBar = document.getElementById('searchBar');
 const listItems = document.querySelectorAll('.list-group-item');
 const noResultsBanner = document.getElementById('noResultsBanner');

 // Add event listener for the input event on the search bar
 searchBar.addEventListener('input', function () {
   const searchTerm = searchBar.value.toLowerCase();
   let hasResults = false;

   // Loop through each list item and check if it matches the search term
   listItems.forEach(item => {
     const itemText = item.textContent.toLowerCase();
     const isMatch = itemText.includes(searchTerm);

     // Show or hide the list item based on the match
     if (isMatch) {
       item.style.display = 'block';
       hasResults = true;
     } else {
       item.style.display = 'none';
     }
   });

   // Show or hide the "No results" banner
   if (hasResults) {
     noResultsBanner.style.display = 'none';
   } else {
     noResultsBanner.style.display = 'block';
   }
 });

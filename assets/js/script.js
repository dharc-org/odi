// BREADCRUMBS

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

// FIRST FILTER IN INDEXES (CARDS)
$(document).ready(function() {
  // Handler for filter clicks
  $('.list-group-item').on('click', function() {
    var selectedCategory = $(this).data('category');
    // Show all search result items
    $('.search-result-item').fadeIn(800);
    // Hide search result items not matching the selected category
    if (selectedCategory !== 'all') {
      $('.search-result-item').not('.' + selectedCategory).hide();
    }

    // Button for resetting filters
    $('#resetFiltersButton').on('click', function() {
      // Show all search result items
      $('.search-result-item').fadeIn(800);
      // Clear the selected category filter
      $('.list-group-item').removeClass('active');
    });
  });
});

// SECOND FILTER IN INDEXES (MEANINGS)
$(document).ready(function() {
  // Handler for filter clicks
  $('.list-group-item2').on('click', function() {
    var selectedCategory2 = $(this).data('category');
    // Show all search result items
    $('.search-result-item2').fadeIn(800);
    // Hide search result items not matching the selected category
    if (selectedCategory2 !== 'all') {
      $('.search-result-item2').not('.' + selectedCategory2).hide();
    }

    // Button for resetting filters
    $('#resetFiltersButton2').on('click', function() {
      // Show all search result items
      $('.search-result-item2').fadeIn(800);
      // Clear the selected category filter
      $('.list-group-item2').removeClass('active');
    });
  });
});

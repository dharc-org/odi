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

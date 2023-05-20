console.log('oi');
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    console.log('Geolocation is not supported by this browser.');
  }
}

function showPosition(position) {
  const latitude = position.coords.latitude;
  const longitude = position.coords.longitude;
  document.getElementById('latitude').value = latitude;
  document.getElementById('longitude').value = longitude;
}

// Chama a função getLocation quando a página é carregada
window.onload = getLocation;

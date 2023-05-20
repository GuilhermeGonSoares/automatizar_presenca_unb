function initAutocomplete() {
  const input = document.getElementById('localizacao');
  const options = {
    componentRestrictions: { country: 'br' },
    fields: ['formatted_address', 'geometry.location'],
    strictBounds: true,
  };
  const autocomplete = new google.maps.places.Autocomplete(input, options);
  // Adiciona um listener para detectar quando uma localização é selecionada
  autocomplete.addListener('place_changed', function () {
    const place = autocomplete.getPlace(); // Obtém a localização selecionada
    const lat = place.geometry.location.lat();
    const lng = place.geometry.location.lng();

    if (!place.geometry) return;
    console.log(lat, lng);

    document.getElementById('localizacao').value = place.formatted_address;
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lng;
  });
}

// Inicia a API do Google Maps Autocomplete
function loadScript() {
  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initAutocomplete`;
  document.body.appendChild(script);
}

// Chama a função de iniciar a API quando a página é carregada
window.onload = loadScript;

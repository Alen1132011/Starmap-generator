const form = document.getElementById('config-form');
const img = document.getElementById('main-preview');
const statusPill = document.getElementById('status-pill');
const statusText = document.getElementById('status-text');
let debounceTimer = null;
let currentLang = 'en';

const translations = {
  bs: {
    'status-ready': 'SPREMNO',
    'status-drawing': 'CRTANJE...',
    'status-error': 'GREŠKA',
    'stamp-text': 'REV A',
    'header-title': 'Nacrt Zvjezdane Karte',
    'header-subtitle': 'lični print noćnog neba',
    'sec-1': 'Položaj i Stil Teksta',
    'sec-2': 'Nebeske Koordinate',
    'sec-3': 'Boje i Paleta',
    'sec-4': 'Tipografija',
    'sec-5': 'Natpisi na Posteru',
    'sec-6': 'Elementi Prikaza',
    'label-main-title': 'Glavni Naslov',
    'label-main-height': 'Visina Naslova',
    'label-sub-title': 'Podnaslov',
    'label-sub-height': 'Visina Podnaslova',
    'label-info-height': 'Visina Info Bloka',
    'label-datetime': 'Datum (G M D) | Vrijeme (H M)',
    'label-latlon': 'Geografska Širina / Dužina',
    'label-presets': 'Brze Astro Teme',
    'label-custom-colors': 'Prilagođene Boje',
    'picker-bg-text': 'Boja Pozadine',
    'picker-frame-text': 'Boja Okvira',
    'picker-stars-text': 'Boja Zvijezda i Linija',
    'picker-text-text': 'Boja Teksta',
    'label-font': 'Odaberi Font',
    'label-location': 'Lokacija',
    'label-date-text': 'Datum (tekst)',
    'label-shape': 'Oblik Mape Zvijezda',
    'opt-circle': 'Klasični Krug',
    'opt-heart': 'Romantično Srce',
    'toggle-frame': 'Vanjski okvir',
    'toggle-grid': 'Astro Grid',
    'toggle-lines': 'Sazviježđa',
    'toggle-moon': 'Prikaži fazu Mjeseca',
    'btn-surprise': 'Iznenadi Me',
    'btn-reset': 'Reset',
    'btn-save': 'Sačuvaj Poster',
    'label-map-search': 'Pretraži grad ili klikni na mapu',
    'btn-search': 'Traži',
    'placeholder-search': 'Npr. Tuzla, BiH...',
    'placeholder-font': 'Pretraži font...',
    'gate-title': 'Prijaviti se da sačuvaš svoj rad?',
    'gate-text': 'Radovi kao gost ostaju samo na ovom ekranu — prijavi se pa ti se sačuvaju na nalogu za kasnije.',
    'gate-login': 'Prijava',
    'gate-register': 'Registracija',
    'gate-skip': 'Nastavi kao Gost',
    'auth-guest-note': 'Nisi prijavljen — radiš kao gost.',
    'btn-login-link': 'PRIJAVA',
    'btn-register-link': 'REGISTRACIJA'
  },
  en: {
    'status-ready': 'READY',
    'status-drawing': 'RENDERING...',
    'status-error': 'ERROR',
    'stamp-text': 'REV A',
    'header-title': 'Star Chart Draft',
    'header-subtitle': 'custom night-sky print',
    'sec-1': 'Text Placement & Style',
    'sec-2': 'Celestial Coordinates',
    'sec-3': 'Colors & Palette',
    'sec-4': 'Typography',
    'sec-5': 'Poster Inscriptions',
    'sec-6': 'Display Elements',
    'label-main-title': 'Main Title',
    'label-main-height': 'Title Height',
    'label-sub-title': 'Subtitle',
    'label-sub-height': 'Subtitle Height',
    'label-info-height': 'Info Block Height',
    'label-datetime': 'Date (Y M D) | Time (H M)',
    'label-latlon': 'Latitude / Longitude',
    'label-presets': 'Quick Astro Themes',
    'label-custom-colors': 'Custom Colors',
    'picker-bg-text': 'Background Color',
    'picker-frame-text': 'Outer Frame Color',
    'picker-stars-text': 'Stars & Lines Color',
    'picker-text-text': 'Text Color',
    'label-font': 'Select Font',
    'label-location': 'Location',
    'label-date-text': 'Date (text)',
    'label-shape': 'Star Map Shape',
    'opt-circle': 'Classic Circle',
    'opt-heart': 'Romantic Heart',
    'toggle-frame': 'Outer Frame',
    'toggle-grid': 'Astro Grid',
    'toggle-lines': 'Constellations',
    'toggle-moon': 'Show Moon Phase',
    'btn-surprise': 'Surprise Me',
    'btn-reset': 'Reset',
    'btn-save': 'Save Poster',
    'label-map-search': 'Search city or click on the map',
    'btn-search': 'Search',
    'placeholder-search': 'e.g. London, UK...',
    'placeholder-font': 'Search font...',
    'gate-title': 'Log in to save your work?',
    'gate-text': 'Guest posters only stay on this screen — sign in and they get saved to your account so you can come back to them later.',
    'gate-login': 'Log In',
    'gate-register': 'Register',
    'gate-skip': 'Continue as Guest',
    'auth-guest-note': 'Not logged in — working as a guest.',
    'btn-login-link': 'LOG IN',
    'btn-register-link': 'REGISTER'
  }
};

function setLang(lang){
  currentLang = lang;
  document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));

  if(window.event && window.event.target){
    window.event.target.classList.add('active');
  } else {
    document.querySelectorAll('.lang-btn').forEach(btn => {
      if(btn.textContent.trim().toLowerCase() === lang) btn.classList.add('active');
    });
  }

  document.querySelectorAll('[data-key]').forEach(el => {
    const key = el.getAttribute('data-key');
    if(translations[lang][key]){
      if(el.tagName === 'OPTION'){ el.text = translations[lang][key]; }
      else { el.textContent = translations[lang][key]; }
    }
  });

  const searchInput = document.getElementById('map-search-input');
  if(searchInput && translations[lang]['placeholder-search']) searchInput.placeholder = translations[lang]['placeholder-search'];

  const fontSearch = document.getElementById('font-search-input');
  if(fontSearch && translations[lang]['placeholder-font']) fontSearch.placeholder = translations[lang]['placeholder-font'];
}

function filterFonts(){
  const filterText = document.getElementById('font-search-input').value.toLowerCase();
  const selectMenu = document.getElementById('font-select-dropdown');
  const options = selectMenu.options;
  for(let i = 0; i < options.length; i++){
    const fontName = options[i].text.toLowerCase();
    options[i].style.display = fontName.includes(filterText) ? "" : "none";
  }
}

function liveVal(name){
  const element = form.querySelector(`[name=${name}]`);
  if(element) document.getElementById('v_' + name).textContent = element.value;
}

function applyPreset(bgColor, frameColor, starsColor, textColor){
  document.getElementById('picker-bg').value = bgColor;
  document.getElementById('picker-frame').value = frameColor;
  document.getElementById('picker-stars').value = starsColor;
  document.getElementById('picker-text').value = textColor;
  updatePreview();
}

function updatePreview(){
  clearTimeout(debounceTimer);
  statusPill.classList.add('busy');
  statusText.textContent = translations[currentLang]['status-drawing'];
  img.classList.add('loading');
  debounceTimer = setTimeout(() => {
    const formData = new FormData(form);
    fetch('/update', { method: 'POST', body: formData })
      .then(r => r.json())
      .then(data => {
        img.src = data.image_url;
        document.getElementById('download-link').href = data.image_url;
        img.classList.remove('loading');
        statusPill.classList.remove('busy');
        statusText.textContent = translations[currentLang]['status-ready'];
      })
      .catch(() => {
        img.classList.remove('loading');
        statusPill.classList.remove('busy');
        statusText.textContent = translations[currentLang]['status-error'];
      });
  }, 250);
}

function resetForm(){
  form.reset();
  document.getElementById('font-search-input').value = "";
  filterFonts();
  liveVal('y_main'); liveVal('y_sub'); liveVal('y_info');
  liveVal('ls_main'); liveVal('ls_sub'); liveVal('ls_info');
  updatePreview();
}

function randomizeLayout(){
  const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
  form.querySelector('[name=y_main]').value = rand(1800, 3200);
  form.querySelector('[name=y_sub]').value = rand(1900, 3300);
  form.querySelector('[name=y_info]').value = rand(2000, 3200);
  form.querySelector('[name=ls_main]').value = rand(0, 40);
  form.querySelector('[name=ls_sub]').value = rand(0, 25);
  form.querySelector('[name=ls_info]').value = rand(0, 15);

  liveVal('y_main'); liveVal('y_sub'); liveVal('y_info');
  liveVal('ls_main'); liveVal('ls_sub'); liveVal('ls_info');

  const randomHex = () => '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0');
  applyPreset(randomHex(), randomHex(), randomHex(), randomHex());
}

document.getElementById('frame-wrap').addEventListener('click', function(){
  this.classList.toggle('zoomed');
});

let leafletMap, marker;

function searchCity(){
  const query = document.getElementById('map-search-input').value;
  if(!query) return;

  fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1&accept-language=${currentLang}`)
    .then(r => r.json())
    .then(data => {
      if(data && data.length > 0){
        const newLat = parseFloat(data[0].lat);
        const newLon = parseFloat(data[0].lon);
        leafletMap.setView([newLat, newLon], 11);

        let nameParts = data[0].display_name.split(',');
        let city = nameParts[0].toUpperCase();
        let country = nameParts.pop().trim().toUpperCase();

        const locationInput = document.querySelector('[name=lokacija]');
        if(locationInput) locationInput.value = `${city}, ${country}`;

        updateLocationFromMap(newLat, newLon);
      } else {
        alert(currentLang === 'bs' ? "Grad nije pronađen. Pokušaj ponovo." : "City not found. Try again.");
      }
    })
    .catch(() => alert(currentLang === 'bs' ? "Greška pri povezivanju sa servisom." : "Error connecting to search service."));
}

function initMap(){
  const initialLat = parseFloat(document.getElementById("input-lat").value) || 20;
  const initialLon = parseFloat(document.getElementById("input-lon").value) || 0;

  leafletMap = L.map('map', { attributionControl: false }).setView([initialLat, initialLon], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(leafletMap);
  marker = L.marker([initialLat, initialLon], { draggable: true }).addTo(leafletMap);

  leafletMap.on('click', e => updateLocationFromMap(e.latlng.lat, e.latlng.lng));
  marker.on('dragend', () => {
    const pos = marker.getLatLng();
    updateLocationFromMap(pos.lat, pos.lng);
  });
}

function updateLocationFromMap(lat, lon){
  document.getElementById('input-lat').value = lat.toFixed(4);
  document.getElementById('input-lon').value = lon.toFixed(4);
  marker.setLatLng([lat, lon]);
  updatePreview();
}

function locateMe(){
  if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(position => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      leafletMap.setView([lat, lon], 12);
      updateLocationFromMap(lat, lon);
    }, () => {
      alert(currentLang === 'bs' ? "Nemoguće pristupiti lokaciji." : "Unable to retrieve your location.");
    });
  } else {
    alert(currentLang === 'bs' ? "Geolokacija nije podržana u vašem browseru." : "Geolocation is not supported by your browser.");
  }
}

function dismissGate(){
  const gate = document.getElementById('gate-overlay');
  if(gate) gate.style.display = 'none';
}

function savePosterToDatabase(){
  const title = document.getElementById('save-project-title').value;
  const formData = new FormData(form);
  formData.append('naslov_projekta', title);

  fetch('/save_poster', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => { alert(data.message); loadPostersFromDatabase(); });
}

function loadPostersFromDatabase(){
  const list = document.getElementById('db-saved-posters');
  if(!list) return;

  fetch('/get_posters')
    .then(res => res.json())
    .then(data => {
      list.innerHTML = "";
      if(data.posters.length === 0){
        list.innerHTML = "<li style='padding:6px; font-size:10px; color:var(--cyan-dim);'>Nema sačuvanih radova.</li>";
        return;
      }
      data.posters.forEach(p => {
        const item = document.createElement('li');
        item.className = "saved-item";
        item.innerHTML = `
          <div class="poster-card">
            ${p.preview_path ? `
              <img src="/${p.preview_path}?v=${Date.now()}" alt="${p.naslov}" class="poster-thumb">
            ` : `
              <div class="poster-thumb-placeholder">
                <div class="placeholder-icon">🖼️</div>
                <div class="placeholder-text">No Preview</div>
              </div>
            `}
            <div class="poster-info">
              <div class="poster-title">${p.naslov}</div>
              <div class="poster-subtitle">${p.ime_prezime || 'Anonymous'}</div>
            </div>
            <div class="poster-actions">
              <button onclick="loadDesign(${p.id})" class="btn-ghost btn-sm">LOAD</button>
              <button onclick="deleteDesign(${p.id}, event)" class="btn-ghost btn-sm danger">×</button>
            </div>
          </div>
        `;
        list.appendChild(item);
      });
    });
}

function loadDesign(id){
  statusPill.classList.add('busy');
  statusText.textContent = "UČITAVANJE...";
  fetch(`/load_poster/${id}`)
    .then(res => res.json())
    .then(data => {
      for(const [key, val] of Object.entries(data)){
        const input = form.querySelector(`[name="${key}"]`);
        if(input){
          if(input.type === 'checkbox'){ input.checked = (val === 'on'); }
          else { input.value = val; }
        }
      }
      const newLat = parseFloat(data.lat);
      const newLon = parseFloat(data.lon);
      leafletMap.setView([newLat, newLon], 8);
      marker.setLatLng([newLat, newLon]);

      liveVal('y_main'); liveVal('y_sub'); liveVal('y_info');
      liveVal('ls_main'); liveVal('ls_sub'); liveVal('ls_info');

      updatePreview();
    });
}

function deleteDesign(id, event){
  event.stopPropagation();
  if(!confirm("Da li sigurno želiš obrisati ovaj rad?")) return;
  fetch(`/delete_poster/${id}`, { method: 'POST' })
    .then(res => res.json())
    .then(() => loadPostersFromDatabase());
}

window.onload = function(){
  form.reset();
  document.getElementById('font-search-input').value = "";
  initMap();
  setLang('en');
  loadPostersFromDatabase();
  updatePreview();
};
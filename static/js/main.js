// map_app/static/js/main.js

// グローバル変数
let map;
let markers = [];

// Google Mapsの初期化
function initMap(mapElementId, initialCenter = { lat: 35.6762, lng: 139.6503 }, initialZoom = 10) {
    map = new google.maps.Map(document.getElementById(mapElementId), {
        center: initialCenter,
        zoom: initialZoom,
        mapTypeId: 'roadmap',
        mapTypeControl: false
    });

    // マップタイプ切り替えコントロールの追加
    addMapTypeControls();

    return map;
}

// マップタイプ切り替えコントロールの追加
function addMapTypeControls() {
    const mapTypeControlDiv = document.createElement('div');
    mapTypeControlDiv.classList.add('map-type-control');
    mapTypeControlDiv.innerHTML = `
        <button id="map-view">Map</button>
        <button id="aerial-view">Aerial</button>
    `;
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(mapTypeControlDiv);

    document.getElementById('map-view').addEventListener('click', () => map.setMapTypeId('roadmap'));
    document.getElementById('aerial-view').addEventListener('click', () => map.setMapTypeId('satellite'));
}

// マーカーの追加
function addMarker(location, title, clickCallback) {
    const marker = new google.maps.Marker({
        position: location,
        map: map,
        title: title
    });

    if (clickCallback) {
        marker.addListener('click', clickCallback);
    }

    markers.push(marker);
    return marker;
}

// すべてのマーカーを表示範囲に収める
function fitMapToBounds() {
    const bounds = new google.maps.LatLngBounds();
    markers.forEach(marker => bounds.extend(marker.getPosition()));
    map.fitBounds(bounds);
}

// マーカーの削除
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

// 画像プレビュー機能
function setupImagePreview(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    if (input && preview) {
        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.innerHTML = `<img src="${e.target.result}" class="img-fluid" alt="Preview">`;
                }
                reader.readAsDataURL(file);
            }
        });
    }
}

// 位置検索機能
function setupPlacesSearch(inputId, mapInstance = map) {
    const input = document.getElementById(inputId);
    const searchBox = new google.maps.places.SearchBox(input);

    mapInstance.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    mapInstance.addListener('bounds_changed', () => {
        searchBox.setBounds(mapInstance.getBounds());
    });

    searchBox.addListener('places_changed', () => {
        const places = searchBox.getPlaces();
        if (places.length === 0) return;

        const bounds = new google.maps.LatLngBounds();
        places.forEach(place => {
            if (!place.geometry || !place.geometry.location) {
                console.log("Returned place contains no geometry");
                return;
            }

            addMarker(place.geometry.location, place.name);

            if (place.geometry.viewport) {
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        mapInstance.fitBounds(bounds);
    });
}

// 写真ギャラリー表示
function displayPhotoGallery(photos, galleryElementId) {
    const gallery = document.getElementById(galleryElementId);
    gallery.innerHTML = '';

    photos.forEach(photo => {
        const photoElement = document.createElement('div');
        photoElement.className = 'photo-item';
        photoElement.innerHTML = `
            <img src="${photo.url}" alt="${photo.caption}">
            <div class="photo-info">
                <p>${photo.caption}</p>
                <small>Date: ${photo.date}</small>
            </div>
        `;
        gallery.appendChild(photoElement);
    });
}

// DOMContentLoaded イベントリスナー
document.addEventListener('DOMContentLoaded', () => {
    // 画像プレビュー機能のセットアップ（アップロードページ用）
    setupImagePreview('id_image', 'image-preview');

    // マップ初期化（マップページ用）
    const mapElement = document.getElementById('map');
    if (mapElement) {
        initMap('map');
        setupPlacesSearch('pac-input');
    }
});

// エクスポート（モジュールとして使用する場合）
export {
    addMarker, clearMarkers, displayPhotoGallery, fitMapToBounds, initMap, setupImagePreview,
    setupPlacesSearch
};

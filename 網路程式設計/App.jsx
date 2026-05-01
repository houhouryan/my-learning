import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Coffee, Battery, Wifi, Volume2, Star, MapPin } from 'lucide-react';

// 模擬店家資料
const INITIAL_SHOPS = [
  { id: 1, name: "漫遊咖啡館", lat: 25.033, lng: 121.565, power: 5, wifi: 4, quiet: 3, type: "cafe" },
  { id: 2, name: "程式設計實驗室", lat: 25.035, lng: 121.567, power: 4, wifi: 5, quiet: 5, type: "lab" },
  // ... 更多資料
];

function App() {
  const [shops, setShops] = useState(INITIAL_SHOPS);
  const [filter, setFilter] = useState('all');
  const [selectedShop, setSelectedShop] = useState(null);

  // 計算生產力指數邏輯
  const calculateScore = (shop) => {
    return ((shop.power * 0.4) + (shop.wifi * 0.3) + (shop.quiet * 0.3)).toFixed(1);
  };

  // 即時狀態回報功能 (使用 LocalStorage)
  const handleReport = (id, status) => {
    const timestamp = new Date().toLocaleTimeString();
    const reportData = { status, time: timestamp };
    localStorage.setItem(`report_${id}`, JSON.stringify(reportData));
    alert(`感謝回報！目前狀態：${status === 'full' ? '客滿' : '有位'}`);
  };

  const filteredShops = shops.filter(shop => 
    filter === 'all' || (filter === 'power' && shop.power >= 4) || (filter === 'wifi' && shop.wifi >= 4)
  );

  return (
    <div className="container-fluid vh-100 p-0 d-flex flex-column">
      {/* 頂部導航欄 */}
      <nav className="navbar navbar-dark bg-dark px-3">
        <span className="navbar-brand mb-0 h1 d-flex align-items-center">
          <Coffee className="me-2" /> 城市漫遊 - 地圖探索器
        </span>
      </nav>

      <div className="d-flex flex-grow-1 overflow-hidden">
        {/* 左側功能區 (30%) */}
        <div className="col-3 bg-light p-3 overflow-auto border-end shadow-sm">
          <h5 className="mb-3">生產力篩選</h5>
          <div className="d-flex gap-2 mb-4">
            <button className={`btn btn-sm ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`} onClick={() => setFilter('all')}>全部</button>
            <button className={`btn btn-sm ${filter === 'power' ? 'btn-primary' : 'btn-outline-primary'}`} onClick={() => setFilter('power')}><Battery size={16} /> 插座優先</button>
            <button className={`btn btn-sm ${filter === 'wifi' ? 'btn-primary' : 'btn-outline-primary'}`} onClick={() => setFilter('wifi')}><Wifi size={16} /> 強訊號</button>
          </div>

          <div className="list-group">
            {filteredShops.map(shop => (
              <button 
                key={shop.id} 
                className="list-group-item list-group-item-action p-3"
                onClick={() => setSelectedShop(shop)}
              >
                <div className="d-flex justify-content-between align-items-start">
                  <h6 className="mb-1 fw-bold">{shop.name}</h6>
                  <span className="badge bg-success rounded-pill">{calculateScore(shop)}</span>
                </div>
                <small className="text-muted d-block mt-1">生產力指數 (滿分 5.0)</small>
              </button>
            ))}
          </div>
        </div>

        {/* 右側地圖區 (70%) */}
        <div className="col-9 position-relative">
          <MapContainer center={[25.033, 121.565]} zoom={15} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {filteredShops.map(shop => (
              <Marker key={shop.id} position={[shop.lat, shop.lng]}>
                <Popup>
                  <div style={{ width: '200px' }}>
                    <h6 className="fw-bold">{shop.name}</h6>
                    <hr className="my-2" />
                    <div className="d-flex flex-column gap-1 mb-2">
                      <small><Battery size={14} /> 插座：{shop.power}/5</small>
                      <small><Wifi size={14} /> WiFi：{shop.wifi}/5</small>
                      <small><Volume2 size={14} /> 安靜：{shop.quiet}/5</small>
                    </div>
                    <div className="d-flex gap-1 mt-2">
                      <button className="btn btn-xs btn-outline-success w-50" onClick={() => handleReport(shop.id, 'available')}>有位</button>
                      <button className="btn btn-xs btn-outline-danger w-50" onClick={() => handleReport(shop.id, 'full')}>客滿</button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  );
}

export default App;
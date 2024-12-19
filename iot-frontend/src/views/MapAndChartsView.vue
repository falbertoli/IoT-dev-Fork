<template>
    <div class="map-and-charts-container">
      <div class="map-container" ref="mapContainer"></div>
  
      <transition name="slide-fade">
        <div v-if="showSidePanel" class="side-panel">
          <h2>{{ selectedLocationFromMap }}</h2>
          <h3>Indoor Sensors</h3>
          <ul>
            <li v-for="(sensor, index) in indoorSensors" :key="index">
              <label>
                <input type="radio" v-model="tempSelectedIndoor" :value="sensor" /> {{ sensor }}
              </label>
            </li>
          </ul>
  
          <h3>Outdoor Sensors</h3>
          <ul>
            <li v-for="(sensor, index) in outdoorSensors" :key="index">
              <label>
                <input type="radio" v-model="tempSelectedOutdoor" :value="sensor" /> {{ sensor }}
              </label>
            </li>
          </ul>
  
          <button @click="applySensorSelection">Show</button>
          <button @click="closeSidePanel">Cancel</button>
        </div>
      </transition>
  
      <!-- <h1>Sensor Data Charts</h1> -->
      <!-- Bind the ref to the SelectCharts component -->
      <SelectCharts ref="selectChartsComponent" />
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import L from 'leaflet';
  import axios from 'axios';
  import 'leaflet/dist/leaflet.css';
  import SelectCharts from '../components/SelectCharts.vue';
  
  export default {
    components: {
      SelectCharts
    },
    setup() {
      const mapContainer = ref(null);
      const locationData = ref({});
      const showSidePanel = ref(false);
  
      const selectedLocationFromMap = ref(null);
      const indoorSensors = ref([]);
      const outdoorSensors = ref([]);
      const tempSelectedIndoor = ref('None');
      const tempSelectedOutdoor = ref('None');
  
      // Ref to the SelectCharts component
      const selectChartsComponent = ref(null);
  
      const loadLocations = async () => {
        const response = await axios.get('/locations.json');
        locationData.value = response.data;
      };
  
      const initMap = () => {
        const map = L.map(mapContainer.value).setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: 'Map data © OpenStreetMap contributors'
        }).addTo(map);
  
        for (const locName in locationData.value) {
          const { latitude, longitude } = locationData.value[locName].coordinates;
          const marker = L.marker([latitude, longitude]).addTo(map);
          marker.on('click', () => {
            selectedLocationFromMap.value = locName;
            indoorSensors.value = locationData.value[locName].indoor;
            outdoorSensors.value = locationData.value[locName].outdoor;
            tempSelectedIndoor.value = indoorSensors.value[0] || 'None';
            tempSelectedOutdoor.value = outdoorSensors.value[0] || 'None';
            showSidePanel.value = true;
          });
        }
      };
  
      const applySensorSelection = () => {
        showSidePanel.value = false;
        
        // Access the SelectCharts component directly
        if (selectChartsComponent.value) {
          selectChartsComponent.value.updateSensorsFromParent(
            selectedLocationFromMap.value,
            tempSelectedIndoor.value,
            tempSelectedOutdoor.value
          );
        }
      };
  
      const closeSidePanel = () => {
        showSidePanel.value = false;
      };
  
      onMounted(async () => {
        await loadLocations();
        initMap();
      });
  
      return {
        mapContainer,
        showSidePanel,
        selectedLocationFromMap,
        indoorSensors,
        outdoorSensors,
        tempSelectedIndoor,
        tempSelectedOutdoor,
        applySensorSelection,
        closeSidePanel,
        selectChartsComponent
      };
    }
  };
  </script>
  
  <style scoped>
  .map-and-charts-container {
    position: relative;
    width: 100%;
    height: 100%;
  }
  .map-container {
    width: 100%;
    height: 400px;
    margin-bottom: 20px;
  }
  
  .side-panel {
    position: absolute;
    top: 60px;
    right: 20px;
    width: 300px;
    background: #fff;
    border: 1px solid #ccc;
    padding: 20px;
    z-index: 1000;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
  }
  
  .slide-fade-enter-active, .slide-fade-leave-active {
    transition: opacity .5s;
  }
  .slide-fade-enter-from, .slide-fade-leave-to {
    opacity: 0;
  }
  </style>
  
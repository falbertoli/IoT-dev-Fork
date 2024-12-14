<template>
  <div class="container">
    <div class="selectors">
      <label for="location-select">Location:</label>
      <select id="location-select" v-model="selectedLocation" @change="() => { updateSensorOptions(); fetchData(); }">
        <option v-for="location in locations" :key="location" :value="location">
          {{ location }}
        </option>
      </select>

      <label for="sensor-select">Sensor Type:</label>
      <select id="sensor-select" v-model="selectedSensor" @change="fetchData">
        <option v-for="sensor in sensors" :key="sensor" :value="sensor">
          {{ sensor }}
        </option>
      </select>

      <label for="indoor-sensor-select">Indoor Sensor:</label>
      <select id="indoor-sensor-select" v-model="selectedIndoorSensor" @change="fetchData">
        <option value="None">None</option>
        <option v-for="indoor in indoorSensorOptions" :key="indoor" :value="indoor">
          {{ indoor }}
        </option>
      </select>

      <label for="outdoor-sensor-select">Outdoor Sensor:</label>
      <select id="outdoor-sensor-select" v-model="selectedOutdoorSensor" @change="fetchData">
        <option value="None">None</option>
        <option v-for="outdoor in outdoorSensorOptions" :key="outdoor" :value="outdoor">
          {{ outdoor }}
        </option>
      </select>

      <!-- Delta checkbox -->
      <div>
        <input type="checkbox" id="delta-checkbox" v-model="showDelta" @change="fetchData"/>
        <label for="delta-checkbox">Show Delta</label>
      </div>

      <!-- Range selection -->
      <label for="range-select">Time Range (days):</label>
      <select id="range-select" v-model="selectedRangeDays" @change="fetchData">
        <option v-for="d in possibleRanges" :key="d" :value="d">{{ d }} days</option>
      </select>
    </div>

    <div id="chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

export default {
  setup() {
    // Available locations and their sensors
    const locationSensorMap = {
      'Kendeda': {
        indoor: ['Arcalis'],
        outdoor: ['Atlas']
      },
      'CNES': {
        indoor: ['Antares', 'Arcalis', 'Alcyone', 'Asterope'],
        outdoor: ['Atlas']
      }
    };

    const locations = ref(['Kendeda', 'CNES']);
    const sensors = ref(['co2', 'humidity', 'temperature', 'pressure']);

    const indoorSensorOptions = ref([]);
    const outdoorSensorOptions = ref([]);

    const selectedLocation = ref('Kendeda');
    const selectedSensor = ref('co2');

    // Default to None for indoor/outdoor (no raw data shown)
    const selectedIndoorSensor = ref('None');
    const selectedOutdoorSensor = ref('None');

    // Delta checkbox
    const showDelta = ref(true); // default show delta

    // Time range selection
    const possibleRanges = ref([1, 3, 7, 14, 30]);
    const selectedRangeDays = ref(7); // default 7 days

    let chart = null;

    const updateSensorOptions = () => {
      const loc = selectedLocation.value;
      indoorSensorOptions.value = locationSensorMap[loc].indoor || [];
      outdoorSensorOptions.value = locationSensorMap[loc].outdoor || [];
      if (!indoorSensorOptions.value.includes(selectedIndoorSensor.value) && selectedIndoorSensor.value !== 'None') {
        selectedIndoorSensor.value = 'None';
      }
      if (!outdoorSensorOptions.value.includes(selectedOutdoorSensor.value) && selectedOutdoorSensor.value !== 'None') {
        selectedOutdoorSensor.value = 'None';
      }
    };

    const initChart = () => {
      chart = echarts.init(document.getElementById('chart'));
      const option = {
        title: {
          text: 'Sensor Data',
        },
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: 'category',
          data: [],
          name: 'Time (UTC)',
          nameLocation: 'center',
          nameTextStyle: {
            padding: [35, 0, 0, 0],
          },
        },
        yAxis: {
          type: 'value',
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: 80,
          containLabel: true,
        },
        dataZoom: [
          {
            type: 'inside',
          },
          {
            type: 'slider',
            bottom: 40,
          },
        ],
        series: [],
      };
      chart.setOption(option);
    };

    const fetchData = async () => {
      let timestamps = null;
      const series = [];

      const loc = selectedLocation.value;
      const sensorType = selectedSensor.value;
      const rangeStr = `${selectedRangeDays.value}d`;

      // If delta is shown, we call the delta endpoint:
      if (showDelta.value) {
        // For delta endpoint, we need indoor/outdoor sensor names
        // If user chose None, fallback to a default sensor to fetch delta data
        const defaultIndoor = indoorSensorOptions.value[0];
        const defaultOutdoor = outdoorSensorOptions.value[0];

        if (!defaultIndoor || !defaultOutdoor) {
          console.error('No sensors available to compute delta for this location.');
          return;
        }

        const indoorParam = selectedIndoorSensor.value === 'None' ? defaultIndoor : selectedIndoorSensor.value;
        const outdoorParam = selectedOutdoorSensor.value === 'None' ? defaultOutdoor : selectedOutdoorSensor.value;

        const apiUrl = `/api/delta/${loc}/${sensorType}?indoor_sensor=${indoorParam}&outdoor_sensor=${outdoorParam}&range=${rangeStr}`;
        try {
          const response = await axios.get(apiUrl);
          const { timestamps: newTimestamps, indoor_value, outdoor_value, values: delta_values } = response.data;
          timestamps = newTimestamps;

          // Show indoor line if user selected a sensor
          if (selectedIndoorSensor.value !== 'None') {
            series.push({
              name: `${sensorType} indoor`,
              type: 'line',
              data: indoor_value,
              smooth: true,
            });
          }

          // Show outdoor line if user selected a sensor
          if (selectedOutdoorSensor.value !== 'None') {
            series.push({
              name: `${sensorType} outdoor`,
              type: 'line',
              data: outdoor_value,
              smooth: true,
            });
          }

          // Always show delta line if delta is checked
          series.push({
            name: `${sensorType} delta`,
            type: 'line',
            data: delta_values,
            smooth: true,
          });
        } catch (error) {
          console.error('Error fetching delta data:', error);
        }
      } else {
        // Delta not shown, so we only show raw indoor/outdoor data if selected
        // Call single sensor endpoints for each selected sensor
        if (selectedIndoorSensor.value !== 'None') {
          const indoorUrl = `/api/data/${loc}/${sensorType}/indoor/${selectedIndoorSensor.value}?range=${rangeStr}`;
          try {
            const response = await axios.get(indoorUrl);
            const { timestamps: indoorTimestamps, values: indoorValues } = response.data;
            if (!timestamps) {
              timestamps = indoorTimestamps;
            }
            series.push({
              name: `${sensorType} indoor`,
              type: 'line',
              data: indoorValues,
              smooth: true,
            });
          } catch (error) {
            console.error('Error fetching indoor data:', error);
          }
        }

        if (selectedOutdoorSensor.value !== 'None') {
          const outdoorUrl = `/api/data/${loc}/${sensorType}/outdoor/${selectedOutdoorSensor.value}?range=${rangeStr}`;
          try {
            const response = await axios.get(outdoorUrl);
            const { timestamps: outdoorTimestamps, values: outdoorValues } = response.data;
            if (!timestamps) {
              timestamps = outdoorTimestamps;
            }
            series.push({
              name: `${sensorType} outdoor`,
              type: 'line',
              data: outdoorValues,
              smooth: true,
            });
          } catch (error) {
            console.error('Error fetching outdoor data:', error);
          }
        }
      }

      updateChart(timestamps, series);
    };

    const updateChart = (timestamps, series) => {
      chart.clear();
      const option = {
        tooltip: {
          trigger: 'axis',
        },
        xAxis: {
          type: 'category',
          data: timestamps || [],
          name: 'Time (UTC)',
          nameLocation: 'center',
          nameTextStyle: {
            padding: [35, 0, 0, 0],
          },
        },
        yAxis: {
          type: 'value',
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: 80,
          containLabel: true,
        },
        dataZoom: [
          {
            type: 'inside',
          },
          {
            type: 'slider',
            bottom: 40,
          },
        ],
        series: series,
      };
      chart.setOption(option);
    };

    onMounted(() => {
      updateSensorOptions();
      initChart();
      fetchData();
    });

    return {
      locations,
      sensors,
      indoorSensorOptions,
      outdoorSensorOptions,
      selectedLocation,
      selectedSensor,
      selectedIndoorSensor,
      selectedOutdoorSensor,
      showDelta,
      possibleRanges,
      selectedRangeDays,
      updateSensorOptions,
      fetchData
    };
  },
};
</script>



  
  <style scoped>
  .container {
    padding: 20px;
  }
  .selectors {
    margin-bottom: 20px;
  }
  select {
    margin-right: 10px;
  }
  </style>
  
<template>
    <div class="container">
      <div class="selectors">
        <label for="location-select">Location:</label>
        <select id="location-select" v-model="selectedLocation" @change="fetchData">
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
  
        <label for="data-type-select">Data Type:</label>
        <div v-for="type in dataTypes" :key="type">
          <input type="checkbox" :id="type" :value="type" v-model="selectedDataTypes" @change="fetchData" />
          <label :for="type">{{ type }}</label>
        </div>
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
      // Reactive references for locations, sensors, data types, and user selections
      const locations = ref(['location_1']);
      const sensors = ref(['co2', 'humidity', 'temperature', 'pressure']); // Sensor types
      const dataTypes = ref(['indoor', 'outdoor', 'delta']); // Data types
      const selectedLocation = ref('location_1');
      const selectedSensor = ref('co2'); // Initially select 'co2'
      const selectedDataTypes = ref(['indoor']); // Multi-select for data types
  
      let chart = null;
  
      // Initialize the chart
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
          },
          yAxis: {
            type: 'value',
          },
          series: [], // Series will be populated based on user selection
        };
        chart.setOption(option);
      };
  
      // Fetch data based on user selection
      // Fetch data based on user selection
const fetchData = async () => {
  let timestamps = null;
  const series = [];

  // Loop through each selected data type (indoor, outdoor, delta)
  for (const type of selectedDataTypes.value) {
    let apiUrl = '';
    if (type === 'delta') {
      apiUrl = `/api/delta/${selectedLocation.value}/${selectedSensor.value}`; // delta-specific API
    } else {
      apiUrl = `/api/data/${selectedLocation.value}/${selectedSensor.value}/${type}`;
    }

    try {
      const response = await axios.get(apiUrl);

      // Handle delta case
      if (type === 'delta') {
        const { timestamps: newTimestamps, values } = response.data;
        console.log("Delta Response:", response.data); // Debugging log

        // Store the timestamps from the first response
        if (!timestamps) {
          timestamps = newTimestamps;
        }

        // Add the data series for delta
        series.push({
          name: `${selectedSensor.value} ${type}`,
          type: 'line',
          data: values, // Using 'values' for delta
          smooth: true,
        });
      } else {
        // Handle indoor/outdoor case
        const { timestamps: newTimestamps, values } = response.data;

        // Store the timestamps from the first response
        if (!timestamps) {
          timestamps = newTimestamps;
        }

        // Add the data series for indoor/outdoor
        series.push({
          name: `${selectedSensor.value} ${type}`,
          type: 'line',
          data: values, // Using 'values' for indoor/outdoor
          smooth: true,
        });
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }

  // Update the chart with the data from the backend
  updateChart(timestamps, series);
};

// Update the chart with new data
const updateChart = (timestamps, series) => {
  // 清除之前的所有数据，确保不会有残留的 series
  chart.clear();

  // 重新定义图表的 xAxis、yAxis，并确保 tooltip 存在以保持交互性
  const option = {
    tooltip: {
      trigger: 'axis', // 确保 tooltip 在悬停时显示数据
    },
    xAxis: {
      type: 'category',
      data: timestamps, // 使用后端提供的统一时间戳
    },
    yAxis: {
      type: 'value',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    series: series, // 传入更新后的 series
  };

  // 重新设置图表的配置
  chart.setOption(option);
};

  
      // Call initChart and fetch initial data when the component is mounted
      onMounted(() => {
        initChart();
        fetchData(); // Fetch default data
      });
  
      // Return the reactive references and methods
      return {
        locations,
        sensors,
        dataTypes,
        selectedLocation,
        selectedSensor,
        selectedDataTypes,
        fetchData,
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
  
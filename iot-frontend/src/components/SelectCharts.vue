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

  // 从统一的 delta API 获取所有数据
  const apiUrl = `/api/delta/${selectedLocation.value}/${selectedSensor.value}`;

  try {
    const response = await axios.get(apiUrl);
    const { timestamps: newTimestamps, indoor_value, outdoor_value, values: delta_values } = response.data;

    // 确保 timestamps 是正确的
    timestamps = newTimestamps;

    // 根据用户选择显示对应的 series
    if (selectedDataTypes.value.includes('indoor')) {
      series.push({
        name: `${selectedSensor.value} indoor`,
        type: 'line',
        data: indoor_value, // 使用后端返回的 indoor 数据
        smooth: true,
      });
    }

    if (selectedDataTypes.value.includes('outdoor')) {
      series.push({
        name: `${selectedSensor.value} outdoor`,
        type: 'line',
        data: outdoor_value, // 使用后端返回的 outdoor 数据
        smooth: true,
      });
    }

    if (selectedDataTypes.value.includes('delta')) {
      series.push({
        name: `${selectedSensor.value} delta`,
        type: 'line',
        data: delta_values, // 使用后端返回的 delta 数据
        smooth: true,
      });
    }
  } catch (error) {
    console.error('Error fetching data:', error);
  }

  // 更新图表
  updateChart(timestamps, series);
};



// Update the chart with new data
const updateChart = (timestamps, series) => {
  // 清除之前的所有数据
  chart.clear();

  const option = {
    tooltip: {
      trigger: 'axis', // 确保 tooltip 在悬停时显示数据
    },
    xAxis: {
      type: 'category',
      data: timestamps, // 使用统一的时间戳
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
    series: series, // 传入更新后的 series 数据
  };

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
  
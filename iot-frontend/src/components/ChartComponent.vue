<template>
  <div class="chart-container">
    <div ref="chart" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';

export default {
  props: {
    chartType: String, // e.g., 'co2', 'delta_co2', 'temperature', etc.
    title: String,     // Title for the chart
    location: String,  // Location value e.g., 'location_1'
    indoorOrOutdoor: String // 'indoor' or 'outdoor', optional for non-delta
  },
  mounted() {
    this.initChart();
  },
  methods: {
    async initChart() {
      let data, timestamps, seriesData;
      const location = this.location || 'location_1'; // Default location
      const sensorType = this.chartType.replace('delta_', ''); // Get sensor type without 'delta_'
      
      try {
        // 根据 chartType 判断使用哪种 API
        if (this.chartType.startsWith('delta_')) {
          // 使用 /api/delta/<location>/<sensor_type> 路由
          const response = await axios.get(`/api/delta/${location}/${sensorType}`);
          data = response.data;
          
          // 根据类型，获取 delta 数据
          seriesData = data.values; // 'values' 为 delta 数据
          timestamps = data.timestamps;
          
        } else {
          // 使用 /api/data/<location>/<sensor_type>/<indoor_or_outdoor> 路由
          const indoorOrOutdoor = this.indoorOrOutdoor || 'indoor'; // Default to 'indoor'
          const response = await axios.get(`/api/data/${location}/${sensorType}/${indoorOrOutdoor}`);
          data = response.data;

          // 获取对应的 indoor 或 outdoor 数据
          seriesData = data.values;
          timestamps = data.timestamps;
        }

        // 检查是否成功获取了数据
        if (!timestamps || !seriesData) {
          console.error('No data available for chart:', this.chartType);
          return;
        }

        // eCharts 配置
        const option = {
          title: {
            text: this.title
          },
          tooltip: {
            trigger: 'axis',
            formatter: (params) => {
              return `${params[0].axisValueLabel}<br />${params[0].seriesName}: ${params[0].value}`;
            }
          },
          xAxis: {
            type: 'category',
            data: timestamps
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: this.title,
              type: 'line',
              data: seriesData,
              smooth: true
            }
          ]
        };

        // 初始化或更新图表
        const chartInstance = echarts.init(this.$refs.chart);
        chartInstance.setOption(option);
      } catch (error) {
        console.error('Error fetching data for chart:', error);
      }
    }
  }
}
</script>

  



<style scoped>
  .chart-container {
    display: grid;
    place-items: center; /* 水平和垂直居中 */
    width: 100%;
    height: 40vh; /* 让容器占满整个视口高度 */
  }
  
  .chart {
    width: 600px;
    height: 400px;
  }
  </style>
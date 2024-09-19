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
      chartType: String,
      title: String
    },
    mounted() {
      this.initChart();
    },
    methods: {
      async initChart() {
        let data, timestamps, seriesData;
  
        try {
          if (this.chartType === 'delta' || this.chartType === 'indoor_co2' || this.chartType === 'outdoor_co2' || this.chartType === 'delta_co2') {
            // 新增 delta-co2 数据请求处理
            const response = await axios.get('/api/delta-co2');
            data = response.data;
  
            if (this.chartType === 'indoor_co2') {
              seriesData = data.indoor_co2;
              timestamps = data.timestamps;
            } else if (this.chartType === 'outdoor_co2') {
              seriesData = data.outdoor_co2;
              timestamps = data.timestamps;
            } else if (this.chartType === 'delta_co2') {
              seriesData = data.delta_co2;
              timestamps = data.timestamps;
            }
  
          } else {
            // 原有 /api/data/{chartType} 的请求
            const response = await axios.get(`/api/data/${this.chartType}`);
            data = response.data;
  
            // 检查是否成功获取了数据
            if (!data.timestamps || !data.values) {
              console.error('No data available for chart:', this.chartType);
              return;
            }
  
            timestamps = data.timestamps;
            seriesData = data.values;
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
    height: 100vh; /* 让容器占满整个视口高度 */
  }
  
  .chart {
    width: 600px;
    height: 400px;
  }
  </style>
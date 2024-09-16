<template>
    <div ref="chart" style="width: 600px; height: 400px;"></div>
  </template>
  
  <script>
  import * as echarts from 'echarts';
  import axios from 'axios';

  axios.defaults.baseURL = '/api';
  
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
            console.log('Initializing chart for:', this.chartType); // 确认组件初始化
            try {
                const response = await axios.get(`/api/data/${this.chartType}`);
                console.log('Data received:', response.data); // 确认接收到的数据
                const data = response.data;

                // 检查是否成功获取了数据
                if (!data.timestamps || !data.values) {
                console.error('No data available for chart:', this.chartType);
                return;
                }

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
                    data: data.timestamps
                },
                yAxis: {
                    type: 'value'
                },
                series: [
                    {
                    name: this.title,
                    type: 'line',
                    data: data.values,
                    smooth: true
                    }
                ]
                };

                const chartInstance = echarts.init(this.$refs.chart);
                chartInstance.setOption(option);
                console.log('Chart rendered successfully for:', this.chartType);
            } catch (error) {
                console.error('Error fetching data for chart:', error);
            }
        }

    }
  }
  </script>
  
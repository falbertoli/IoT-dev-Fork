<template>
  <div id="app">
    <h1>Single data source charts (indoor)</h1>
    <!-- ChartComponent 组件保持不变 -->
     <div class="chart-container">
      <ChartComponent chartType="co2" title="CO2 Levels" />
      <ChartComponent chartType="temperature" title="Temperature" />
      <ChartComponent chartType="humidity" title="Humidity" />
      <ChartComponent chartType="pressure" title="Pressure" />
      <ChartComponent chartType="delta_co2" title="Delta CO2 Levels" />
      <ChartComponent chartType="delta_temperature" title="Delta Temperature" />
      <ChartComponent chartType="delta_humidity" title="Delta Humidity" />
      <ChartComponent chartType="delta_pressure" title="Delta Pressure" />
    </div>

      
    <!-- 这个 router-view 会动态加载 Delta 页面等 -->
    <!-- <router-view></router-view> -->

    <h1>Sensor Data Charts</h1>
    <!-- 使用 SelectCharts 组件 -->
    <SelectCharts />
  </div>
</template>

<script>
import ChartComponent from './components/ChartComponent.vue';
import SelectCharts from './components/SelectCharts.vue';

export default {
  components: {
    // ChartComponent
    SelectCharts,
    ChartComponent
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin-top: 40px;
  margin-bottom: 40px;
}
.chart-container {
  display: flex;
  flex-direction: column;
  gap: 80px; /* 为每个图表组件设置20px的间距 */
}

.chart-container > * {
  margin-bottom: 80px; /* 每个图表组件之间的底部间距 */
}


</style>

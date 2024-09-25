<template>
  <div id="app">
    <!-- <h1>Interactive CO2, Temperature, Humidity, Pressure Charts</h1> -->
    <!-- ChartComponent 组件保持不变 -->
    <!-- <ChartComponent chartType="co2" title="CO2 Levels" />
    <ChartComponent chartType="temperature" title="Temperature" />
    <ChartComponent chartType="humidity" title="Humidity" />
    <ChartComponent chartType="pressure" title="Pressure" /> -->

    <!-- 这个 router-view 会动态加载 Delta 页面等 -->
    <!-- <router-view></router-view> -->

    <h1>Sensor Data Charts</h1>
    <!-- 使用 SelectCharts 组件 -->
    <SelectCharts />
  </div>
</template>

<script>
// import ChartComponent from './components/ChartComponent.vue';
import SelectCharts from './components/SelectCharts.vue';

export default {
  components: {
    // ChartComponent
    SelectCharts
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin-top: 40px;
}
</style>

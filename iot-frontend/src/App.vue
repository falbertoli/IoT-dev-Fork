<template>
  <div id="app">
    <h1>Interactive CO2, Temperature, Humidity, Pressure Charts</h1>
    <ChartComponent chartType="co2" title="CO2 Levels" />
    <ChartComponent chartType="temperature" title="Temperature" />
    <ChartComponent chartType="humidity" title="Humidity" />
    <ChartComponent chartType="pressure" title="Pressure" />
  </div>
</template>

<script>
import ChartComponent from './components/ChartComponent.vue';

export default {
  components: {
    ChartComponent
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

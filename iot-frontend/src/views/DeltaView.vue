<template>
  <div id="delta">
    <h1>CO2 Delta (Indoor vs Outdoor)</h1>
    <ChartComponent chartType="indoor_co2" title="Indoor CO2 Levels" />
    <ChartComponent chartType="outdoor_co2" title="Outdoor CO2 Levels" />
    <ChartComponent chartType="delta_co2" title="CO2 Difference (Indoor - Outdoor)" />
  </div>
</template>

<script>
import ChartComponent from '../components/ChartComponent.vue';

export default {
  name: 'DeltaView',  // 将名称修改为 DeltaView
  components: {
    ChartComponent
  }
}
</script>

<style>
#delta {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin-top: 40px;
}
</style>

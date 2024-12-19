<template>
    <div class="home">
      <!-- <h1>Welcome to the Home Page</h1>
      <p>This is the home page of the application. Select options below to view sensor data.</p> -->
      <!-- 引入 SelectCharts 组件 -->
      <SelectCharts />
    </div>
  </template>
  
  <script>
  import SelectCharts from '../components/SelectCharts.vue';
  
  export default {
    name: 'HomeView',
    components: {
      SelectCharts,
    },
  };
  </script>
  
  <style scoped>
  .home {
    text-align: center;
    margin-top: 20px;
  }
  
  .home h1 {
    font-size: 2rem;
    margin-bottom: 10px;
  }
  
  .home p {
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 20px;
  }
  </style>
  
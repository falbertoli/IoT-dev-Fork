const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://172.96.161.120:5000',
        changeOrigin: true,
        // 去掉 pathRewrite，因为 Flask 后端也以 /api 开头
      }
    }
  }
})

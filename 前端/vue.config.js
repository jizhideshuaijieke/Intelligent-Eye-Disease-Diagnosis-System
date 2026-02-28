const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '127.0.0.1',
    port: 7000,
    client: {
      webSocketURL: 'ws://127.0.0.1:7000/ws',
    },
  },
  chainWebpack: (config) => {
    config.plugin('html').tap((args) => {
      args[0].title = '眼底医疗辅助诊断系统';
      return args;
    });
  },
});

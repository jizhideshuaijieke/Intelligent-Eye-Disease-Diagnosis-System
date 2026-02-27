const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
    transpileDependencies: true,
    devServer: {
        port: 7000
    },
    chainWebpack: config => {
        // 链式调用 html 插件来修改标题
        config.plugin('html').tap(args => {
            args[0].title = '眼底医疗辅助诊断系统';
            return args;
        });
    }
});  
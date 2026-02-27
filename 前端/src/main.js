import Vue from 'vue'
import App from './App.vue'
import router from './router'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import { initApiConfig } from './api/config';

Vue.config.productionTip = false
Vue.use(ElementUI);

// 初始化 API 配置后再挂载应用
initApiConfig().then(() => {
  new Vue({
    router,
    render: h => h(App)
  }).$mount('#app')
})

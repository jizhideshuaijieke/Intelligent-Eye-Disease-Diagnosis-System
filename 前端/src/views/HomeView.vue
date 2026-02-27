<template>
  <div id="Home">
    <div class="header">
      <img class="logo-icon" src="@/assets/logo.png">
      <img src="@/assets/generalIcons/visitor.png" alt="User" class="user-icon" @click="goToPersonalInfo">
    </div>
    <div class="toolbar">
      <ul>
        <!-- 使用 v-for 动态生成 li 元素 -->
        <li v-for="(item, index) in toolbarItems" :key="index" :class="{ 'active': $route.path === item.path }">
          <router-link :to="item.path">{{ item.label }}</router-link>
        </li>
      </ul>
    </div>
    <div class="main">
      <keep-alive>
        <router-view></router-view>
      </keep-alive>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeView",
  data() {
    return {
      // 存储 toolbar 菜单项信息的数组
      toolbarItems: [
        { path: '/analyses', label: 'AI分析' },
        { path: '/case', label: '病例管理' },
        { path: '/dataCharts', label: '病理数据可视化统计' },
        { path: '/userInform', label: '个人信息' }
      ]
    };
  },
  mounted() { },
  methods: {
    goToPersonalInfo() {
      if (this.$route.path !== '/userInform') {
        this.$router.push('/userInform')
      }
    }
  }
};
</script>

<style scoped>
#Home {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 30px);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-image: linear-gradient(to right, #ddf1ee, #7ee6c2);
  color: #ffffff;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  margin-right: 10px;
}

.logo-icon {
  height: 40px;
  cursor: pointer;
}

.user-icon {
  height: 30px;
  cursor: pointer;
}

.toolbar {
  height: 35px;
  background-color: #48af9b;
  display: flex;
  padding: 4px 20px 0 20px;
  /* position: relative; */
}

.toolbar ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
}

.toolbar li {
  /* margin: 0 5px; */
  height: 100%;
  display: flex;
  position: relative;
  background-color: transparent;
  transition: all 0.2s ease;
}

.toolbar li a {
  text-decoration: none;
  color: #f4f4f4;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.001s ease, background-color 0.001s ease;
  padding: 8px 20px;
  border-radius: 8px 8px 0 0;
  position: relative;
  z-index: 1;
}

.toolbar li.active a {
  color: #48af9b;
  font-weight: bold;
  background-color: #fff;
  border: 1px solid #48af9b;
  border-bottom: none;
  z-index: 3;
}

.toolbar li.active a::before,
.toolbar li.active a::after {
  content: '';
  position: absolute;
  bottom: 0;
  width: 20px;
  height: 8px;
  background-color: #48af9b;
  z-index: 3;
}

.toolbar li.active a::before {
  left: -20px;
  border-bottom-right-radius: 10px;
  box-shadow: 5px 0 0 0 #fff;
}

.toolbar li.active a::after {
  right: -20px;
  border-bottom-left-radius: 10px;
  box-shadow: -5px 0 0 0 #fff;
}

.main {
  flex: 1;
  overflow: auto;
  background-color: #fff;
  height: calc(100vh - 80px);
  width: 100%;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 2;
}

.el-form-item :deep(.el-form-item__label) {
  color: #d4c7e3 !important;
}
</style>
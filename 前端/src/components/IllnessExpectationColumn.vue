<template>
  <div id="IllnessExpectation">
    <!-- 循环渲染每个进度条项 -->
    <div v-if="progresses.length">
      <div class="progress-item" v-for="(item, index) in progresses" :key="index">
        <!-- 显示疾病名称 -->
        <span class="progress-name">{{ item.name }}</span>
        <div class="progress-container">
          <!-- 进度条 -->
          <div class="progress-bar" :style="{ width: (item.probability * currentRatio * 100) + '%' }">
            <!-- 显示概率百分比 -->
            <span class="progress-percentage">{{ (item.probability * currentRatio * 100).toFixed(2) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    progresses: {
      type: Array,
      default: () => [
        { name: "轻度非增生性病变", probability: 0 },
        { name: "中度非增生性病变", probability: 0 },
        { name: "重度非增生性病变", probability: 0 },
        { name: "增生性病变", probability: 0 },
        { name: "疑似青光眼病变", probability: 0 },
        { name: "早期青光眼", probability: 0 },
        { name: "中期青光眼", probability: 0 },
        { name: "晚期青光眼", probability: 0 },
        { name: "病理性近视", probability: 0 },
        { name: "近视性黄斑病变", probability: 0 },
        { name: "近视性视网膜病变", probability: 0 },
        { name: "近视性视网膜病变", probability: 0 },
        { name: "干性AMD", probability: 0 },
        { name: "湿性AMD", probability: 0 },
        { name: "白内障病变", probability: 0 },
        { name: "疑似白内障病变", probability: 0 },
        { name: "其他", probability: 0 },
        { name: "正常", probability: 0 }
      ]
    }
  },
  data() {
    return {
      currentRatio: 0, // 当前增长比例，范围从 0 到 1
      animationDuration: 100, // 动画总时长，单位为毫秒，这里修改为 1000 让动画更明显
      intervalTime: 50, // 每次更新的时间间隔，单位为毫秒
      totalSteps: null, // 总共的增长步数
      step: 0, // 当前步数
      intervalId: null // 保存定时器 ID
    };
  },
  watch: {
    progresses: {
      handler() {
        // 当 progresses 变化时，重置进度条状态
        this.resetProgress();
        this.Init();
        console.log(this.progresses);
      },
      deep: true // 深度监听 progresses 数组的变化
    }
  },
  mounted() {
    this.resetProgress();
    this.Init();
  },
  methods: {
    resetProgress() {
      // 清除定时器
      if (this.intervalId) {
        clearInterval(this.intervalId);
      }
      // 重置当前步数和比例
      this.step = 0;
      this.currentRatio = 0;
    },
    Init() {
      // 计算总共的增长步数
      this.totalSteps = this.animationDuration / this.intervalTime;
      this.intervalId = setInterval(() => {
        if (this.step < this.totalSteps) {
          this.step++;
          // 计算当前比例
          this.currentRatio = this.step / this.totalSteps;
        } else {
          clearInterval(this.intervalId);
        }
      }, this.intervalTime);
    }
  }
};
</script>

<style scoped>
#IllnessExpectation {
  width: calc(100% - 20px);
  padding: 10px;
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 每个进度条项的样式 */
.progress-item {
  width: 100%;
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.progress-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(5px);
}

/* 疾病名称的样式，设置右对齐 */
.progress-name {
  width: 40%;
  /* 可根据实际情况调整宽度 */
  margin-right: 10px;
  text-align: center;
  color: #2a5e55;
  font-weight: 550;
  /* letter-spacing: 0.5px; */
}

/* 进度条容器的样式 */
.progress-container {
  width: 70%;
  background-color: #ececec;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) inset;
}

/* 进度条的样式 */
.progress-bar {
  height: 15px;
  background: linear-gradient(90deg,
      #aedeaf 0%,
      #95d798 30%,
      #81C784 60%,
      #4CAF50 100%);
  border-radius: 10px;
  width: 100%;
  position: relative;
  text-align: center;
  color: white;
  transition: width 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* 概率百分比的样式 */
.progress-percentage {
  position: absolute;
  top: 50%;
  left: calc(80% + 20px);
  transform: translate(-50%, -50%);
  color: #2a5e55;
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
  /* 可根据需要调整字体大小 */
}
</style>
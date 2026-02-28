<template>
  <div id="IllnessExpectation">
    <div v-if="progresses.length">
      <div v-for="(item, index) in progresses" :key="index" class="progress-item">
        <span class="progress-name">{{ item.name }}</span>
        <div class="progress-container">
          <div class="progress-bar" :style="{ width: `${(item.probability * currentRatio * 100).toFixed(2)}%` }">
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
        { name: "正常", probability: 0 },
        { name: "其他疾病", probability: 0 },
        { name: "病理性近视", probability: 0 },
        { name: "青光眼", probability: 0 },
        { name: "白内障", probability: 0 },
        { name: "糖尿病性视网膜病变", probability: 0 },
        { name: "老年性黄斑部病变", probability: 0 },
        { name: "高血压视网膜病变", probability: 0 },
      ],
    },
  },
  data() {
    return {
      currentRatio: 0,
      animationDuration: 100,
      intervalTime: 50,
      totalSteps: null,
      step: 0,
      intervalId: null,
    };
  },
  watch: {
    progresses: {
      handler() {
        this.resetProgress();
        this.initAnimation();
      },
      deep: true,
    },
  },
  mounted() {
    this.resetProgress();
    this.initAnimation();
  },
  methods: {
    resetProgress() {
      if (this.intervalId) clearInterval(this.intervalId);
      this.step = 0;
      this.currentRatio = 0;
    },
    initAnimation() {
      this.totalSteps = this.animationDuration / this.intervalTime;
      this.intervalId = setInterval(() => {
        if (this.step < this.totalSteps) {
          this.step++;
          this.currentRatio = this.step / this.totalSteps;
        } else {
          clearInterval(this.intervalId);
        }
      }, this.intervalTime);
    },
  },
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

.progress-name {
  width: 40%;
  margin-right: 10px;
  text-align: center;
  color: #2a5e55;
  font-weight: 550;
}

.progress-container {
  width: 70%;
  background-color: #ececec;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) inset;
}

.progress-bar {
  height: 15px;
  background: linear-gradient(90deg, #aedeaf 0%, #95d798 30%, #81c784 60%, #4caf50 100%);
  border-radius: 10px;
  position: relative;
  text-align: center;
  color: white;
  transition: width 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.progress-percentage {
  position: absolute;
  top: 50%;
  left: calc(80% + 20px);
  transform: translate(-50%, -50%);
  color: #2a5e55;
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
}
</style>

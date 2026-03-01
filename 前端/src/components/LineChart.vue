<template>
  <div class="line-chart-wrapper">
    <div ref="lineChart" class="line-chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  props: {
    titleText: {
      type: String,
      default: '折线图示例',
    },
    chartData: {
      type: Array,
      default: () => [],
    },
    xAxisValues: {
      type: Array,
      default: () => [],
    },
    axisTextColor: {
      type: String,
      default: '#333333',
    },
    isGradient: {
      type: Boolean,
      default: true,
    },
    isSmooth: {
      type: Boolean,
      default: false,
    },
    colors: {
      type: Array,
      default: () => ['#84fab0', '#8fd3f4'],
    },
  },
  data() {
    return {
      myChart: null,
    };
  },
  mounted() {
    this.updateChart();
    window.addEventListener('resize', this.handleResize);
  },
  activated() {
    this.$nextTick(() => this.handleResize());
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
    if (this.myChart) {
      this.myChart.dispose();
      this.myChart = null;
    }
  },
  methods: {
    ensureChart() {
      const chartDom = this.$refs.lineChart;
      if (!chartDom) return false;
      if (!this.myChart) {
        this.myChart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
      }
      return true;
    },
    getAreaColor() {
      if (!this.isGradient) return this.colors[0];
      return {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: this.colors[0] },
          { offset: 0.4, color: this.colors[0] },
          { offset: 1, color: this.colors[1] },
        ],
      };
    },
    getChartOption() {
      return {
        title: {
          text: this.titleText,
          textStyle: {
            color: 'rgb(145, 158, 182)',
          },
        },
        xAxis: {
          type: 'category',
          data: this.xAxisValues,
          axisLabel: {
            color: this.axisTextColor,
          },
          axisPointer: {
            show: true,
            label: {
              show: false,
            },
            lineStyle: {
              color: '#666',
              width: 1,
              type: 'solid',
            },
          },
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: this.axisTextColor,
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: '#666666',
            },
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: '#aaaaaa',
            },
          },
        },
        series: [
          {
            data: this.chartData,
            type: 'line',
            color: '#4c6f68',
            label: {
              show: false,
              position: 'top',
              fontSize: 15,
            },
            emphasis: {
              label: {
                show: true,
              },
            },
            areaStyle: {
              color: this.getAreaColor(),
            },
            smooth: this.isSmooth,
          },
        ],
      };
    },
    updateChart() {
      if (!this.ensureChart()) return;
      this.myChart.setOption(this.getChartOption(), true);
    },
    handleResize() {
      if (this.myChart) {
        this.myChart.resize();
      }
    },
  },
  watch: {
    chartData: {
      deep: true,
      handler() {
        this.updateChart();
      },
    },
    xAxisValues: {
      deep: true,
      handler() {
        this.updateChart();
      },
    },
    titleText() {
      this.updateChart();
    },
  },
};
</script>

<style scoped>
.line-chart-wrapper {
  width: 100%;
  height: 100%;
}

.line-chart {
  margin: 20px;
  width: calc(100% - 40px);
  height: calc(100% - 40px);
}
</style>

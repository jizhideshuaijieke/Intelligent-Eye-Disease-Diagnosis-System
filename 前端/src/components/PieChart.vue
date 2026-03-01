<template>
  <div class="pie-chart-wrapper">
    <div ref="pieChart" class="pie-chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  props: {
    titleText: {
      type: String,
      default: '饼状图示例',
    },
    chartData: {
      type: Array,
      default: () => [],
    },
    names: {
      type: Array,
      default: () => [],
    },
    labelColor: {
      type: String,
      default: '#6E7079',
    },
    colorList: {
      type: Array,
      default: () => ['#91C7AE', '#C23531', '#2F4554', '#6AB0B8', '#E98F6F', '#B296A7', '#5F7878'],
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
      const chartDom = this.$refs.pieChart;
      if (!chartDom) return false;
      if (!this.myChart) {
        this.myChart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
      }
      return true;
    },
    getChartOption() {
      const formattedData = this.names.map((name, index) => ({
        name,
        value: Number(this.chartData[index] || 0),
      }));

      return {
        title: {
          text: this.titleText,
          left: 'center',
          textStyle: {
            color: 'rgb(145, 158, 182)',
          },
        },
        tooltip: {
          trigger: 'item',
        },
        legend: {
          orient: 'vertical',
          left: 'right',
          top: 'center',
          textStyle: {
            color: 'rgb(145, 158, 182)',
          },
        },
        series: [
          {
            name: '数据',
            type: 'pie',
            center: ['30%', '50%'],
            color: this.colorList,
            roseType: 'radius',
            data: formattedData,
            label: {
              color: this.labelColor,
              show: false,
            },
            labelLine: {
              show: false,
            },
            itemStyle: {
              borderColor: this.labelColor,
              borderWidth: 0,
            },
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
    names: {
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
.pie-chart-wrapper {
  background-color: rgb(250, 250, 250);
  width: 80%;
  height: calc(100% - 35px);
}

.pie-chart {
  background-color: rgb(250, 250, 250);
  width: calc(100% - 40px);
  height: calc(100% - 40px);
  margin: 20px;
}
</style>

<template>
  <div id="pieChart">
    <div id="PieChart" style="width: calc(100% - 40px); height: calc(100% - 40px)"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";
export default {
  props: {
    titleText: {
      type: String,
      default: "饼状图示例",
    },
    // 接收父组件传递的数据
    chartData: {
      type: Array,
      default: () => [],
    },
    // 接收父组件传递的横坐标值
    names: {
      type: Array,
      default: () => [],
    },
    labelColor: {
      type: String,
      default: "#6E7079"
    },
    colorList: {
      type: Array,
      default: () => [
        "#91C7AE",
        "#C23531",
        "#2F4554",
        "#6AB0B8",
        "#E98F6F",
        "#B296A7",  // 紫灰玫瑰色
        "#5F7878"   // 石板青灰色
      ]
    },
  },
  data() {
    return {
      myChart: null,
    };
  },
  mounted() {
    this.renderPieChart();
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    if (this.myChart) {
      this.myChart.dispose();
    }
  },
  methods: {
    renderPieChart() {
      const chartDom = document.getElementById("PieChart");
      this.myChart = echarts.init(chartDom);

      const formattedData = this.names.map((name, index) => ({
        value: this.chartData[index],
        name: name,
      }));

      const option = {
        title: {
          text: this.titleText,
          left: "center",
          textStyle: {
            color: "rgb(145, 158, 182)",
          },
        },
        tooltip: {
          trigger: "item",
        },
        legend: {
          orient: 'vertical', // 垂直布局
          left: 'right', // 位于图表右侧
          top: 'center', // 垂直居中
          textStyle: {
            color: 'rgb(145, 158, 182)' // 图例文字颜色
          }
        },
        series: [
          {
            name: "数据",
            type: "pie",
            center: ['30%', '50%'],
            color: this.colorList,
            roseType: 'radius',    // 使用radius类型，可减小差异
            data: formattedData,
            label: {
              color: this.labelColor,
              show: false
            },
            labelLine: {
              show: false // 隐藏引导线
            },
            itemStyle: {
              borderColor: this.labelColor, // 边框颜色
              borderWidth: 0 // 将边框宽度设置为0即可去除线框
            }
          },
        ],
      };

      this.myChart.setOption(option);
    },
    handleResize() {
      if (this.myChart) {
        this.myChart.resize();
      }
    },
  },
  watch: {
    chartData: {
      handler() {
        this.renderPieChart();
      },
      deep: true,
      immediate: false
    },
    names: {
      handler() {
        this.renderPieChart();
      },
      deep: true,
      immediate: false
    }
  },
};
</script>

<style scoped>
#pieChart {
  background-color: rgb(250, 250, 250);
  width: 80%;
  height: calc(100% - 35px);
}

#PieChart {
  background-color: rgb(250, 250, 250);
  width: 80%;
  margin: 20px;
}
</style>
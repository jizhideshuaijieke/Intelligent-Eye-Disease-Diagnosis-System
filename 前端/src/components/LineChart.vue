<template>
  <div id="lineChart">
    <div id="LineChart" style="width: calc(100% - 40px); height: calc(100% - 40px)"></div>
  </div>
</template>

<script>
import * as echarts from "echarts";
export default {
  // props为父组件需要传递的参数
  props: {
    titleText: {
      type: String,//要传递的数据类型
      default: "折线图示例",//父组件没有传递时的默认值
    },
    // 接收父组件传递的数据
    chartData: {
      type: Array,
      default: () => [],
    },
    // 接收父组件传递的横坐标值
    xAxisValues: {
      type: Array,
      default: () => [],
    },
    axisTextColor: {
      type: String,
      default: "#333333",
    },
    // 控制是否使用颜色渐变
    isGradient: {
      type: Boolean,
      default: true,
    },
    isSmooth: {
      type: Boolean,
      default: false,
    },
    // 接收父组件传递的渐进颜色
    colors: {
      type: Array,
      default: () => ["#ff0000","#00ff00"],
    },
  },
  data() {
    return {};
  },
  mounted() {
    this.renderLineChart();
  },
  beforeDestroy() {
    // 组件销毁前移除事件监听
    window.removeEventListener("resize", this.handleResize);
    // 销毁 ECharts 实例
    if (this.myChart) {
      this.myChart.dispose();
    }
  },
  methods: {
    renderLineChart() {
      // 获取 DOM 元素
      const chartDom = document.getElementById("LineChart");
      // 初始化 ECharts 实例
      this.myChart = echarts.init(chartDom);
      // 配置图表选项
      const option = this.getChartOption();
      // 使用配置项显示图表
      this.myChart.setOption(option);
      // 监听窗口大小变化事件
      window.addEventListener("resize", this.handleResize);
    },
    handleResize() {
      if (this.myChart) {
        // 窗口大小改变时，重新调整图表大小
        this.myChart.resize();
      }
    },
    getAreaColor() {
      if (this.isGradient) {
        return {
          type: "linear",
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0,
              color: this.colors[0],
            },
            {
              offset: 0.4,
              color: this.colors[0],
            },
            {
              offset: 1,
              color: this.colors[1],
            },
          ],
          global: false,
        };
      }
      return this.colors[0];
    },
    getChartOption() {
      return {
        title: {
          text: this.titleText,
          textStyle: {
            color: "rgb(145, 158, 182)",
          },
        },
        xAxis: {
          type: "category",
          data: this.xAxisValues,
          axisLabel: {
            color: this.axisTextColor,
          },
          axisPointer: {
            show: true,
            label: {
              show: false // 隐藏x轴指示标签
            },
            lineStyle: {
              color: '#666',
              width: 1,
              type: 'solid'
            }
          }
        },
        yAxis: {
          type: "value",
          axisLabel: {
            color: "#333333",
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: "#666666"
            }
          },
          splitLine: {
            show: true,
            lineStyle: {
              color:"#aaaaaa"
            }
          }
        },
        series: [
          {
            data: this.chartData,
            type: "line",
            color: "#4c6f68",
            label: {
              show: false,
              position: 'top',
              textStyle: {
                fontSize: 15
              }
            },
            emphasis: {
              label: {
                show: true
              }
            },
            areaStyle: {
              color: this.getAreaColor(),
            },
            smooth: this.isSmooth,
          },
        ],
      };
    }
  },
  watch:{
    chartData(){
      if (this.myChart) {
        const option = this.getChartOption();
        this.myChart.setOption(option);
      }
    }
  }
};
</script>

<style scoped>
#lineChart {
  width: 100%;
  height: 100%
}

#LineChart {
  margin: 20px;
}
</style>
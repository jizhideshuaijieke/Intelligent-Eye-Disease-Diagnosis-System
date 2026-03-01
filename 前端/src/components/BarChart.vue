<template>
  <div id="chart-container">
    <div ref="barChart" id="BarChart"></div>
    <div id="statistics" v-if="statistics" style="flex: 0 0 30%; margin: 20px 20px 0 0;">
      <div class="button-group">
        <button
          v-for="(button, index) in statisticButtons"
          :key="index"
          :class="{ active: currentStatistics === button.type }"
          @click="showStatistics(button.type)"
        >
          {{ button.label }}
        </button>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th v-if="currentStatistics === 'diseaseTotal' || currentStatistics === 'diseasePercentage'">疾病</th>
              <th v-if="currentStatistics === 'ageGroupTotal'">年龄段</th>
              <th
                v-if="
                  currentStatistics === 'diseaseTotal' ||
                  currentStatistics === 'ageGroupTotal' ||
                  currentStatistics === 'totalCount'
                "
              >
                数量（例）
              </th>
              <th v-if="currentStatistics === 'diseasePercentage'">占比（%）</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="currentStatistics === 'diseaseTotal' || currentStatistics === 'diseasePercentage'">
              <tr v-for="(item, index) in seriesNames" :key="index">
                <td>{{ item }}</td>
                <td v-if="currentStatistics === 'diseaseTotal'">
                  {{ seriesData[index] ? seriesData[index].reduce((sum, val) => sum + val, 0) : 0 }}
                </td>
                <td v-if="currentStatistics === 'diseasePercentage'">{{ getDiseasePercentage(index) }}</td>
              </tr>
              <tr class="total-row">
                <td>总患病数</td>
                <td> {{ getTotalCount() }} </td>
              </tr>
            </template>
            <template v-if="currentStatistics === 'ageGroupTotal'">
              <tr v-for="(ageGroup, index) in xAxisValues" :key="index">
                <td>{{ ageGroup }}</td>
                <td>{{ getAgeGroupTotal(index) }}</td>
              </tr>
              <tr class="total-row">
                <td>总患病数</td>
                <td>{{ getTotalCount() }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts/core';
import { BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent,
} from 'echarts/components';
import { LabelLayout, UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  BarChart,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
  LegendComponent,
]);

export default {
  props: {
    titleText: {
      type: String,
      default: '柱状图示例',
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
      default: '#6E7079',
    },
    seriesNames: {
      type: Array,
      default: () => [],
    },
    seriesData: {
      type: Array,
      default: () => [],
    },
    gradientColorList: {
      type: Array,
      default: () => [
        [
          { offset: 0, color: '#91C7AE' },
          { offset: 1, color: '#91C7AE' },
        ],
        [
          { offset: 0, color: '#C23531' },
          { offset: 1, color: '#C23531' },
        ],
        [
          { offset: 0, color: '#2F4554' },
          { offset: 1, color: '#2F4554' },
        ],
        [
          { offset: 0, color: '#6AB0B8' },
          { offset: 1, color: '#6AB0B8' },
        ],
        [
          { offset: 0, color: '#E98F6F' },
          { offset: 1, color: '#E98F6F' },
        ],
        [
          { offset: 0, color: '#B296A7' },
          { offset: 1, color: '#B296A7' },
        ],
        [
          { offset: 0, color: '#5F7878' },
          { offset: 1, color: '#5F7878' },
        ],
      ],
    },
    gradientDirection: {
      type: Object,
      default: () => ({ x: 0, y: 0, x2: 0, y2: 1 }),
    },
    statistics: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      myChart: null,
      currentStatistics: 'diseaseTotal',
      statisticButtons: [
        { type: 'diseaseTotal', label: '各疾病总计' },
        { type: 'ageGroupTotal', label: '年龄段总患病数' },
        { type: 'diseasePercentage', label: '占比' },
      ],
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
      const chartDom = this.$refs.barChart;
      if (!chartDom) return false;
      if (!this.myChart) {
        this.myChart = echarts.getInstanceByDom(chartDom) || echarts.init(chartDom);
      }
      return true;
    },
    getSeriesOption() {
      return this.seriesNames.map((name, index) => {
        const colorStops = this.gradientColorList[index % this.gradientColorList.length];
        return {
          name,
          type: 'bar',
          data: this.seriesData[index] || [],
          itemStyle: {
            color: {
              type: 'linear',
              ...this.gradientDirection,
              colorStops,
            },
          },
        };
      });
    },
    getChartOption() {
      return {
        title: {
          text: this.titleText,
          textStyle: {
            color: 'rgb(145, 158, 182)',
          },
        },
        tooltip: {},
        legend: {
          data: this.seriesNames,
          bottom: '10px',
          textStyle: {
            color: '#333333',
          },
        },
        xAxis: {
          data: this.xAxisValues,
          axisLabel: {
            color: this.axisTextColor,
          },
        },
        yAxis: {
          axisLabel: {
            color: this.axisTextColor,
          },
          splitLine: {
            lineStyle: {
              color: 'rgb(41, 52, 98)',
            },
          },
        },
        series: this.getSeriesOption(),
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
    getAgeGroupTotal(index) {
      let total = 0;
      this.seriesData.forEach((data) => {
        if (data[index]) {
          total += data[index];
        }
      });
      return total;
    },
    getTotalCount() {
      let total = 0;
      this.seriesData.forEach((data) => {
        total += data.reduce((sum, val) => sum + val, 0);
      });
      return total;
    },
    getDiseasePercentage(index) {
      const diseaseTotal = this.seriesData[index]
        ? this.seriesData[index].reduce((sum, val) => sum + val, 0)
        : 0;
      const totalCount = this.getTotalCount();
      return totalCount > 0 ? ((diseaseTotal / totalCount) * 100).toFixed(2) : 0;
    },
    showStatistics(type) {
      this.currentStatistics = type;
    },
  },
  watch: {
    seriesData: {
      deep: true,
      handler() {
        this.updateChart();
      },
    },
    seriesNames: {
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
#chart-container {
  display: flex;
  width: 100%;
  height: 100%;
}

#BarChart {
  width: 80%;
  margin: 20px 0 10px 20px;
  overflow: hidden;
}

#statistics {
  width: 20%;
  color: #333333;
}

.button-group {
  width: 100%;
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
  margin-bottom: 10px;
}

.button-group button {
  padding: 5px 10px;
  border: none;
  cursor: pointer;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.button-group button.active {
  background-color: #4c6f68;
  color: white;
}

.table-container {
  width: 100%;
  overflow-y: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-height: 120px;
  max-height: 400px;
}

table {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
  background: white;
  font-size: 0.9em;
}

table th {
  background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
  color: #2c3e50;
  font-weight: 600;
  padding: 6px 8px;
  position: sticky;
  top: 0;
  font-size: 12px;
  line-height: 1.2;
}

table td {
  color: #4a4a4a;
  padding: 4px 8px;
  transition: background 0.2s;
  font-size: 11px;
  line-height: 1.3;
}

table tr {
  height: 28px;
}

table tr:nth-child(even) {
  background-color: #f8f9fa;
}

table tr:hover td {
  background-color: #f1f5f9;
}

table th:first-child {
  border-radius: 8px 0 0 0;
}

table th:last-child {
  border-radius: 0 8px 0 0;
}

table th,
table td {
  border: 1px solid #e9ecef;
}

.total-row {
  background-color: #ebfefa !important;
  font-weight: 600;
}

.total-row td {
  border-top: 2px solid #4c6f68 !important;
}
</style>

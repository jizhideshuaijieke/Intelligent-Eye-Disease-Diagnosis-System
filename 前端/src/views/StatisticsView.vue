<template>
  <div id="statistic">
    <div class="top">
      <div class="line">
        <LineChart
          :titleText="lineChartTitle"
          :chartData="lineChartData"
          :xAxisValues="lineXAxisValues"
          :isGradient="isGradient"
          :colors="lineGradientColors"
          :axisTextColor="axisTextColor"
        />
      </div>
      <div class="pie">
        <PieChart
          :titleText="pieChartTitle"
          :chartData="pieChartData"
          :names="pieSeriesNames"
          :labelColor="axisTextColor"
        />
      </div>
    </div>
    <div class="bottom">
      <BarChart
        :titleText="barChartTitle"
        :seriesNames="barSeriesNames"
        :seriesData="barSeriesData"
        :xAxisValues="barXAxisValues"
        :axisTextColor="axisTextColor"
      />
    </div>
  </div>
</template>

<script>
import BarChart from '@/components/BarChart.vue';
import LineChart from '@/components/LineChart.vue';
import PieChart from '@/components/PieChart.vue';
import axios from 'axios';
import { getApiUrl } from '@/api/config';
import {
  DISEASE_KEY_ORDER,
  DISEASE_LABEL_MAP,
  STATS_UPDATED_EVENT,
  readExportedCases,
  buildStatisticsIncrement,
} from '@/utils/statisticsCaseStore';

export default {
  components: {
    BarChart,
    LineChart,
    PieChart,
  },
  data() {
    return {
      lineChartTitle: '不同月份的患者数量',
      lineChartData: [],
      lineXAxisValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
      isGradient: true,
      lineGradientColors: ['rgba(132,250,176,0.1)', 'rgba(143,211,244,0.3)'],

      pieChartTitle: '不同疾病占比情况',
      pieChartData: [],
      pieSeriesNames: [],

      barChartTitle: '不同年龄段的患病情况',
      barSeriesNames: DISEASE_KEY_ORDER.map((key) => DISEASE_LABEL_MAP[key]),
      barSeriesData: [],
      barXAxisValues: ['0~9岁', '10~19岁', '20~34岁', '35~49岁', '50~64岁', '65岁及以上'],

      axisTextColor: '#333333',

      lineBaseData: [],
      pieBaseMap: {},
      barBaseRows: [],
    };
  },
  created() {
    this.loadStatisticsData();
  },
  mounted() {
    window.addEventListener(STATS_UPDATED_EVENT, this.handleStatsUpdated);
  },
  activated() {
    this.mergeWithExportedCases();
  },
  beforeDestroy() {
    window.removeEventListener(STATS_UPDATED_EVENT, this.handleStatsUpdated);
  },
  methods: {
    createEmptyDiseaseMap() {
      return DISEASE_KEY_ORDER.reduce((acc, key) => {
        acc[key] = 0;
        return acc;
      }, {});
    },
    normalizeLineData(raw) {
      const source = Array.isArray(raw) ? raw : [];
      const list = new Array(12).fill(0);
      source.slice(0, 12).forEach((value, index) => {
        list[index] = Number(value || 0);
      });
      return list;
    },
    normalizePieData(raw) {
      const source = raw && typeof raw === 'object' ? raw : {};
      const map = this.createEmptyDiseaseMap();
      DISEASE_KEY_ORDER.forEach((key) => {
        map[key] = Number(source[key] || 0);
      });
      return map;
    },
    normalizeBarRows(raw) {
      const rows = Array.isArray(raw) ? raw : [];
      const normalized = this.barXAxisValues.map((_, rowIndex) => {
        const row = rows[rowIndex] && typeof rows[rowIndex] === 'object' ? rows[rowIndex] : {};
        const next = this.createEmptyDiseaseMap();
        DISEASE_KEY_ORDER.forEach((key) => {
          next[key] = Number(row[key] || 0);
        });
        return next;
      });
      return normalized;
    },
    async loadStatisticsData() {
      await Promise.all([this.loadLineData(), this.loadPieData(), this.loadBarData()]);
      this.mergeWithExportedCases();
    },
    async loadLineData() {
      try {
        const result = await axios.get(getApiUrl('/getPatientsNum'));
        this.lineBaseData = this.normalizeLineData(result?.data?.data);
      } catch (error) {
        console.error('获取患者月度统计失败:', error);
        this.lineBaseData = this.normalizeLineData([]);
      }
    },
    async loadPieData() {
      try {
        const result = await axios.get(getApiUrl('/getDiseasesDistribution'));
        this.pieBaseMap = this.normalizePieData(result?.data?.data);
      } catch (error) {
        console.error('获取疾病占比失败:', error);
        this.pieBaseMap = this.normalizePieData({});
      }
    },
    async loadBarData() {
      try {
        const result = await axios.post(getApiUrl('/getDiseaseConditionByAge'), {
          firstAge: 9,
          secondAge: 19,
          thirdAge: 34,
          forthAge: 49,
          fifthAge: 64,
        });
        this.barBaseRows = this.normalizeBarRows(result?.data?.data);
      } catch (error) {
        console.error('获取年龄段患病统计失败:', error);
        this.barBaseRows = this.normalizeBarRows([]);
      }
    },
    mergeWithExportedCases() {
      if (!this.lineBaseData.length) {
        this.lineChartData = this.normalizeLineData([]);
      }
      if (!Object.keys(this.pieBaseMap).length) {
        this.pieBaseMap = this.normalizePieData({});
      }
      if (!this.barBaseRows.length) {
        this.barBaseRows = this.normalizeBarRows([]);
      }

      const exportedCases = readExportedCases();
      const increments = buildStatisticsIncrement(exportedCases);

      this.lineChartData = this.lineBaseData.map((value, index) => value + Number(increments.monthly[index] || 0));

      this.pieSeriesNames = DISEASE_KEY_ORDER.map((key) => DISEASE_LABEL_MAP[key]);
      this.pieChartData = DISEASE_KEY_ORDER.map(
        (key) => Number(this.pieBaseMap[key] || 0) + Number(increments.disease[key] || 0)
      );

      this.barSeriesNames = DISEASE_KEY_ORDER.map((key) => DISEASE_LABEL_MAP[key]);
      this.barSeriesData = DISEASE_KEY_ORDER.map((key) =>
        this.barXAxisValues.map(
          (_, ageIndex) => Number(this.barBaseRows[ageIndex]?.[key] || 0) + Number(increments.ageDisease[ageIndex]?.[key] || 0)
        )
      );
    },
    handleStatsUpdated() {
      this.mergeWithExportedCases();
    },
  },
};
</script>

<style scoped>
#statistic {
  height: 100%;
  background-color: rgb(250, 250, 250);
}

.top {
  height: calc(50% - 40px);
  display: flex;
}

.line {
  width: 55%;
  margin: 30px 30px 0 30px;
  background-color: rgb(250, 250, 250);
  box-shadow: 12px 12px 12px rgba(0, 0, 0, 0.1), -10px -10px 10px white;
  border-radius: 20px;
}

.pie {
  width: 45%;
  margin: 30px 30px 0 30px;
  background-color: rgb(250, 250, 250);
  box-shadow: 12px 12px 12px rgba(0, 0, 0, 0.1), -10px -10px 10px rgb(255, 255, 255);
  border-radius: 20px;
}

.bottom {
  height: calc(50% - 30px);
  margin: 30px 30px 0 30px;
  background-color: rgb(250, 250, 250);
  box-shadow: 12px 12px 12px rgba(0, 0, 0, 0.1), -10px -10px 10px white;
  border-radius: 20px;
}
</style>

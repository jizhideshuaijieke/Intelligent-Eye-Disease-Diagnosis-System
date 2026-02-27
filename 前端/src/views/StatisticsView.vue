<template>
  <div id="statistic">
    <div class="top">
      <div class="line">
        <LineChart :titleText="LineChartTitle" :chartData="LineChartData" :xAxisValues="LineXAxisValues"
          :isGradient="isGradient" :colors="LineGradientColors" :axisTextColor="axisTextColor" />
      </div>
      <div class="pie">
        <PieChart :titleText="PieChartTitle" :chartData="PieChartData" :names="PieSeriesNames"
          :labelColor="axisTextColor" />
      </div>
    </div>
    <div class="bottom">
      <BarChart :titleText="BarChartTitle" :seriesNames="BarSeriesNames" :seriesData="BarSeriesData"
        :xAxisValues="BarXAxisValues" :axisTextColor="axisTextColor"></BarChart>
    </div>
  </div>
</template>

<script>
import BarChart from "@/components/BarChart.vue";
import LineChart from "@/components/LineChart.vue";
import PieChart from "@/components/PieChart.vue";
import axios from 'axios'
import { getApiUrl } from '@/api/config'
export default {
  components: {
    BarChart,
    LineChart,
    PieChart,
  },
  data() {
    return {
      LineChartTitle: "不同月份的患者数量",
      LineChartData: [],
      // LineChartData: [
      //   450, 250, 155, 348, 192, 687, 485, 665, 985, 475, 342, 258,
      // ],
      isGradient: true,
      LineGradientColors: ["rgba(132,250,176,0.1)", "rgba(143,211,244,0.3)"],
      LineXAxisValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
      PieChartTitle: "不同疾病占比情况",
      PieChartData: [],
      PieSeriesNames: [],
      BarChartTitle: "不同年龄段的患病情况",
      BarSeriesNames: [
        "糖尿病",
        "青光眼",
        "白内障",
        "AMD",
        "高血压",
        "近视",
        "其他疾病或异常",
      ],
      BarChartResult: [],
      BarSeriesData: [
        [12, 25, 30, 18, 22, 28],
        [8, 15, 20, 12, 16, 22],
        [2, 10, 22, 37, 18, 32],
        [15, 27, 44, 25, 25, 44],
        [26, 36, 47, 29, 14, 17],
        [9, 18, 18, 18, 29, 9],
        [44, 15, 9, 37, 36, 23],
      ],
      BarXAxisValues: [
        "0~9岁",
        "10~19岁",
        "20~34岁",
        "35~49岁",
        "50~64岁",
        "65岁及以上",
      ],
      axisTextColor: "#333333",
      nameMapping: {
        diabetes: "糖尿病",
        glaucoma: "青光眼",
        cataract: "白内障",
        AMD: "AMD",
        hypertension: "高血压",
        myopia: "近视",
        others: "其他疾病或异常"
      }
    };
  },
  created() {
    this.processBarData();
    this.processLineData();
    this.processPieData();
  },
  mounted() {

  },
  methods: {
    //获取柱状图数据
    async processBarData() {
      // 获取疾病名称
      this.BarSeriesNames = Object.values(this.nameMapping);
      // 初始化 BarSeriesData 数组
      this.BarSeriesData = Array.from({ length: this.BarSeriesNames.length }, () => []);
      try {
        // 可以将 URL 提取到配置文件中，提高可维护性
        const apiUrl = getApiUrl("/getDiseaseConditionByAge");
        const result = await axios.post(apiUrl, {
          firstAge: 9,
          secondAge: 19,
          thirdAge: 34,
          forthAge: 49,
          fifthAge: 64
        });
        // 检查返回数据的结构
        if (Array.isArray(result.data.data)) {
          this.BarChartResult = result.data.data;
          console.log(this.BarChartResult);

          // 遍历数据，填充 BarSeriesData
          this.BarChartResult.forEach((item) => {
            if (typeof item === 'object' && item !== null) {
              Object.keys(item).forEach((key, index) => {
                if (index < this.BarSeriesData.length) {
                  this.BarSeriesData[index].push(item[key]);
                }
              });
            }
          });
        } else {
          console.log(result.data.data)
          console.error('服务器返回的数据结构不符合预期');
        }
      } catch (error) {
        // 处理请求错误
        console.error('请求数据时发生错误:', error);
      }
    },
    //获取折线图数据
    async processLineData() {
      const lineData = await axios.get(getApiUrl("/getPatientsNum"));
      this.LineChartData = lineData.data.data;
      // console.log(this.LineChartData)
    },
    async processPieData() {
      const result = await axios.get(getApiUrl("/getDiseasesDistribution"));
      const data=result.data.data;
      for (const key in data) {
        if (Object.prototype.hasOwnProperty.call(data, key)) {
          if (this.nameMapping[key]) {
            this.PieSeriesNames.push(this.nameMapping[key]);
            this.PieChartData.push(data[key]);
          }
        }
      }
    }
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
  margin: 30px 30px 0px 30px;
  background-color: rgb(250, 250, 250);
  box-shadow: 12px 12px 12px rgba(0, 0, 0, 0.1),
    -10px -10px 10px white;
  border-radius: 20px;
}

.pie {
  width: 45%;
  margin: 30px 30px 0px 30px;
  background-color: rgb(250, 250, 250);
  box-shadow: 12px 12px 12px rgba(0, 0, 0, 0.1),
    -10px -10px 10px rgb(255, 255, 255);
  border-radius: 20px;
}

.bottom {
  height: calc(50% - 30px);
  margin: 30px 30px 0px 30px;
  background-color: rgb(250, 250, 250);
  box-shadow: 12px 12px 12px rgba(0, 0, 0, 0.1),
    -10px -10px 10px white;
  border-radius: 20px;
}
</style>
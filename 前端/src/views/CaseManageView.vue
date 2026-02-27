<template>
  <div id="case-manage">
    <div class="dialog-container">
      <AIDialog :shortcutButtons="shortcutButtons" :shortcutFunctions="shortcutFunctions" @CaseAnalysis="caseAnalysis"
        @open="open" @close="close" />
    </div>
    <div class="body">
      <!-- 引入对话框子组件 -->
      <div class="case">
        <div class="case-content" :class="{ 'shrink': isOpen }">
          <div class="page-content">
            <el-form :model="form" ref="formRef">
              <el-row>
                <!-- 左半部分表单 -->
                <el-col :span="14" class="left-col">
                  <h2 style="color: #696969;">病历信息</h2>
                  <div class="personal-info-container">
                    <el-form-item label="姓名" prop="name">
                      <el-input v-model="form.name" />
                    </el-form-item>
                    <el-form-item label="年龄" prop="age">
                      <el-input v-model="form.age" @input="handleAgeInput" />
                    </el-form-item>
                    <el-form-item label="性别" prop="gender">
                      <el-input v-model="form.gender" />
                    </el-form-item>
                    <el-form-item label="病历号" prop="caseID">
                      <el-input v-model="form.caseID" />
                    </el-form-item>
                  </div>

                  <div class="eye-data-container">
                    <el-form-item label="左眼视力" prop="leftEyeVision">
                      <el-input v-model="form.leftEyeVision" />
                    </el-form-item>
                    <el-form-item label="右眼视力" prop="rightEyeVision">
                      <el-input v-model="form.rightEyeVision" />
                    </el-form-item>
                    <el-form-item label="左眼眼压(mmHg)" prop="leftEyePressure">
                      <el-input v-model="form.leftEyePressure" />
                    </el-form-item>
                    <el-form-item label="右眼眼压(mmHg)" prop="rightEyePressure">
                      <el-input v-model="form.rightEyePressure" />
                    </el-form-item>
                  </div>

                  <div class="eye-status-container1">
                    <el-form-item label="眼轴长度(mm)" prop="eyeAxisLength">
                      <el-input v-model="form.eyeAxisLength" />
                    </el-form-item>
                    <el-form-item label="角膜曲率(D)" prop="cornealCurvature">
                      <el-input v-model="form.cornealCurvature" />
                    </el-form-item>
                    <el-form-item label="晶状体混浊程度" prop="lensClouding">
                      <el-input v-model="form.lensClouding" />
                    </el-form-item>
                    <el-form-item label="视网膜血管情况" prop="retinalVasculature">
                      <el-input v-model="form.retinalVasculature" />
                    </el-form-item>
                  </div>

                  <div class="eye-status-container2">
                    <el-form-item label="黄斑状况" prop="macularCondition">
                      <el-input v-model="form.macularCondition" />
                    </el-form-item>
                    <el-form-item label="高血压病史" prop="historyOfHypertension">
                      <el-input v-model="form.historyOfHypertension" />
                    </el-form-item>
                    <el-form-item label="糖尿病病史" prop="historyOfDiabetes">
                      <el-input v-model="form.historyOfDiabetes" />
                    </el-form-item>
                    <el-form-item label="眼底病史" prop="historyOfEyeDisease">
                      <el-input v-model="form.historyOfEyeDisease" />
                    </el-form-item>
                  </div>

                  <div class="eye-status-container3">
                    <el-form-item label="家族病史" prop="familyMedicalHistory">
                      <el-input v-model="form.familyMedicalHistory" />
                    </el-form-item>
                    <el-form-item label="临床诊断" prop="clinicalDiagnosis">
                      <el-input v-model="form.clinicalDiagnosis" />
                    </el-form-item>
                  </div>

                </el-col>
                <!-- 右半部分图片和导出 -->
                <el-col :span="10" class="right-col">
                  <div class="image-container">
                    <el-form-item label="左眼图片" class="eyeImageLabel">
                      <image-uploader :isUpload="true" :imageFile="this.form.leftEyeImageBase64"
                        @file-uploaded="LHandleUpload" class="image" />
                    </el-form-item>
                    <el-form-item label="右眼图片" class="eyeImageLabel">
                      <image-uploader :isUpload="true" :imageFile="this.form.rightEyeImageBase64"
                        @file-uploaded="RHandleUpload" class="image" />
                    </el-form-item>
                  </div>
                  <div class="advice-and-export">
                    <el-form-item label="医生建议">
                      <el-input v-model="form.advice" type="textarea" maxlength="300" resize="none"
                        :autosize="{ minRows: 6, maxRows: 6 }" />
                    </el-form-item>
                    <el-form-item>
                      <PdfExportButton @click.native="exportPdf" :form-data="form" />
                    </el-form-item>
                  </div>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ImageUploader from '@/components/ImageUploader.vue';
import AIDialog from '@/components/AIDialog.vue';
import PdfExportButton from '@/components/PdfExportButton.vue';
import axios from 'axios'
import { getApiUrl } from '@/api/config'
export default {
  components: {
    AIDialog, ImageUploader, PdfExportButton
  },
  data() {
    return {
      isOpen: false,
      shortcutButtons: ["病例综合分析"],
      shortcutFunctions: ["caseAnalysis"],//供AIDialog调用获得父组件的信息
      form: {
        name: '',
        age: '',
        gender: '',
        caseID: '',
        leftEyeVision: '',
        rightEyeVision: '',
        leftEyePressure: '',
        rightEyePressure: '',
        eyeAxisLength: '',
        cornealCurvature: '',
        lensClouding: '',
        retinalVasculature: '',
        macularCondition: '',
        historyOfHypertension: '',
        historyOfDiabetes: '',
        historyOfEyeDisease: '',
        familyMedicalHistory: '',
        advice: '',
        diagnoseDoctor: '',
        diagnoseDate: '',
        clinicalDiagnosis: '',
        // leftEyeImage: null,//file
        // rightEyeImage: null,
        leftEyeImageBase64: null,
        rightEyeImageBase64: null,
        // leftOctImage: null,
        // rightOctImage: null,
        leftOctImageBase64: null,
        rightOctImageBase64: null,
      }
    }
  },
  activated() {
    this.InitCase();
    this.InitAdvice();
  },
  // created() {
  //   this.InitCase();
  //   this.InitAdvice();
  // },
  mounted() {

  },
  methods: {
    exportPdf() {
      const now = new Date();
      this.form.diagnoseDate = `${now.getFullYear()}.${(now.getMonth() + 1).toString()}.${now.getDate().toString()}`;
      console.log(this.form.diagnoseDate)
      //医生名字导入PDF
    },
    InitCase() {
      if (this.$route.query && this.$route.query.patientName) {
        this.form.name = this.$route.query.patientName;
      }
      if (this.$route.query && this.$route.query.patientAge) {
        this.form.age = this.$route.query.patientAge;
      }
      if (this.$route.query && this.$route.query.patientSex) {
        this.form.gender = this.$route.query.patientSex;
      }
      if (this.$route.query && this.$route.query.trackingNumber) {
        this.form.caseID = this.$route.query.trackingNumber;
      }
      if (this.$route.query && this.$route.query.imageChoice) {
        const choice = this.$route.query.imageChoice;
        const images = this.$route.query.images;
        console.log(images);
        if (choice === 1) {
          if (images.name == "left") {
            this.form.leftEyeImageBase64 = images.path;
            // this.form.leftEyeImage = this.base64ToFile(images.path, "leftEye");
          }
          else if (images.name == "right") {
            this.form.rightEyeImageBase64 = images.path;
            // this.form.rightEyeImage = this.base64ToFile(images.path, "rightEye");
          }
          else if (images.name == "left-oct") this.form.leftOctImageBase64 = images.path;
          else this.form.rightOctImageBase64 = images.path;
        } else {
          for (let image of images) {
            if (image.name == "left") this.form.leftEyeImageBase64 = image.path;
            else if (image.name == "right") this.form.rightEyeImageBase64 = image.path;
            else if (image.name == "left-oct") this.form.leftOctImageBase64 = image.path;
            else this.form.rightOctImageBase64 = image.path;
          }
        }
      }
    },
    InitAdvice() {
      if (this.$route.query && this.$route.query.inputs) {
        const inputElements = this.$route.query.inputs;
        const validInputElements = Array.isArray(inputElements) ? inputElements : [];
        const groupedData = {
          "左眼": [],
          "右眼": []
        };
        // 对 inputElements 进行分类
        validInputElements.forEach(item => {
          if (item.name === "left" || item.name === "left - oct") {
            groupedData["左眼"] = groupedData["左眼"].concat(item.inputs.map(input => input.value));
          } else if (item.name === "right" || item.name === "right - oct") {
            groupedData["右眼"] = groupedData["右眼"].concat(item.inputs.map(input => input.value));
          }
        });
        // 用于存储最终生成的字符串
        let result = "";
        // 遍历分类后的结果，拼接字符串
        for (const [key, values] of Object.entries(groupedData)) {
          if (values.length > 0) {
            result += `${key}：\n`;
            values.forEach((value, index) => {
              result += `${index + 1}.${value}\n`;
            });
          }
        }
        this.form.advice = result;
      }
    },
    //用于病例分析
    async caseAnalysis() {
      console.log("测试输出")
      //获取该页面病例的信息并返回给对话框，这里返回1
      const data = {
        age: this.form.age,
        gender: this.form.gender,
        outcome: this.form.clinicalDiagnosis
      };
      const response = await axios.post(getApiUrl("/aiSuggestion"), data);
      const result = String(response.data.data);64
      console.log(result);
      return result;
      // return String("针对50岁男性患者晚期青光眼的情况，以下是针对性的诊断建议和治疗流程：\n\n### 1. 治疗建议\n- **眼内压控制**：在晚期青光眼患者中，眼内压的控制是防止进一步视神经损害的关键。可以考虑如下方式：\n  - **药物治疗**：根据患者的个体耐受性及以往用药记录，选择合适的降眼压药物组合。\n  - **激光治疗**：如需要可考虑进行处于相对安全的范围内的激光小梁成形术或激光周边虹膜切开术，以改善房水流出。\n  - **手术治疗**：对于需要手术干预的患者，可以考虑进行青光眼滤过手术（如小梁切除术）或管状阀植入手术。\n\n### 2. 检查计划\n- **眼压监测**：定期监测眼内压，评估治疗效果。\n- **视野检查**：使用电脑视野计定期进行视野检测，记录视野缺损的进展情况。\n- **视神经检查**：使用OCT（光学相干断层扫描）检查视网膜神经纤维层厚度，评估视神经的损伤程度。\n- **房角检查**：使用前房角镜检查房角的开放情况，如有必要进行房水动力学检查。\n\n### 3. 用药建议\n根据患者的具体情况，可以考虑以下几类降眼压药物：\n- **β-adrenergic拮抗剂**（如美托洛尔眼药水）\n- **前列腺素类**（如拉坦前列素眼药水）\n- **碳酸酐酶抑制剂**（如乙酰唑胺口服或磺酰胺眼药水）\n- **α2-adrenergic激动剂**（如布林佐胺眼药水）\n\n在实施药物治疗时，务必注意患者可能的副作用和合并症，同时对药物的相互作用进行评估。如果患者对某些药物有过敏或不良反应，需及时调整用药计划。\n\n### 总结\n鉴于患者已经处于青光眼的晚期阶段，治疗的重点在于降低眼内压，减缓视神经进一步损害的进展。通过综合的检查与个体化的用药计划，可以为患者提供最佳的管理方案。同时，患者的生活方式调整（如合理控制体重、避免剧烈运动等）也对病情有一定影响，建议进行相应的指导和提醒。");
    },
    // 打开操作，将 isOpen 设为 true
    open() {
      this.isOpen = true;
    },
    // 关闭操作，将 isOpen 设为 false
    close() {
      this.isOpen = false;
    },
    LHandleUpload({ file, base64 }) {  // 解构参数获取file和base64
      if (file instanceof File) {
        // this.form.leftEyeImage = file;
        this.form.leftEyeImageBase64 = base64;
      } else {
        this.$message.error('文件格式不正确，请上传图片文件');
      }
    },
    RHandleUpload({ file, base64 }) {
      if (file instanceof File) {
        // this.form.rightEyeImage = file;
        this.form.rightEyeImageBase64 = base64;
      } else {
        this.$message.error('文件格式不正确，请上传图片文件');
      }
    },
    handleAgeInput(value) {//浏览器所有输入的返回都是字符串
      if (!/^(1[0-1][0-9]|120|[1-9][0-9]?)$/.test(value)) {
        this.form.age = value.replace(/[^\d]/g, '')
          .replace(/^0+/, '')
          .slice(0, 3);

        if (this.form.age !== '') {
          this.$nextTick(() => {
            this.$message.warning('请输入1-120之间的有效年龄');
            this.form.age = '';
          });
        }
      }
    }
  }
};
</script>

<style scoped>
#case-manage {
  width: 100%;
  height: 100%;
  /* position: relative; */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.body {
  flex: 1;
  height: 100vh;
  overflow: auto;
  padding: 20px;
  box-sizing: border-box;
  /* position: relative; */
  padding: 30px;
}

.dialog-container {
  width: 400px;
  height: 100%;
  background: transparent;
  /* background: #f8f9fa; */
  /* border-right: 1px solid #e4e7ed; */
  position: relative;
  transition: transform 0.3s ease;
  transform: translateX(0);
  /* z-index: 1000; */
}

.dialog-container.shrink {
  transform: translateX(-400px);
}

.page-content {
  height: calc(100% - 40px);
  width: 100%;
  /* width: auto; */
  padding: 20px 0;
}

.case {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  /* padding: 20px; */
}

.case-content {
  position: absolute;
  top: 10px;
  right: 0;
  left: 2%;
  width: 96%;
  height: calc(100% - 20px);
  /* display: flex;
  justify-content: center;
  align-items: center; */
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  transition: width 0.3s ease, left 0.3s ease;
}

.case-content.shrink {
  left: 400px;
  width: calc(100% - 400px);
}

.el-row {
  gap: 24px;
}

.left-col {
  /* margin: 3rem 0 0 0; */
  height: 100%;
  /* border: 1px solid #65676c; */
  border-radius: 10px;
  /* box-shadow: 0 2px 8px rgba(0,0,0,0.05); */
  background: #f8f9fa;
  padding: 1rem;
}

.personal-info-container {
  display: flex;
  width: 100%;
  gap: 20px;
  /* padding: 0; */
  clear: both;
  border-bottom: 1px solid #65676c;
  padding-bottom: 1rem;
}

.eye-data-container {
  /* margin: 1rem 0 0 0; */
  display: flex;
  width: 100%;
  gap: 20px;
  /* padding: 0; */
  clear: both;
}

.eye-status-container1,
.eye-status-container2,
.eye-status-container3 {
  display: flex;
  width: 100%;
  gap: 20px;
  clear: both;
}

.eye-status-container3 {
  width: 50%;
}

.right-col {
  /* margin: 3rem 0 0 0; */
  height: calc(100% - 40px);
  padding: 7px 20px;
  background: #f8f9fa;
  border-radius: 10px;
  /* box-shadow: 0 2px 8px rgba(0,0,0,0.05); */
}

.image-container {
  /* padding: 5px 0 0 0; */
  display: flex;
  gap: 20px;
  clear: both;
  height: 60%;
}

.advice-and-export {
  height: 40%;
}

.eyeImageLabel {
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.image {
  flex: 1;
  /* display: flex; */
  width: 100%;
  height: 100%;
  aspect-ratio: 1/1;
  /* border: 2px dashed #dcdde1; */
  border-radius: 8px;
  background: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image:hover {
  background: #e8edf3;
  border-color: #6c757d;
}

.el-form-item:deep(.el-textarea__inner),
.el-form-item:deep(.el-input__inner) {
  width: calc(100% - 20px);
  /* background-color: transparent; */
  color: #696969;
  border-color: #696969;
  background: #f8f9fa;
  border-radius: 8px;
  /* border-color: #dcdde1; */
  transition: all 0.3s ease;
}

.el-form-item:deep(.el-textarea__inner:focus),
.el-form-item:deep(.el-input__inner:focus) {
  background: white;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.el-row {
  display: flex;
  gap: 20px;
}

/* 全局表单标签左对齐 */
:deep(.el-form-item__label) {
  text-align: left;
  width: 100%;
  padding-left: 0;
  color: #696969;
  font-size: 0.9em;
  font-weight: 500;
}

:deep(.el-form-item__error) {
  color: #dc3545;
  font-size: 0.9em;
  margin-top: 4px;
}
</style>
<template>
  <div id="case-manage">
    <div class="dialog-container">
      <AIDialog
        :shortcutButtons="shortcutButtons"
        :shortcutFunctions="shortcutFunctions"
        @CaseAnalysis="caseAnalysis"
        @open="open"
        @close="close"
      />
    </div>
    <div class="body">
      <div class="case">
        <div class="case-content" :class="{ shrink: isOpen }">
          <div class="page-content">
            <el-form :model="form" ref="formRef">
              <el-row>
                <el-col :span="14" class="left-col">
                  <h2 style="color: #696969;">病例信息</h2>
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

                <el-col :span="10" class="right-col">
                  <div class="image-container">
                    <el-form-item label="左眼图片" class="eyeImageLabel">
                      <image-uploader
                        :isUpload="true"
                        :imageFile="form.leftEyeImageBase64"
                        @file-uploaded="LHandleUpload"
                        class="image"
                      />
                    </el-form-item>
                    <el-form-item label="右眼图片" class="eyeImageLabel">
                      <image-uploader
                        :isUpload="true"
                        :imageFile="form.rightEyeImageBase64"
                        @file-uploaded="RHandleUpload"
                        class="image"
                      />
                    </el-form-item>
                  </div>
                  <div class="advice-and-export">
                    <el-form-item label="医生建议">
                      <el-input
                        v-model="form.advice"
                        type="textarea"
                        maxlength="300"
                        resize="none"
                        :autosize="{ minRows: 6, maxRows: 6 }"
                      />
                    </el-form-item>
                    <el-form-item>
                      <PdfExportButton
                        :form-data="form"
                        @before-export="prepareExport"
                        @export-success="handleExportSuccess"
                        @export-error="handleExportError"
                      />
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
import axios from 'axios';

import AIDialog from '@/components/AIDialog.vue';
import ImageUploader from '@/components/ImageUploader.vue';
import PdfExportButton from '@/components/PdfExportButton.vue';
import { getApiUrl } from '@/api/config';
import { STATS_UPDATED_EVENT, clearPendingCaseMeta, getPendingCaseMeta } from '@/utils/statisticsCaseStore';

export default {
  components: {
    AIDialog,
    ImageUploader,
    PdfExportButton,
  },
  data() {
    return {
      isOpen: false,
      pendingCaseMeta: null,
      shortcutButtons: ['病例综合分析'],
      shortcutFunctions: ['caseAnalysis'],
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
        leftEyeImageBase64: null,
        rightEyeImageBase64: null,
        leftOctImageBase64: null,
        rightOctImageBase64: null,
      },
    };
  },
  activated() {
    this.initCase();
    this.initAdvice();
    this.syncPendingCaseMeta();
  },
  methods: {
    parseQueryValue(value) {
      if (value == null) return null;
      if (typeof value === 'object') return value;
      if (typeof value !== 'string') return value;
      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    },
    prepareExport() {
      const now = new Date();
      this.form.diagnoseDate = `${now.getFullYear()}.${String(now.getMonth() + 1).padStart(2, '0')}.${String(
        now.getDate()
      ).padStart(2, '0')}`;
    },
    syncPendingCaseMeta() {
      const meta = getPendingCaseMeta();
      const createdAt = Number(meta?.createdAt || 0);
      const expired = !createdAt || Date.now() - createdAt > 2 * 60 * 60 * 1000;
      if (expired) {
        clearPendingCaseMeta();
        this.pendingCaseMeta = null;
        return;
      }
      this.pendingCaseMeta = meta;
    },
    async handleExportSuccess() {
      if (!String(this.form.caseID || '').trim()) {
        this.$message.warning('请先填写病历号，再导出并写入数据库。');
        return;
      }
      if (!String(this.form.name || '').trim()) {
        this.$message.warning('请先填写患者姓名，再导出并写入数据库。');
        return;
      }

      const diagnosisName = String(this.pendingCaseMeta?.topDiagnosisName || '').trim();
      const outcome = String(this.form.clinicalDiagnosis || diagnosisName).trim();
      const age = this.form.age === '' ? null : Number(this.form.age);

      try {
        const response = await axios.post(getApiUrl('/saveCaseHistory'), {
          name: this.form.name,
          gender: this.form.gender,
          age: Number.isFinite(age) ? age : null,
          reportId: this.form.caseID,
          time: this.form.diagnoseDate,
          outcome,
          leftPhoto: this.form.leftEyeImageBase64,
          rightPhoto: this.form.rightEyeImageBase64,
          aiSuggestion: this.form.advice,
        });

        const payload = response?.data || {};
        if (payload.code !== 1) {
          throw new Error(payload.message || '病例写入失败');
        }

        clearPendingCaseMeta();
        this.pendingCaseMeta = null;
        window.dispatchEvent(new CustomEvent(STATS_UPDATED_EVENT));
        this.$message.success('病例已写入数据库并同步到统计图表。');
      } catch (error) {
        this.$message.error(error?.message || '病例写入数据库失败');
      }
    },
    handleExportError() {
      // Ignore export errors here.
    },
    initCase() {
      const query = this.$route.query || {};

      if (query.patientName) this.form.name = query.patientName;
      if (query.patientAge != null) this.form.age = query.patientAge;
      if (query.patientSex) this.form.gender = query.patientSex;
      if (query.trackingNumber) this.form.caseID = query.trackingNumber;

      const choiceRaw = this.parseQueryValue(query.imageChoice);
      const choice = Number(choiceRaw);
      const imagesRaw = this.parseQueryValue(query.images);

      if (!imagesRaw) return;

      const assignByName = (image) => {
        if (!image || typeof image !== 'object') return;
        if (image.name === 'left') this.form.leftEyeImageBase64 = image.path || null;
        else if (image.name === 'right') this.form.rightEyeImageBase64 = image.path || null;
        else if (image.name === 'left-oct') this.form.leftOctImageBase64 = image.path || null;
        else if (image.name === 'right-oct') this.form.rightOctImageBase64 = image.path || null;
      };

      if (choice === 1 && !Array.isArray(imagesRaw)) {
        assignByName(imagesRaw);
        return;
      }

      if (Array.isArray(imagesRaw)) {
        imagesRaw.forEach(assignByName);
      }
    },
    initAdvice() {
      const query = this.$route.query || {};
      const inputElements = this.parseQueryValue(query.inputs);
      const validInputElements = Array.isArray(inputElements) ? inputElements : [];

      const groupedData = {
        左眼: [],
        右眼: [],
      };

      validInputElements.forEach((item) => {
        const name = String(item?.name || '');
        const inputs = Array.isArray(item?.inputs) ? item.inputs : [];
        const values = inputs.map((input) => String(input?.value || '').trim()).filter(Boolean);

        if (name === 'left' || name === 'left-oct' || name === 'left - oct') {
          groupedData.左眼 = groupedData.左眼.concat(values);
        } else if (name === 'right' || name === 'right-oct' || name === 'right - oct') {
          groupedData.右眼 = groupedData.右眼.concat(values);
        }
      });

      let result = '';
      Object.entries(groupedData).forEach(([eye, values]) => {
        if (!values.length) return;
        result += `${eye}：\n`;
        values.forEach((value, index) => {
          result += `${index + 1}. ${value}\n`;
        });
      });

      if (result.trim()) {
        this.form.advice = result;
      }
    },
    async caseAnalysis() {
      const data = {
        age: this.form.age,
        gender: this.form.gender,
        outcome: this.form.clinicalDiagnosis,
      };
      const response = await axios.post(getApiUrl('/aiSuggestion'), data);
      return String(response?.data?.data || '');
    },
    open() {
      this.isOpen = true;
    },
    close() {
      this.isOpen = false;
    },
    LHandleUpload({ file, base64 }) {
      if (file instanceof File) {
        this.form.leftEyeImageBase64 = base64;
      } else {
        this.$message.error('文件格式不正确，请上传图片文件');
      }
    },
    RHandleUpload({ file, base64 }) {
      if (file instanceof File) {
        this.form.rightEyeImageBase64 = base64;
      } else {
        this.$message.error('文件格式不正确，请上传图片文件');
      }
    },
    handleAgeInput(value) {
      const text = String(value || '');
      if (/^(1[0-1][0-9]|120|[1-9][0-9]?)$/.test(text)) return;

      this.form.age = text.replace(/[^\d]/g, '').replace(/^0+/, '').slice(0, 3);
      if (this.form.age === '') return;

      this.$nextTick(() => {
        this.$message.warning('请输入 1-120 之间的有效年龄');
        this.form.age = '';
      });
    },
  },
};
</script>

<style scoped>
#case-manage {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.body {
  flex: 1;
  height: 100vh;
  overflow: auto;
  box-sizing: border-box;
  padding: 30px;
}

.dialog-container {
  width: 400px;
  height: 100%;
  background: transparent;
  position: relative;
  transition: transform 0.3s ease;
  transform: translateX(0);
}

.dialog-container.shrink {
  transform: translateX(-400px);
}

.page-content {
  height: calc(100% - 40px);
  width: 100%;
  padding: 20px 0;
}

.case {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.case-content {
  position: absolute;
  top: 10px;
  right: 0;
  left: 2%;
  width: 96%;
  height: calc(100% - 20px);
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
  display: flex;
  gap: 20px;
}

.left-col {
  height: 100%;
  border-radius: 10px;
  background: #f8f9fa;
  padding: 1rem;
}

.personal-info-container {
  display: flex;
  width: 100%;
  gap: 20px;
  clear: both;
  border-bottom: 1px solid #65676c;
  padding-bottom: 1rem;
}

.eye-data-container {
  display: flex;
  width: 100%;
  gap: 20px;
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
  height: calc(100% - 40px);
  padding: 7px 20px;
  background: #f8f9fa;
  border-radius: 10px;
}

.image-container {
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
  width: 100%;
  height: 100%;
  aspect-ratio: 1/1;
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
  color: #696969;
  border-color: #696969;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.el-form-item:deep(.el-textarea__inner:focus),
.el-form-item:deep(.el-input__inner:focus) {
  background: white;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

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

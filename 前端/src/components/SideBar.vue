<template>
  <div id="sideBar">
    <div class="basic-information-container">
      <div v-if="!isBulkUpload" class="patient-information">
        <div class="patient-row">
          <span class="inform-unit">
            <img src="@/assets/generalIcons/visitor.png" width="24" />
          </span>
          <span class="inform-unit">{{ patientName }}</span>
          <span class="inform-unit">{{ patientSex }}</span>
          <span class="inform-unit">{{ `${patientAge}岁` }}</span>
        </div>
        <div class="patient-row">检查单号：{{ trackingNumber }}</div>
      </div>
      <div v-else class="title">批量上传图像</div>
    </div>

    <hr />

    <div class="thumbnail">
      <template v-if="imageSrc">
        <img
          :src="imageSrc"
          class="thumbnail-image selected-thumbnail"
          alt="Thumbnail"
          @click="handleThumbnailClick(0)"
        />
      </template>
      <template v-else-if="images.length > 0">
        <img
          v-for="(image, index) in images"
          :key="index"
          :src="image.path"
          class="thumbnail-image"
          :class="{ 'selected-thumbnail': currentImageIndex === index }"
          alt="Thumbnail"
          @click="handleThumbnailClick(index)"
        />
      </template>
      <template v-else-if="imagePaths.length > 0">
        <img
          v-for="(imagePath, index) in imagePaths"
          :key="index"
          :src="imagePath.path"
          class="thumbnail-image"
          :class="{ 'selected-thumbnail': currentImageIndex === index + images.length }"
          alt="Thumbnail"
          @click="handleThumbnailClick(index)"
        />
      </template>
    </div>

    <div class="exchange-tools">
      <button class="tool-button" :class="{ 'button-active': toolChoose === 1 }" @click="handleExchangeTool(1)">
        <i class="el-icon-edit big-icon"></i>
        诊断建议
      </button>
      <button
        v-if="imageResults.length !== 0 && imageResults[currentImageIndex] && imageResults[currentImageIndex].probabilities"
        class="tool-button"
        :class="{ 'button-active': toolChoose === 2 }"
        @click="handleExchangeTool(2)"
      >
        <i class="el-icon-s-data big-icon"></i>
        AI检测结果
      </button>
    </div>

    <div v-if="toolChoose === 1" class="input-container" :class="{ exInput: isBulkUpload }">
      <div
        v-for="(inputWrapper, inputIndex) in currentInputList"
        :key="inputIndex"
        class="input-wrapper"
      >
        <span class="input-index">{{ `${inputIndex + 1}.` }}</span>
        <input class="tech-input" placeholder="输入与病灶矩形相关信息" v-model="inputWrapper.value" />
        <span class="delete-btn" @click="handleDelete(currentImageIndex, inputIndex)">×</span>
      </div>
    </div>

    <div v-if="toolChoose === 2" class="ai-suggest" :class="{ 'exAI-suggest': isBulkUpload }">
      <StatusBar :progresses="imageResults[currentImageIndex].probabilities" />
    </div>

    <div v-if="!isBulkUpload" class="report-container">
      <hr />
      <div class="generate-report">
        <button class="report-button" @click="generateReport">
          <i v-if="!isLoading" class="el-icon-document big-icon"></i>
          {{ buttonName }}
          <span v-if="isLoading" class="loading-spinner"></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import StatusBar from '@/components/IllnessExpectationColumn.vue';
import { MessageBox } from 'element-ui';
import { collectTopDiagnosisFromResults, savePendingCaseMeta } from '@/utils/statisticsCaseStore';

export default {
  components: { StatusBar },
  props: {
    width: {
      type: Number,
      default: 400,
    },
    height: {
      type: Number,
      default: 800,
    },
    patientName: {
      type: String,
      default: '测试患者',
    },
    patientSex: {
      type: String,
      default: '男',
    },
    patientAge: {
      type: Number,
      default: 0,
    },
    trackingNumber: {
      type: String,
      default: '1111111111',
    },
    images: {
      type: Array,
      default: () => [],
    },
    imagePaths: {
      type: Array,
      default: () => [],
    },
    imageSrc: {
      type: String,
      default: '',
    },
    imageResults: {
      type: Array,
      default: () => [],
    },
    imageChoice: {
      type: Number,
      default: 0,
    },
    currentImageIndex: {
      type: Number,
      default: 0,
    },
    isBulkUpload: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isLoading: false,
      buttonName: '导入至病例',
      selectedImages: '',
      inputElements: [],
      toolChoose: 1,
    };
  },
  computed: {
    currentInputList() {
      const current = this.inputElements[this.currentImageIndex];
      return Array.isArray(current?.inputs) ? current.inputs : [];
    },
  },
  created() {
    this.updateInputElementsLength();
  },
  methods: {
    updateInputElementsLength() {
      let source = [];
      if (this.imageSrc) {
        source = [{ name: 'single-image' }];
        this.selectedImages = this.imageSrc;
      } else if (this.images.length > 0) {
        source = this.images;
        this.selectedImages = this.images;
      } else if (this.imagePaths.length > 0) {
        source = this.imagePaths;
        this.selectedImages = this.imagePaths;
      } else {
        source = [];
      }

      const next = source.map((item, index) => {
        const prev = this.inputElements[index];
        return {
          name: item?.name || `image-${index + 1}`,
          inputs: Array.isArray(prev?.inputs) ? prev.inputs : [],
        };
      });

      this.inputElements = next;
    },
    addInputElement(imageIndex) {
      if (!this.inputElements[imageIndex]) {
        this.$set(this.inputElements, imageIndex, {
          name: `image-${imageIndex + 1}`,
          inputs: [],
        });
      }
      const list = this.inputElements[imageIndex].inputs;
      list.push({ index: list.length + 1, value: '' });
    },
    handleDelete(imageIndex, inputIndex) {
      if (!this.inputElements[imageIndex]) return;
      const list = this.inputElements[imageIndex].inputs;
      if (!Array.isArray(list) || list.length === 0) return;
      list.splice(inputIndex, 1);
      this.$emit('rectangleRemoved', imageIndex, inputIndex);
    },
    handleThumbnailClick(index) {
      if (index === this.currentImageIndex) return;
      this.$emit('imageIndexChanged', index);
    },
    handleTabClick(index) {
      this.$emit('imageIndexChanged', index);
    },
    handleExchangeTool(index) {
      this.toolChoose = index;
    },
    getAnnotationCount() {
      return (this.inputElements || []).reduce((sum, item) => {
        const inputs = Array.isArray(item?.inputs) ? item.inputs : [];
        const validCount = inputs.filter((input) => String(input?.value || '').trim().length > 0).length;
        return sum + validCount;
      }, 0);
    },
    generateReport() {
      const topDiagnosis = collectTopDiagnosisFromResults(this.imageResults);
      const annotationCount = this.getAnnotationCount();

      savePendingCaseMeta({
        topDiagnosisName: topDiagnosis?.name || '',
        topDiagnosisProbability: topDiagnosis?.probability || 0,
        annotationCount,
      });

      this.isLoading = true;
      this.buttonName = '正在导入';

      setTimeout(() => {
        this.buttonName = '导入至病例';
        this.$emit('setGenerateStatus', true);
        this.$confirm('导入成功，即将跳转到病例页。', '提示', {
          showCancelButton: false,
          showConfirmButton: false,
          type: 'success',
        }).catch(() => {});

        this.isLoading = false;
        setTimeout(() => {
          MessageBox.close();
          const params = {
            images: this.selectedImages,
            imageChoice: this.imageChoice,
            inputs: this.inputElements,
            patientName: this.patientName,
            patientAge: this.patientAge,
            patientSex: this.patientSex,
            trackingNumber: this.trackingNumber,
          };
          this.$router.push({
            path: '/case',
            query: params,
          });
        }, 2000);
      }, 1000);
    },
  },
  watch: {
    images: {
      deep: true,
      handler() {
        this.updateInputElementsLength();
      },
    },
    imagePaths: {
      deep: true,
      handler() {
        this.updateInputElementsLength();
      },
    },
  },
};
</script>

<style scoped>
#sideBar {
  width: calc(100% - 1px);
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, #1a3b5c 0%, #2c5e80 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(15px);
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.3), inset 0 0 20px rgba(0, 0, 0, 0.5);
}

.basic-information-container {
  min-height: 45px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 20px;
  margin: 0 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #16304c 0%, #244e6c 100%);
}

.patient-information {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
}

.patient-row {
  margin-bottom: 6px;
}

.inform-unit {
  margin-right: 8px;
  vertical-align: middle;
}

.title {
  width: 100%;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #00b8d4;
}

.thumbnail {
  width: calc(100% - 40px);
  height: calc(30% - 20px);
  display: flex;
  flex-wrap: wrap;
  padding: 10px;
  border-radius: 12px;
  margin: 0 10px;
}

.thumbnail-image {
  width: 27%;
  height: 38%;
  margin: 8px;
  cursor: pointer;
  border-radius: 10px;
  object-fit: contain;
  background: #000;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.thumbnail-image:hover {
  transform: scale(1.06);
}

.selected-thumbnail {
  border: 1.5px solid rgb(38, 173, 187);
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(0, 184, 212, 0.4);
}

.exchange-tools {
  width: calc(100% - 20px);
  height: calc(8vh - 10px);
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 15px 10px;
  border-radius: 20px;
  background: linear-gradient(135deg, #16304c 0%, #244e6c 100%);
}

.tool-button {
  width: 40%;
  height: 60%;
  border: 1px solid rgb(38, 173, 187);
  font-size: 14px;
  font-weight: 600;
  color: rgb(38, 173, 187);
  cursor: pointer;
  margin: 0 12px;
  border-radius: 20px;
  background: transparent;
}

.tool-button:hover {
  background-color: rgba(38, 173, 187, 0.3);
}

.button-active {
  color: white;
  background: linear-gradient(135deg, #00b8d4 0%, #0096a8 100%);
}

.big-icon {
  font-size: 16px;
  margin-right: 6px;
}

.input-container {
  width: calc(100% - 40px);
  height: calc(35% - 10px);
  overflow: auto;
  border-radius: 12px;
  margin: 0 10px;
  padding: 10px;
}

.exInput {
  height: calc(40% + 10px);
}

.input-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 10px;
}

.input-index {
  min-width: 24px;
  color: #fff;
  text-align: center;
}

.tech-input {
  width: calc(100% - 60px);
  padding: 6px 8px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #1e3858 0%, #2a5072 100%);
  color: #ecf0f1;
}

.delete-btn {
  margin-left: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgb(235, 109, 109);
  color: white;
  font-size: 18px;
  text-align: center;
  line-height: 20px;
  cursor: pointer;
}

.ai-suggest {
  width: calc(100% - 50px);
  height: calc(35% - 20px);
  border-radius: 12px;
  margin: 15px 10px;
  padding: 15px;
  overflow: auto;
}

.exAI-suggest {
  height: 40%;
}

.report-container {
  position: absolute;
  width: 100%;
  height: 50px;
  bottom: 20px;
}

.generate-report {
  display: flex;
  justify-content: center;
}

.report-button {
  width: 80%;
  height: 40px;
  border-radius: 25px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  background: linear-gradient(135deg, #00b8d4 0%, #0096a8 100%);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
  margin-left: 10px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>

<template>
  <div id="sideBar">
    <div class="basic-information-container">
      <div v-if="!isBulkUpload" class="patient-information">
        <div>
          <span class="inform-unit">
            <img src="@/assets/generalIcons/visitor.png" width="30">
          </span>
          <span class="inform-unit">{{ patientName }}</span>
          <span class="inform-unit">{{ patientSex }}</span>
          <span class="inform-unit">{{ String(patientAge) + "岁" }}</span>
        </div>
        <div>
          检查单号：{{ trackingNumber }}
        </div>
      </div>
      <div v-else class="title">
        批量上传图像
      </div>
    </div>
    <hr>
    <div class="thumbnail">
      <!-- 根据条件显示二进制图片或路径图片 -->
      <template v-if="imageSrc">
        <img :src="imageSrc" class="thumbnail-image selected-thumbnail" alt="Thumbnail"
          @click="handleThumbnailClick(0)">
      </template>
      <template v-else-if="images.length > 0">
        <!-- 这一行需要修改image为对象 -->
        <img v-for="(image, index) in images" :key="index" :src="image.path" class="thumbnail-image"
          :class="{ 'selected-thumbnail': currentImageIndex === index }" alt="Thumbnail"
          @click="handleThumbnailClick(index)">
      </template>
      <template v-else-if="imagePaths.length > 0">
        <img v-for="(imagePath, index) in imagePaths" :key="index" :src="imagePath.path" class="thumbnail-image"
          :class="{ 'selected-thumbnail': currentImageIndex === index + images.length }" alt="Thumbnail"
          @click="handleThumbnailClick(index)">
      </template>
    </div>
    <div class="exchange-tools">
      <button class="tool-button" :class="{ 'button-active': toolChoose === 1 }" @click="handleExchangeTool(1)">
        <i class="el-icon-edit big-icon"></i>
        诊断建议
      </button>
      <button v-if="imageResults.length!==0 && imageResults[currentImageIndex].probabilities" class="tool-button"
        :class="{ 'button-active': toolChoose === 2 }" @click="handleExchangeTool(2)">
        <i class="el-icon-s-data big-icon"></i>
        AI检测结果
      </button>
    </div>
    <div v-if="toolChoose === 1" class="input-container" :class="{ 'exInput': isBulkUpload }">
      <!-- 根据当前显示图片的索引显示对应的输入框 -->
      <div v-for="(inputWrapper, inputIndex) in inputElements[currentImageIndex].inputs" :key="inputIndex"
        class="input-wrapper">
        <span class="input-index">{{ String(Number(inputIndex) + 1) }}.</span>
        <input class="tech-input" :placeholder="'输入与矩形相关信息'" v-model="inputWrapper.value" />
        <!-- 仅在输入框个数大于 1 时显示删除按钮 -->
        <span class="delete-btn" @click="handleDelete(currentImageIndex, inputIndex)">×</span>
      </div>
    </div>
    <div v-if="toolChoose === 2" class="ai-suggest" :class="{ 'exAI-suggest': isBulkUpload }">
      <StatusBar :progresses="imageResults[currentImageIndex].probabilities"></StatusBar>
    </div>
    <div v-if="!isBulkUpload" class="report-container">
      <hr>
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
import StatusBar from '@/components/IllnessExpectationColumn.vue'
import { MessageBox } from 'element-ui';
export default {
  components: { StatusBar },
  props: {
    width: {
      type: Number,
      default: 400
    },
    height: {
      type: Number,
      default: 800
    },
    patientName: {
      type: String,
      default: "测试患者"
    },
    patientSex: {
      type: String,
      default: "男"
    },
    patientAge: {
      type: Number,
      default: 0
    },
    trackingNumber: {
      type: String,
      default: "1111111111"
    },
    images: {
      type: Array,
      default: () => []
    },
    imagePaths: {
      type: Array,
      default: () => []
    },
    imageSrc: {
      type: String,
      default: ""
    },
    imageResults: {
      type: Array,
      default: () => []
    },
    imageChoice: {
      type: Number,
      default: 0
    },
    currentImageIndex: {
      type: Number,
      default: 0
    },
    isBulkUpload: {
      type: Boolean,
      default: false
    }
    // probabilities: {
    //   type: Array,
    //   default: () => []
    // }
  },
  data() {
    return {
      isLoading: false, // 加载状态变量
      // imageName: ["图片1", "图片2", "图片3"],
      buttonName: "导入至病例",
      selectedImages: "",
      inputElements: [],
      toolChoose: 1,
      // tabs: []
    };
  },
  created() {
    this.updateInputElementsLength();
  },
  methods: {
    updateInputElementsLength() {
      let imageCount = 0;
      if (this.imageSrc) {
        imageCount = 1;
        this.selectedImages = this.imageSrc;
        this.inputElements = Array.from({ length: imageCount }, () => []);
      } else if (this.images.length > 0) {
        imageCount = this.images.length;
        this.selectedImages = this.images;
        this.inputElements = this.images.map(item => ({
          name: item.name,
          inputs: []
        }));
      } else if (this.imagePaths.length > 0) {
        imageCount = this.imagePaths.length;
        this.selectedImages = this.imagePaths;
        this.inputElements = this.imagePaths.map(item => ({
          name: item.name,
          inputs: []
        }));
      }
      // this.inputElements = Array.from({ length: imageCount }, () => []);
      // this.tabs = Array.from({ length: imageCount }, (_, index) => `图片${index + 1}`);
    },
    addInputElement(imageIndex) {
      const newIndex = this.inputElements[imageIndex].inputs.length + 1;
      const inputWrapper = {
        index: newIndex,
        value: ''
      };
      this.inputElements[imageIndex].inputs.push(inputWrapper);
    },
    handleDelete(imageIndex, inputIndex) {
      if (this.inputElements[imageIndex].inputs.length > 0) {
        this.inputElements[imageIndex].inputs.splice(inputIndex, 1);
        this.$emit('rectangleRemoved', imageIndex, inputIndex);
      }
    },
    // imageUrl(image) {
    //   return URL.createObjectURL(new Blob([image]));
    // },
    handleThumbnailClick(index) {
      if (index == this.currentImageIndex) return;
      this.$emit('imageIndexChanged', index);
    },
    handleTabClick(index) {
      this.$emit('imageIndexChanged', index);
    },
    handleExchangeTool(index) {
      this.toolChoose = index;
    },
    generateReport() {
      this.isLoading = true; // 开始加载，显示加载动画
      this.buttonName = "正在导入";
      // 模拟异步操作，比如发送请求
      setTimeout(() => {
        this.buttonName = "导入至病例";
        this.$emit('setGenerateStatus', true);
        this.$confirm('导入成功！即将进行页面跳转...', '提示', {
          showCancelButton: false,
          showConfirmButton: false,
          type: 'success'
        }).catch(() => { });
        this.isLoading = false; // 加载完成，隐藏加载动画
        setTimeout(() => {
          MessageBox.close();
          const params = {
            images: this.selectedImages,
            imageChoice: this.imageChoice,
            inputs: this.inputElements,
            patientName: this.patientName,
            patientAge: this.patientAge,
            patientSex: this.patientSex,
            trackingNumber: this.trackingNumber
          }
          this.$router.push({
            path: '/case',
            query: params
          });
        }, 2000);
      }, 1000);
    }
  },
  watch: {
    // 监听 images 和 imagePaths 的变化
    images: {
      deep: true,
      handler() {
        this.updateInputElementsLength();
      }
    },
    imagePaths: {
      deep: true,
      handler() {
        this.updateInputElementsLength();
      }
    }
  }
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
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.3),
    inset 0 0 20px rgba(0, 0, 0, 0.5);
}

#sideBar::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg,
      transparent 50%,
      rgba(255, 255, 255, 0.02) 50%);
  pointer-events: none;
}

.basic-information-container {
  height: 45px;
  display: flex;
  /* padding: 20px; */
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  padding: 15px 25px;
  border-radius: 15px;
  margin: 0 10px;
  background: linear-gradient(135deg, #16304c 0%, #244e6c 100%);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.basic-information-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, transparent 45%, rgba(255, 255, 255, 0.03) 55%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.basic-information-container:hover::before {
  opacity: 1;
}

.patient-information {
  color: rgb(255, 255, 255, 0.8);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.inform-unit {
  margin: 0px 10px 0px 10px;
  vertical-align: middle;
}

.title {
  width: 100%;
  margin-top: 10px;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #00b8d4;
  background-clip: text;
  letter-spacing: 2px;
  text-shadow: 2px 2px 8px rgba(0, 200, 220, 0.2),
    0 0 15px rgba(0, 200, 220, 0.1);
  margin-bottom: 10px;
}

.thumbnail {
  width: calc(100% - 40px);
  height: calc(30% - 20px);
  display: flex;
  flex-wrap: wrap;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 15px;
  margin: 0 10px;
}

.thumbnail-image {
  width: 27%;
  height: 38%;
  margin: 8px;
  cursor: pointer;
  /* border: 2px solid rgb(38, 173, 187); */
  border-radius: 10px;
  border: none;
  object-fit: contain;
  /* border-color: rgba(255,255,255,0.1); */
  /* background-color: black;*/
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  background: black;
  /* 设置鼠标指针为手指形状 */
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.thumbnail-image:hover {
  transform: scale(1.1);
  box-shadow: 0 0 30px rgba(0, 184, 212, 0.2);
  border-color: #00b8d4;
}

.selected-thumbnail {
  /* transform: scale(1.1);
  box-shadow: 0 0 20px rgb(38, 173, 187); */
  border: 1.5px solid rgb(38, 173, 187);
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(0, 184, 212, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.exchange-tools {
  width: calc(100% - 20px);
  height: calc(8vh - 10px);
  border-top: 1px solid rgb(238, 238, 238);
  /* background-color: rgb(15, 26, 72, 0.6); */
  display: flex;
  justify-content: center;
  align-items: center;
  /* border-radius: 20px; */
  margin: 15px 10px;
  border-radius: 25px;
  background: linear-gradient(135deg, #16304c 0%, #244e6c 100%);
  /* margin: 0 20px; */
}

.tool-button {
  width: 40%;
  height: 60%;
  /* background-color: transparent; */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  border: 1px solid rgb(38, 173, 187);
  font-size: 15px;
  font-weight: bold;
  color: rgb(38, 173, 187);
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin: 0 15px;
  border-radius: 20px;
}

.tool-button:hover {
  background-color: rgb(38, 173, 187, 0.5)
}

.big-icon {
  font-size: 18px;
  margin-right: 8px;
}

.button-active {
  /* background-color: rgb(38, 173, 187);*/
  color: white;
  background: linear-gradient(135deg, #00b8d4 0%, #0096a8 100%);
  box-shadow: 0 3px 10px rgba(0, 200, 220, 0.3),
    inset 0 2px 0 rgba(255, 255, 255, 0.1);
}

.input-container {
  width: calc(100% - 40px);
  height: calc(35% - 10px);
  display: inline-block;
  vertical-align: top;
  overflow: scroll;
  scrollbar-width: none;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 15px;
  margin: 0 10px;
  padding: 10px;
}

.exInput {
  height: calc(40% + 10px);
}

.input-wrapper {
  position: relative;
  /* margin-bottom: 5px; */
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 10px;
}

.input-wrapper input {
  width: calc(100% - 50px);
  margin-left: 5px;
}

.input-wrapper .delete-btn {
  display: inline-block;
  margin-left: 10px;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  background-color: rgb(235, 109, 109);
  color: white;
  font-size: 20px;
  text-align: center;
  line-height: 22px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.delete-btn:hover {
  background-color: #c62828;
  transform: scale(1.1);
}

.input-index {
  min-width: 20px;
  text-align: center;
  font-size: 18px;
  color: white;
  text-shadow: 2px 2px 8px rgba(0, 200, 220, 0.2);
}

.tech-input {
  position: relative;
  width: 100%;
  padding: 5px 0px 5px 5px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #1e3858 0%, #2a5072 100%);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  /* box-shadow: 0 0 15px rgba(0, 255, 255, 0.3), inset 0 0 10px rgba(0, 255, 255, 0.1); */
  font-size: 16px;
  color: #ecf0f1;
  overflow: hidden;
}

.tech-input::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  opacity: 0;
  transition: opacity 0.5s ease;
}

.tech-input:focus::before {
  opacity: 1;
}

.tech-input:focus {
  box-shadow: 0 0 25px rgba(0, 255, 255, 0.5), inset 0 0 15px rgba(0, 255, 255, 0.2);
}

.ai-suggest {
  width: calc(100% - 50px);
  height: calc(35% - 20px);
  /* padding: 20px 20px 0 20px; */
  background: rgba(255, 255, 255, 0.02);
  border-radius: 15px;
  margin: 15px 10px;
  padding: 15px;
  color: #e0ecff;
  overflow: scroll;
  scrollbar-width: none;
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
  font-size: 18px;
  font-weight: 600;
  /* background-color: rgba(38, 173, 187); */
  background: linear-gradient(135deg, #00b8d4 0%, #0096a8 100%);
  box-shadow: 0 3px 10px rgba(0, 200, 220, 0.3),
    inset 0 2px 0 rgba(255, 255, 255, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-button:hover {
  background: linear-gradient(135deg, #00a8c2 0%, #008599 100%);
}

/* .report-button:hover {
  background-color: #0056b3;
} */

.loading-spinner {
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
  margin-left: 10px;
  box-sizing: border-box;
  /* 确保边框包含在宽高内 */
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
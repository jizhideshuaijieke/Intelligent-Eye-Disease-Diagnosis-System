<template>
  <div id="ImageObserve">
    <button v-if="isBulkUpload && !isBulkContainerOpen" @click="toggleBulkContainer" class="toggle-button">
      <span class="button-text">
        <i class="el-icon-arrow-right"></i>
      </span>
    </button>
    <div v-if="isBulkUpload" class="left-bulkBar" :class="{ 'slide-in': isBulkContainerOpen }">
      <button @click="toggleBulkContainer" class="close-button">关闭</button>
      <div class="bulk-container" v-if="isBulkUpload">
        <div class="thumbnail">
          <div v-for="(group, groupIndex) in images" :key="groupIndex">
            <div class="image-row" :class="{ 'selected-row': selectedGroup === groupIndex }"
              @click="handleExchangeImages(groupIndex)">
              <img v-for="(image, index) in group" :key="index" :src="image.path" class="thumbnail-image"
                alt="Thumbnail">
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="right-canvas" :style="{ width: isBulkContainerOpen ? `calc(100% - 20%)` : '100%' }"
      :class="{ 'slide-right': isBulkContainerOpen }">
      <ImageRectangleDrawer :images="isBulkUpload ? images[selectedGroup] : images" :imageSrc="imageSrc"
        :imagePaths="imagePaths" :imageResults="isBulkUpload ? imageResults[selectedGroup] : imageResults"
        :patientName="patientName" :patientAge="patientAge" :patientSex="patientSex" :trackingNumber="trackingNumber"
        :canvasWidth="imgWidth" :isBulkUpload="isBulkUpload" :canvasHeight="imgHeight"
        @rectangleAdded="onRectangleAdded" @rectangleRemoved="onRectangleRemoved" />
    </div>
  </div>
</template>

<script>
import ImageRectangleDrawer from "@/components/ImageRectangleDrawer.vue";
export default {
  components: {
    ImageRectangleDrawer,
  },
  data() {
    return {
      imgWidth: 0,
      imgHeight: 0,
      images: [],
      imageResults: [],
      imageSrc: "",
      imagePaths: [],
      selectedGroup: 0,
      isBulkUpload: false,
      isBulkContainerOpen: false,
      patientName: "",
      patientAge: 0,
      patientSex: "",
      trackingNumber: ""
    };
  },
  created() {
    this.InitBulkUploadStatus();
    this.InitImagePaths();
    this.InitImageResults();
    this.InitBasicInformation()
  },
  mounted() {
    // 在组件挂载时添加 resize 事件监听器
    window.addEventListener('resize', this.handleWindowResize);
  },
  beforeDestroy() {
    // 在组件销毁前移除 resize 事件监听器，避免内存泄漏
    window.removeEventListener('resize', this.handleWindowResize);
  },
  methods: {
    InitBasicInformation() {
      if (this.$route.query && this.$route.query.patientName) {
        this.patientName = this.$route.query.patientName;
      }
      if (this.$route.query && this.$route.query.patientAge) {
        this.patientAge = Number(this.$route.query.patientAge);
      }
      if (this.$route.query && this.$route.query.patientSex) {
        this.patientSex = this.$route.query.patientSex;
      }
      if (this.$route.query && this.$route.query.trackingNumber) {
        this.trackingNumber = this.$route.query.trackingNumber;
      }
    },
    InitImagePaths() {
      if (this.$route.query && this.$route.query.imagePaths) {
        this.imagePaths = this.$route.query.imagePaths;
      }
      if (this.$route.query && this.$route.query.imageSrc) {
        this.imageSrc = this.$route.query.imageSrc;
      }
      if (this.$route.query && this.$route.query.images) {
        this.images = this.$route.query.images;
      }
    },
    // 检测是否是批量上传
    InitBulkUploadStatus() {
      if (this.$route.query && this.$route.query.isBulkUpload) {
        if (this.$route.query.isBulkUpload === "true")
          this.isBulkUpload = true;
      }
      console.log(this.isBulkUpload);
      this.handleWindowResize()
    },
    InitImageResults() {
      if (this.$route.query && this.$route.query.imageResults) {
        this.imageResults = this.$route.query.imageResults;
      }
      console.log(this.imageResults);
    },
    handleExchangeImages(index) {
      this.selectedGroup = index;
      // 添加选中行样式控制
      const rows = document.querySelectorAll('.image-row');
      rows.forEach(row => row.classList.remove('selected-row'));
      rows[index].classList.add('selected-row');
    },
    computedCanvasWidth(mul, bulk) {
      this.imgWidth = window.innerWidth * 0.7 - Number(bulk) * 200;
    },
    computedCanvasHeight() {
      this.imgHeight = window.innerHeight - 30;
    },
    onRectangleAdded(rectangle) {
      console.log("这是父组件的矩形框添加:", rectangle);
      // 可以在这里添加父组件的处理逻辑，如保存矩形框信息
    },
    onRectangleRemoved(rectangle) {
      console.log("这是父组件的矩形框删除:", rectangle);
      // 可以在这里添加父组件的处理逻辑，如更新数据等
    },
    // 根据是否是批量上传动态获取视窗大小
    handleWindowResize() {
      this.computedCanvasWidth(this.isBulkUpload, this.isBulkContainerOpen);
      this.computedCanvasHeight();
      // console.log(this.imgWidth + "+" + this.imgHeight);
    },
    toggleBulkContainer() {
      this.isBulkContainerOpen = !this.isBulkContainerOpen;
      this.handleWindowResize();
    }
  },
};
</script>

<style scoped>
#ImageObserve {
  width: 100%;
  height: calc(100% - 20px);
  display: flex;
  position: relative;
  overflow-y: hidden;
}

.toggle-button {
  position: fixed;
  width: 20px;
  top: 100px;
  padding: 15px 15px;
  background-color: #333333;
  color: #ffffff;
  border: none;
  border-top-right-radius: 15px;
  border-bottom-right-radius: 15px;
  font-size: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 999;
}

.toggle-button:hover {
  background-color: #444444;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  transform: translateY(-1px);
}

.button-text {
  margin-right: 2px;
}

.left-bulkBar {
  width: 20%;
  height: calc(100% - 20px);
  position: fixed;
  left: -20%;
  background-color: #1a1a1a;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
  transition: left 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 1000;
}

.left-bulkBar.slide-in {
  left: 0;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 0;
  background: none;
  border: none;
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: 500;
  cursor: pointer;
  z-index: 1001;
}

.bulk-container {
  width: calc(100% - 40px);
  height: calc(100% - 40px);
  /* 占满父容器高度 */
  padding: 20px;
  background-color: #1a1a1a;
  overflow-y: auto;
  /* 添加滚动条 */
}

.thumbnail {
  height: calc(100% - 30px);
  gap: 15px;
  padding: 15px;
  background-color: #2c2c2c;
  border-radius: 10px;
}

.image-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 15px;
  padding: 12px;
  background-color: #333333;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.image-row:hover {
  transform: translateY(-5px);
}

.image-row.selected-row {
  background-color: #356ba4;
  transform: translateY(0) scale(1.02);
  box-shadow: 0 0 15px rgba(74, 144, 226, 0.4);
}

.thumbnail-image {
  width: 20%;
  height: 20%;
  /* object-fit: cover; */
  border-radius: 6px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.thumbnail-image:hover {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.thumbnail-image.selected {
  border-color: #4a90e2;
  transform: scale(1.03);
  box-shadow: 0 0 15px rgba(74, 144, 226, 0.4);
}

/* 辅助元素样式 */
.group-label {
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
}

.right-canvas {
  width: 100%;
  height: 100%;
  transition: width 0.3s ease, margin-left 0.3s ease;
  margin-left: 0;
}

.right-canvas.slide-right {
  margin-left: 20%;
}
</style>
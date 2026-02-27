<template>
  <div id="imageAnalysis" v-loading.lock="isLoading" element-loading-text="正在分析">
    <div class="submit-and-results">
      <div class="submit">
        <!-- 单张点击上传 -->
        <div v-if="!isBulkUpload" class="single-submit">
          <div class="eyeGround-group">
            <div class="title">眼底图像</div>
            <div class="imageContainer">
              <div v-for="index in [1, 2]" :key="index" class="images single-image">
                <div v-if="hasAnalysis && hasSingleUpload[index]" class="imageSelector">
                  <button @click="ImageUploaderButton(index)" :class="{ active: imageKind[index] }">
                    <span>{{ imageKind[index] ? "显示原图" : "显示增强" }}</span>
                  </button>
                </div>
                <ImageUploader v-show="!imageKind[index]" :isUpload="true"
                  @file-uploaded="(payload) => imageUpload(payload, index)" />
                <ImageUploader v-if="hasAnalysis && imageKind[index]" :imageFile="enforceImageResults[index]" />
              </div>
            </div>
          </div>
          <!-- 第二组：后两个下标 -->
          <div class="oct-group">
            <div class="title">OCT图像</div>
            <div class="imageContainer">
              <div v-for="index in [3, 4]" :key="index" class="images single-image">
                <!-- <div v-if="hasAnalysis && hasSingleUpload[index]" class="imageSelector">
                  <button @click="ImageUploaderButton(index)" :class="{ active: imageKind[index] }">
                    <span>{{ imageKind[index] ? "显示原图" : "显示增强" }}</span>
                  </button>
                </div> -->
                <ImageUploader :isUpload="true" @file-uploaded="(payload) => imageUpload(payload, index)" />
                <!-- <ImageUploader v-if="hasAnalysis && imageKind[index]" :imageFile="enforceImageResults[index]" /> -->
              </div>
            </div>
          </div>
        </div>
        <div v-else class="batch-submit">
          <!--批量上传预览-->
          <div class="title">批量上传</div>
          <div class="bulkImageContainer">
            <div v-if="!isUploadImg" class="bulk-upload">
              <input type="file" webkitdirectory directory multiple @change="startBulkUpload" ref="folderInput">
            </div>
            <div v-if="isUploadImg" class="bulk-images">
              <div class="group-number">当前组号: {{ selectedGroup + 1 }}</div>
              <div class="arrow left-arrow" @click="prevPage" v-if="selectedGroup != 0">&lt;</div>
              <div class="imageContainer">
                <div v-for="(image, index) of groupedImages[selectedGroup]" :key="index" class="images group-image">
                  <div v-if="hasAnalysis && groupedImagesResult[selectedGroup][index].enhanced_image"
                    class="imageSelector">
                    <button @click="ImageUploaderButton(index)"
                      :class="{ active: groupImageKind[selectedGroup][index] }">
                      <span>{{ groupImageKind[selectedGroup][index] ? "显示原图" : "显示增强" }}</span>
                    </button>
                  </div>
                  <ImageUploader
                    :imageFile="groupImageKind[selectedGroup][index] ? groupedImagesResult[selectedGroup][index].enhanced_image : image.path" />
                </div>
              </div>
              <div class="arrow right-arrow" @click="nextPage" v-if="selectedGroup != totalGroup - 1">&gt;</div>
              <div class="reUpload-icon" @click="reBulkUpload" title="重新上传">
                <i class="el-icon-refresh-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="results">
        <!-- 单张结果图 -->
        <div v-if="!isBulkUpload" class="single-results">
          <div class="eyeGround-results">
            <div class="title">眼底结果图像</div>
            <div v-if="hasAnalysis" class="imageContainer">
              <div v-for="(image, index) of filteredEyeGroundImageResult" :key="index" class="images single-result">
                <ImageUploader :imageFile="image.path" />
              </div>
            </div>
          </div>
          <div class="oct-results">
            <div class="title">OCT分层图像</div>
            <div v-if="hasAnalysis" class="imageContainer">
              <div v-for="(image, index) of filteredOCTImageResult" :key="index" class="images single-result">
                <ImageUploader :imageFile="image.path" />
              </div>
            </div>
          </div>
        </div>
        <!--批量上传结果图-->
        <div v-else class="bulk-results">
          <div class="title">结果图</div>
          <div v-if="hasAnalysis" class="imageContainer">
            <div v-for="(image, index) of groupedImagesResult[selectedGroup]" :key="index" class="images group-image">
              <ImageUploader :imageFile="image.path" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="states">
      <div class="setUp">
        <div class="mode">
          <!-- <button @click="$refs.folderInput.click(), setBulkStatus()"> 批量上传 </button> -->
          <button @click="setBulkStatus()" :class="{ active: !isBulkUpload }" :disabled="!isBulkUpload">
            <i class="el-icon-tickets big-icon"></i>
            单例上传
          </button>
          <button @click="setBulkStatus()" :class="{ active: isBulkUpload }" :disabled="isBulkUpload">
            <i class="el-icon-folder-opened big-icon"></i>
            批量上传
          </button>
        </div>
        <div class="tools">
          <button @click="observationMode">
            <i class="el-icon-edit-outline big-icon"></i>
            观察模式
          </button>
          <button @click="getResults">
            <i class="el-icon-search big-icon"></i>
            {{ setUpName }}
          </button>
        </div>
        <!-- 隐藏的原生文件输入 -->
        <!-- <input type="file" webkitdirectory directory multiple @change="startBulkUpload" hidden ref="folderInput"> -->
      </div>
      <div class="probabilities">
        <div v-if="hasAnalysis" class="probability-buttons">
          <button v-for="(image, index) in isBulkUpload ? filteredGroupedImages[selectedGroup] : filteredImageResult"
            :key="index" @click="showProbabilities(index)" :class="{ active: activeIndex === index }">
            图像{{ index + 1 }}的概率
          </button>
        </div>
        <!-- 根据当前激活的索引展示对应的 probabilities -->
        <div class="progress">
          <StatusBar
            :progresses="hasAnalysis ? (isBulkUpload ? filteredGroupedImages[selectedGroup] : filteredImageResult)[activeIndex].probabilities : undefined">
          </StatusBar>
        </div>
      </div>
      <!-- <div v-else class="progresses-empty">
        启动AI分析以获取结果
      </div> -->
    </div>
  </div>
</template>

<script>
import StatusBar from '@/components/IllnessExpectationColumn.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import axios from 'axios'
import { getApiUrl } from '@/api/config'

export default {
  name: 'ImageAnalysisView', // 添加组件名称
  components: {
    StatusBar,
    ImageUploader,
  },
  computed: {
    filteredEyeGroundImageResult() {
      return this.imageResult.filter(image => image.name === 'left' || image.name === 'right');
    },
    filteredOCTImageResult() {
      return this.imageResult.filter(image => image.name === 'left-oct' || image.name === 'right-oct');
    },
    filteredImageResult() {
      return this.imageResult.filter(image => image.name != 'left-oct' && image.name != 'right-oct');
    },
    filteredGroupedImages() {
      return this.groupedImagesResult.map(subArray => {
        return subArray.filter(image => image.name !== 'left-oct' && image.name !== 'right-oct');
      });
    }
  },
  data() {
    return {
      // singleButtonName: ["左眼眼底图", "右眼眼底图", "左眼OCT图像", "右眼OCT图像"],
      patientName: "张三",
      patientAge: 21,
      patientSex: "男",
      trackingNumber: "HOSP20250324A001",
      imageKind: {//四种按钮的bool，点击显示对应的组件  //10:38 
        1: false,
        2: false,
        3: false,
        4: false
      },
      hasSingleUpload: {
        1: false,
        2: false,
        3: false,
        4: false
      },
      groupImageKind: [[]],
      imageFundus: [],//两种眼底图
      imageOCT: [],//两种OCT图像
      hasCommitted: false,//是否已上传    //10:38
      hasAnalysis: false,//是否已分析
      // hasBulkUpload: false,
      // initialImages: [],
      // resultImages: [],
      setUpName: "启动AI分析",
      activeIndex: 0, //分析部分的按钮选择的下标
      // probabilities: [],
      isLoading: false,
      images: [],
      groupedImages: [], //分组之后的图片,用于分组显示
      imageResult: [],//单张结果图
      enforceImageResults: {
        1: null,
        2: null,
        3: null,
        4: null,
      },
      //单张增强图结果
      groupedImagesResult: [],//分组后的结果图
      groupedEnforceImagesResults: [],//分组后的增强图
      // imageSrc: "",
      // imagePaths: [],
      // imageResult: [{
      //   name: "oct",
      //   path: base64,
      //   hasLegend: true,
      //   legends: [
      //     { "color": "#FF5733", "name": "活力橙" },
      //     { "color": "#33FF57", "name": "清新绿" },
      //     { "color": "#5733FF", "name": "梦幻紫" },
      //     { "color": "#FFFF33", "name": "灿烂黄" },
      //     { "color": "#33FFFF", "name": "澄澈蓝" },
      //     { "color": "#FF33C1", "name": "浪漫粉" },
      //     { "color": "#9933FF", "name": "深邃靛" },
      //     { "color": "#33FF99", "name": "盎然碧" },
      //     { "color": "#FF9933", "name": "暖阳橘" },
      //     { "color": "#3399FF", "name": "宁静海蓝" }
      //   ]
      // }],
      // uploadedImg: [],
      isUploadImg: false,
      isBulkUpload: false,  //是否为批量上传
      selectedGroup: 0,
      totalGroup: 0,
      // currentPage: 0//批量上传时的预览页码
    };
  },
  methods: {
    //批量上传左切预览图
    prevPage() {
      if (this.selectedGroup > 0) {
        this.selectedGroup--;
      }
      this.activeIndex = 0;
    },
    //批量上传右切预览图
    nextPage() {
      if (this.selectedGroup < this.totalGroup) {
        this.selectedGroup++;
      }
      this.activeIndex = 0;
    },
    //点击切换上传模式
    setBulkStatus() {
      const resetData = () => {
        this.isUploadImg = false;
        if (this.images.length > 0) this.images = [];
        if (this.groupedImages.length > 0) this.groupedImages = [];
        this.hasAnalysis = false;
        if (this.imageResult.length > 0) {
          this.imageResult = [];
          this.enforceImageResults = {
            1: null,
            2: null,
            3: null,
            4: null,
          };
        }
        if (this.groupedImagesResult.length > 0) {
          this.groupedImagesResult = [];
          this.groupedEnforceImagesResults = [];
        }
        this.activeIndex = 0;
        this.setUpName = "启动AI分析";
      };
      if (this.isUploadImg) {
        this.$confirm('你已上传过图片,切换模式将不保留已上传图片, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.isBulkUpload = !this.isBulkUpload;
          resetData();
        }).catch(() => { });
      } else {
        this.isBulkUpload = !this.isBulkUpload;
        resetData();
      }
    },
    //多张上传
    async startBulkUpload(event) {
      if (event.target.files.length === 0) {
        console.log('用户点击了取消');
        return;
      }
      // this.isBulkUpload = true;
      // this.hasBulkUpload = true;
      this.isUploadImg = true;
      const files = Array.from(event.target.files);
      const folderStructure = {};
      files.forEach(file => {
        const pathParts = file.webkitRelativePath.split('/');
        if (pathParts.length <= 2) {
          this.fff = file;//无效语句，如果不是子文件夹文件or空文件夹，就不放入数组
        }
        else {
          const folderName = pathParts[1];//子文件夹名称
          //索引作为名称,如果遍历到新文件夹，创建一个存储数组
          if (!folderStructure[folderName]) {
            folderStructure[folderName] = [];
          }
          folderStructure[folderName].push(file);
        }
      });
      let idx = 1;
      if (Object.entries(folderStructure).length) {//有新数据才置空
        this.images = [];
        this.imageResult = [];
        // this.hasCommitted = false;
        this.selectedGroup = 0;
      }
      //每一个子文件夹的图片
      for (const [folderName, files] of Object.entries(folderStructure)) {
        this.folderName = folderName;
        for (const file of files) {
          const base64 = await this.readFileAsBase64(file);
          const matches = base64.match(/^data:(.+);base64,(.+)$/);
          const imageType = matches[1];
          console.log(imageType);
          if (imageType === 'image/png')
            this.images.push({
              index: idx,
              name: "left-oct",
              path: base64,
              probabilities: [],
              hasLegend: true,
              legends: [
                { "color": "#FFFF00", "name": "神经纤维层" },
                { "color": "#00FFFF", "name": "神经节细胞层+内丛状层" },
                { "color": "#FFA500", "name": "内核层" },
                { "color": "#0000FF", "name": "外丛状层" },
                { "color": "#FF0000", "name": "外核层" },
                { "color": "#00FF00", "name": "椭圆体带" },
                { "color": "#0000FF", "name": "视网膜色素上皮层" },
                { "color": "#A52A2A", "name": "脉络膜" }
              ]
            });
          else {
            this.images.push({
              index: idx,
              name: "",
              path: base64,
              probabilities: []
            });
          }
        }
        idx++;
      }
      // 根据索引排序
      this.images.sort((a, b) => a.index - b.index);
      this.groupedImages = this.getGroupedImages(this.images);
      // this.groupImageKind = this.getGroupedImages(this.images).map(group => group.map(() => false));
      this.groupImageKind = this.getImageKindByImages(this.groupedImages);
      // console.log(this.groupImageKind);
      this.totalGroup = this.groupedImages.length;
    },
    getGroupedImages(images) {
      const groups = {};
      images.forEach((image) => {
        if (!groups[image.index]) {
          groups[image.index] = [];
        }
        groups[image.index].push(image);
      });
      return Object.values(groups);
    },
    getImageKindByImages(images) {
      return images.map(item => {
        if (Array.isArray(item)) {
          return this.getImageKindByImages(item);
        }
        return false;
      });
    },
    // 文件转Base64
    async readFileAsBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
      });
    },
    ImageUploaderButton(type) {//10:38
      if (!this.isBulkUpload) this.imageKind[type] = !this.imageKind[type];
      else this.$set(this.groupImageKind[this.selectedGroup], type, !this.groupImageKind[this.selectedGroup][type]);
    },
    imageUpload(payload, type) {
      const newItem = {
        index: type,
        name: "",
        path: payload.base64,
        probabilities: [],
        hasLegend: type <= 2 ? false : true,
        legends: type <= 2 ? [] : [
          { "color": "#FFFF00", "name": "神经纤维层" },
          { "color": "#00FFFF", "name": "神经节细胞层+内丛状层" },
          { "color": "#FFA500", "name": "内核层" },
          { "color": "#0000FF", "name": "外丛状层" },
          { "color": "#FF0000", "name": "外核层" },
          { "color": "#00FF00", "name": "椭圆体带" },
          { "color": "#0000FF", "name": "视网膜色素上皮层" },
          { "color": "#A52A2A", "name": "脉络膜" }
        ]
      };
      switch (type) {
        case 1:
          newItem.name = "left";
          if (this.hasSingleUpload[1]) {
            const indexToReplace = this.imageFundus.findIndex(item => item.index === 1);
            if (indexToReplace !== -1) {
              this.imageFundus.splice(indexToReplace, 1, newItem);
            }
          } else {
            this.imageFundus.push(newItem);
          }
          this.hasSingleUpload[1] = true;
          break;
        case 2:
          newItem.name = "right";
          if (this.hasSingleUpload[2]) {
            const indexToReplace = this.imageFundus.findIndex(item => item.index === 2);
            if (indexToReplace !== -1) {
              this.imageFundus.splice(indexToReplace, 1, newItem);
            }
          } else {
            this.imageFundus.push(newItem);
          }
          this.hasSingleUpload[2] = true;
          break;
        case 3:
          newItem.name = "left-oct";
          if (this.hasSingleUpload[3]) {
            const indexToReplace = this.imageOCT.findIndex(item => item.index === 3);
            if (indexToReplace !== -1) {
              this.imageOCT.splice(indexToReplace, 1, newItem);
            }
          } else {
            this.imageOCT.push(newItem);
          }
          this.hasSingleUpload[3] = true;
          break;
        case 4:
          newItem.name = "right-oct";
          if (this.hasSingleUpload[4]) {
            const indexToReplace = this.imageOCT.findIndex(item => item.index === 4);
            if (indexToReplace !== -1) {
              this.imageOCT.splice(indexToReplace, 1, newItem);
            }
          } else {
            this.imageOCT.push(newItem);
          }
          this.hasSingleUpload[4] = true;
          break;
      }
      this.handleImageUpload();
    },
    handleImageUpload() {
      this.images = [
        ...this.imageFundus,
        ...this.imageOCT
      ];
      this.isUploadImg = true;
    },//10:38
    async getResults() {
      if (!this.isUploadImg) {
        this.$alert('请先上传图片!', '注意', {
          confirmButtonText: '确定',
          callback: () => { }
        });
      } else {
        this.isLoading = true;
        // this.hasCommitted = true;
        // 这里模拟加载过程，假设 3 秒后加载完成，隐藏加载动画，模拟获取答案
        console.log(this.images);
        await axios.post(getApiUrl("/aibo"), this.images).then(res => {
          this.isLoading = false;
          this.setUpName = "重新进行分析";
          const results = res.data.data;
          console.log(results)
          if (!this.isBulkUpload) {
            this.imageResult = results;
            for (let image of results)
              this.enforceImageResults[image.index] = image.enhanced_image;
          } else {
            this.groupedImagesResult = this.getGroupedImages(results);
            // this.groupedEnforceImagesResults = this.getGroupedImages(results);
          }
          this.isUploadImg = true;
          this.hasAnalysis = true;
        })
      }
    },
    observationMode() {
      if (!this.isUploadImg) {
        this.$alert('请先上传图片!', '注意', {
          confirmButtonText: '确定',
          callback: () => { }
        });
      } else {
        this.$router.push({
          path: '/imageObservation',
          query: {
            images: this.isBulkUpload ? this.groupedImages : this.images,
            imagePaths: this.imagePaths,
            imageSrc: this.imageSrc,
            imageResults: this.isBulkUpload ? this.groupedImagesResult : this.imageResult,
            isBulkUpload: this.isBulkUpload,
            patientName: this.patientName,
            patientAge: this.patientAge,
            patientSex: this.patientSex,
            trackingNumber: this.trackingNumber
          }
        })
      }
    },
    reBulkUpload() {
      this.$confirm('重新上传将不保留现有已上传的图片, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.isUploadImg = false;
        this.hasAnalysis = false;
        this.activeIndex = 0
        this.selectedGroup = 0;
        this.totalGroup = 0;
        this.setUpName = "启动AI分析";
        this.groupImageKind = [];
        this.groupedImages = [];
        this.groupedImagesResult = [];
        this.groupedEnforceImagesResults = [];

      }).catch(() => { });
    },
    onRectangleAdded(rectangle) {
      console.log("这是父组件的矩形框添加:", rectangle);
      // 可以在这里添加父组件的处理逻辑，如保存矩形框信息
    },
    onRectangleRemoved(rectangle) {
      console.log("这是父组件的矩形框删除:", rectangle);
      // 可以在这里添加父组件的处理逻辑，如更新数据等
    },
    //点击“显示...概率”按钮时触发切换显示
    showProbabilities(index) {
      this.activeIndex = index;
    },
  },
  watch: {
    images: {
      handler(newValue) {
        this.isUploadImg = newValue.length > 0;
      },
      deep: true // 深度监听数组变化
    }
  }
};
</script>

<style scoped>
#imageAnalysis {
  width: calc(100% - 30px);
  height: calc(100% - 30px);
  padding: 15px;
  background: white;
  display: flex;
  overflow: hidden;
}

.submit-and-results {
  width: calc(70% - 20px);
  border: none;
  margin-right: 20px;
  /* box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3); */
  background: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.submit {
  width: 100%;
  height: calc(50% - 10px);
  padding: 0 15px 25px 0;
}

.results {
  width: 100%;
  height: calc(50% - 15px);
}

.single-results {
  width: 100%;
  height: 100%;
  display: flex;
}

.eyeGround-results {
  width: 50%;
  height: 100%;
  margin-right: 20px;
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.oct-results {
  width: 50%;
  height: 100%;
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  /* 添加盒阴影 */
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.bulk-results {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.title {
  margin-top: 10px;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #2c6d62;
  letter-spacing: 2px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
}

.states {
  width: 30%;
  border: none;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #a8d8d0 0%, #bce8e1 100%);
}

.setUp {
  width: 100%;
  height: 20%;
  border-bottom: 1px solid rgba(61, 115, 105, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #b2e2da 0%, #c6f2eb 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 10px 10px 0 0;
  z-index: 1;
}

.setUp button {
  width: calc(50% - 20px);
  height: calc(100% - 20px);
  margin: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #c2e8e2 0%, #d4f4ef 100%);
  color: #2a5e55;
  border: none;
  border-radius: 30px;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  align-items: center;
}

.setUp button:hover {
  background: linear-gradient(135deg, #b1dbd5 0%, #c2e8e2 100%);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.setUp button.active {
  background: #388e3c;
  color: #fff;
  box-shadow: 0 4px 8px rgba(56, 142, 60, 0.2);
  transform: scale(1.05);
}

.setUp button::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-100%);
  transition: transform 0.3s ease;
}

.setUp button:hover::before {
  transform: translateY(0);
}

.big-icon {
  font-size: 20px;
  margin-right: 8px;
  /* 可根据需要调整图标与文字的间距 */
}

.setUp::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: -20px;
  width: 80%;
  height: 1px;
  background: linear-gradient(90deg, transparent 30%, rgba(42, 94, 85, 0.1) 50%, transparent 70%);
}

.mode {
  width: 100%;
}

.tools {
  width: 100%;
}

.probabilities {
  height: calc(80% - 40px);
  padding: 20px;
  border-bottom-right-radius: 10px;
  text-align: center;
  color: #2a5e55;
  overflow-y: scroll;
  /* 隐藏滚动条（Firefox） */
  scrollbar-width: none;
}

.probability-buttons {
  padding: 0 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.probability-buttons button {
  /* 调小宽度 */
  padding: 4px 6px;
  background: rgba(255, 255, 255, 0.2);
  color: #2a5e55;
  border: none;
  /* 修改圆角，模拟书签形状 */
  border-radius: 8px 8px 0 0;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: none;
  /* 减小最小宽度 */
  min-width: 80px;
}

.probability-buttons button::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  /* 绘制三角形 */
  width: 0;
  height: 0;
  border-top: 12px solid #2a5e55;
  border-left: 12px solid transparent;
}

.probability-buttons button.active {
  background: #4CAF50;
  color: white;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
  transform: translateY(0) scale(1.05);
  font-weight: 600;
}

.probability-buttons button.active::after {
  /* 激活状态下三角形颜色改变 */
  border-top: 12px solid white;
}

.probability-buttons button::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(76, 175, 80, 0.2);
  transform: scale(0);
  filter: blur(5px);
  transition: transform 0.3s ease, filter 0.3s ease;
}

.probability-buttons button:hover::before {
  transform: scale(1);
  filter: blur(0);
}

/* .progress {
  margin-top: 20px;
} */

.progresses-empty {
  width: 100%;
  text-align: center;
  font-size: 30px;
  color: #999;
}

.single-submit {
  width: 100%;
  display: flex;
  height: 100%;
}

.eyeGround-group {
  width: calc(50% - 10px);
  margin-right: 20px;
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  /* 添加盒阴影 */
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.oct-group {
  width: calc(50% - 10px);
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  /* 添加盒阴影 */
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.batch-submit {
  width: 100%;
  height: 100%;
  /* 使用渐变背景 */
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  /* 添加盒阴影 */
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  /* 优化边框样式 */
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.imageContainer {
  width: 100%;
  height: 80%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.bulkImageContainer {
  width: 100%;
  height: 80%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bulk-images {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 待定 */
.group-number {
  position: absolute;
  right: 0;
  top: 10px;
  transform: translateX(-50%);
  color: #fff;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 14px;
}

.arrow {
  position: absolute;
  top: 25%;
  transform: scaleX(0.5) translateY(-50%);
  font-size: 50px;
  color: black;
  background-color: transparent;
  cursor: pointer;
  z-index: 10;
}

.left-arrow {
  left: 15px;
}

.right-arrow {
  right: 15px;
}

.reUpload-icon {
  position: absolute;
  top: 40%;
  right: 15px;
  background: linear-gradient(135deg, #2c6d62 0%, #388e3c 100%);
  ;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

/* 这是原来的样式 */
/* .images {
  margin: 0 12px 0 12px;
} */

.images {
  margin: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  /* transition: transform 0.3s ease; */
  transform: scale(1);
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.images:hover {
  transform: scale(1.05);
}

.single-image {
  width: 100%;
}

.single-result {
  width: 45%;
}

.group-image {
  width: 22%;
}

.imageSelectorContainer {
  width: calc(100% - 20px);
  padding: 10px;
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.imageSelector {
  width: 30%;
  height: 10%;
  position: absolute;
  right: 0;
  bottom: 0;
  cursor: pointer;
  z-index: 3;
  text-align: center;
  transition: all 0.3s ease;
}

.imageSelector:hover {
  transform: scale(1.05);
}

.imageSelector button {
  width: 100%;
  cursor: pointer;
  font-size: 12px;
  border: none;
  margin: 0;
  color: #fff;
  background: linear-gradient(135deg, #2c6d62 0%, #388e3c 100%);
  border-radius: 8px;
  font-weight: 600;
  padding: 8px 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.imageSelector button:hover {
  background: linear-gradient(135deg, #388e3c 0%, #2c6d62 100%);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.imageSelector button.active {
  color: #fff;
  background: linear-gradient(135deg, #388e3c 0%, #4caf50 100%);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
  transform: scale(1.05);
}

input[type="file"] {
  padding: 12px 24px;
  background: linear-gradient(135deg, #c2e8e2 0%, #d4f4ef 100%);
  color: #2a5e55;
  border: 3px solid #2a5e55;
  border-radius: 30px;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 0 0 3px rgba(42, 94, 85, 0.2), 0 4px 12px rgba(0, 0, 0, 0.1);
}

input[type="file"]::file-selector-button {
  border: none;
  background: transparent;
  padding: 0;
  margin: 0;
  color: inherit;
  font: inherit;
  cursor: pointer;
  position: relative;
  z-index: 1;
}

input[type="file"]:hover {
  background: linear-gradient(135deg, #b1dbd5 0%, #c2e8e2 100%);
  border-color: #388e3c;
  box-shadow: 0 0 0 3px rgba(56, 142, 60, 0.3), 0 8px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

input[type="file"]:focus {
  outline: none;
  background: linear-gradient(135deg, #a0cfc6 0%, #b1dbd5 100%);
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.4), 0 0 10px rgba(42, 94, 85, 0.4);
  transform: scale(1.04);
}
</style>
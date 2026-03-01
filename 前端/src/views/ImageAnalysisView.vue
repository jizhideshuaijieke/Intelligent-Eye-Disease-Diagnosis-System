<template>
  <div id="imageAnalysis" v-loading.lock="isLoading" element-loading-text="正在分析">
    <div class="submit-and-results">
      <div class="submit">
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
                <ImageUploader v-show="!imageKind[index]" :isUpload="true" @file-uploaded="(payload) => imageUpload(payload, index)" />
                <ImageUploader v-if="hasAnalysis && imageKind[index]" :imageFile="enforceImageResults[index]" />
              </div>
            </div>
          </div>

          <div class="oct-group">
            <div class="title">OCT图像</div>
            <div class="imageContainer">
              <div v-for="index in [3, 4]" :key="index" class="images single-image">
                <ImageUploader :isUpload="true" @file-uploaded="(payload) => imageUpload(payload, index)" />
              </div>
            </div>
          </div>
        </div>

        <div v-else class="batch-submit">
          <div class="title">批量上传</div>
          <div class="bulkImageContainer">
            <div v-if="!isUploadImg" class="bulk-upload">
              <input type="file" webkitdirectory directory multiple @change="startBulkUpload" ref="folderInput">
            </div>
            <div v-if="isUploadImg" class="bulk-images">
              <div class="group-number">当前组号: {{ selectedGroup + 1 }}</div>
              <div class="arrow left-arrow" @click="prevPage" v-if="selectedGroup !== 0">&lt;</div>
              <div class="imageContainer">
                <div v-for="(image, index) in currentGroupedImages" :key="index" class="images group-image">
                  <div v-if="hasAnalysis && currentGroupedResults[index] && currentGroupedResults[index].enhanced_image" class="imageSelector">
                    <button @click="ImageUploaderButton(index)" :class="{ active: groupImageKind[selectedGroup] && groupImageKind[selectedGroup][index] }">
                      <span>{{ groupImageKind[selectedGroup] && groupImageKind[selectedGroup][index] ? "显示原图" : "显示增强" }}</span>
                    </button>
                  </div>
                  <ImageUploader :imageFile="getBulkPreviewImage(index, image.path)" />
                </div>
              </div>
              <div class="arrow right-arrow" @click="nextPage" v-if="selectedGroup !== totalGroup - 1">&gt;</div>
              <div class="reUpload-icon" @click="reBulkUpload" title="重新上传">
                <i class="el-icon-refresh-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="results">
        <div v-if="!isBulkUpload" class="single-results">
          <div class="eyeGround-results">
            <div class="title">眼底结果图像</div>
            <div v-if="hasAnalysis" class="imageContainer">
              <div v-for="(image, index) in filteredEyeGroundImageResult" :key="index" class="images single-result">
                <ImageUploader :imageFile="image.path" />
              </div>
            </div>
          </div>

          <div class="oct-results">
            <div class="title">OCT分层图像</div>
            <div v-if="hasAnalysis" class="imageContainer">
              <div v-for="(image, index) in filteredOCTImageResult" :key="index" class="images single-result">
                <ImageUploader :imageFile="image.path" />
              </div>
            </div>
          </div>
        </div>

        <div v-else class="bulk-results">
          <div class="title">结果图</div>
          <div v-if="hasAnalysis" class="imageContainer">
            <div v-for="(image, index) in currentGroupedResults" :key="index" class="images group-image">
              <ImageUploader :imageFile="image.path" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="states">
      <div class="setUp">
        <div class="mode">
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
      </div>

      <div class="probabilities">
        <div v-if="hasAnalysis && currentProbabilityTargets.length" class="probability-buttons">
          <button v-for="(image, index) in currentProbabilityTargets" :key="index" @click="showProbabilities(index)" :class="{ active: activeIndex === index }">
            图像{{ index + 1 }}的概率
          </button>
        </div>
        <div v-if="hasAnalysis && currentProgresses.length" class="progress">
          <StatusBar :progresses="currentProgresses"></StatusBar>
        </div>
        <div v-else-if="hasAnalysis" class="progresses-empty">当前上传图像暂未返回可展示的概率</div>
      </div>
    </div>
  </div>
</template>

<script>
import StatusBar from '@/components/IllnessExpectationColumn.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import axios from 'axios'
import { getApiUrl } from '@/api/config'

export default {
  name: 'ImageAnalysisView',
  components: { StatusBar, ImageUploader },
  computed: {
    filteredEyeGroundImageResult() {
      return this.sortByIndex(this.imageResult.filter(image => image.name === 'left' || image.name === 'right'))
    },
    filteredOCTImageResult() {
      return this.sortByIndex(this.imageResult.filter(image => image.name === 'left-oct' || image.name === 'right-oct'))
    },
    filteredImageResult() {
      return this.sortByIndex(this.imageResult.filter(image => image.name !== 'left-oct' && image.name !== 'right-oct'))
    },
    filteredGroupedImages() {
      return this.groupedImagesResult.map(group => group.filter(image => image.name !== 'left-oct' && image.name !== 'right-oct'))
    },
    currentGroupedImages() {
      return this.groupedImages[this.selectedGroup] || []
    },
    currentGroupedResults() {
      return this.groupedImagesResult[this.selectedGroup] || []
    },
    currentProbabilityTargets() {
      if (!this.hasAnalysis) return []
      if (this.isBulkUpload) {
        const currentGroupFundus = this.filteredGroupedImages[this.selectedGroup] || []
        if (currentGroupFundus.length) return currentGroupFundus
        return (this.groupedImagesResult[this.selectedGroup] || []).filter(image => image.name === 'left-oct' || image.name === 'right-oct')
      }
      if (this.filteredImageResult.length) return this.filteredImageResult
      return this.filteredOCTImageResult || []
    },
    currentProgresses() {
      const targets = this.currentProbabilityTargets
      if (!Array.isArray(targets) || targets.length === 0) return []
      const safeIndex = Math.min(this.activeIndex, targets.length - 1)
      const current = targets[safeIndex]
      if (Array.isArray(current?.probabilities) && current.probabilities.length) return current.probabilities
      if (current?.name === 'left-oct' || current?.name === 'right-oct') return this.mockSameTypeProbabilities(current?.index)
      return []
    }
  },
  data() {
    return {
      patientName: '张三',
      patientAge: 21,
      patientSex: '男',
      trackingNumber: 'HOSP20250324A001',
      imageKind: { 1: false, 2: false, 3: false, 4: false },
      hasSingleUpload: { 1: false, 2: false, 3: false, 4: false },
      groupImageKind: [[]],
      imageFundus: [],
      imageOCT: [],
      hasCommitted: false,
      hasAnalysis: false,
      setUpName: '启动AI分析',
      activeIndex: 0,
      isLoading: false,
      images: [],
      groupedImages: [],
      imageResult: [],
      enforceImageResults: { 1: null, 2: null, 3: null, 4: null },
      groupedImagesResult: [],
      groupedEnforceImagesResults: [],
      imageSrc: '',
      imagePaths: [],
      isUploadImg: false,
      isBulkUpload: false,
      selectedGroup: 0,
      totalGroup: 0,
    }
  },
  methods: {
    sortByIndex(items) {
      const list = Array.isArray(items) ? items : []
      return [...list].sort((a, b) => Number(a?.index || 0) - Number(b?.index || 0))
    },
    prevPage() {
      if (this.selectedGroup > 0) this.selectedGroup--
      this.activeIndex = 0
    },
    nextPage() {
      if (this.selectedGroup < this.totalGroup - 1) this.selectedGroup++
      this.activeIndex = 0
    },
    setBulkStatus() {
      const resetData = () => {
        this.isUploadImg = false
        this.images = []
        this.groupedImages = []
        this.hasAnalysis = false
        this.imageResult = []
        this.enforceImageResults = { 1: null, 2: null, 3: null, 4: null }
        this.groupedImagesResult = []
        this.groupedEnforceImagesResults = []
        this.activeIndex = 0
        this.setUpName = '启动AI分析'
      }

      if (this.isUploadImg) {
        this.$confirm('你已上传过图片，切换模式将不保留已上传图片，是否继续？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.isBulkUpload = !this.isBulkUpload
          resetData()
        }).catch(() => {})
      } else {
        this.isBulkUpload = !this.isBulkUpload
        resetData()
      }
    },
    async startBulkUpload(event) {
      if (event.target.files.length === 0) return

      this.isUploadImg = true
      const files = Array.from(event.target.files)
      const folderStructure = {}

      files.forEach(file => {
        const pathParts = file.webkitRelativePath.split('/')
        if (pathParts.length > 2) {
          const folderName = pathParts[1]
          if (!folderStructure[folderName]) folderStructure[folderName] = []
          folderStructure[folderName].push(file)
        }
      })

      let idx = 1
      if (Object.entries(folderStructure).length) {
        this.images = []
        this.imageResult = []
        this.selectedGroup = 0
      }

      for (const [, groupFiles] of Object.entries(folderStructure)) {
        for (const file of groupFiles) {
          const base64 = await this.readFileAsBase64(file)
          const matches = base64.match(/^data:(.+);base64,(.+)$/)
          const imageType = matches ? matches[1] : ''

          if (imageType === 'image/png') {
            this.images.push({
              index: idx,
              name: 'left-oct',
              path: base64,
              probabilities: [],
              hasLegend: true,
              legends: [
                { color: '#FFFF00', name: '神经纤维层' },
                { color: '#00FFFF', name: '神经节细胞层+内丛状层' },
                { color: '#FFA500', name: '内核层' },
                { color: '#0000FF', name: '外丛状层' },
                { color: '#FF0000', name: '外核层' },
                { color: '#00FF00', name: '椭圆体带' },
                { color: '#0000FF', name: '视网膜色素上皮层' },
                { color: '#A52A2A', name: '脉络膜' },
              ],
            })
          } else {
            this.images.push({ index: idx, name: '', path: base64, probabilities: [] })
          }
        }
        idx++
      }

      this.images.sort((a, b) => a.index - b.index)
      this.groupedImages = this.getGroupedImages(this.images)
      this.groupImageKind = this.getImageKindByImages(this.groupedImages)
      this.totalGroup = this.groupedImages.length
    },
    getGroupedImages(images) {
      const groups = {}
      images.forEach((image) => {
        if (!groups[image.index]) groups[image.index] = []
        groups[image.index].push(image)
      })
      return Object.values(groups)
    },
    getImageKindByImages(images) {
      return images.map(item => (Array.isArray(item) ? this.getImageKindByImages(item) : false))
    },
    async readFileAsBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = error => reject(error)
        reader.readAsDataURL(file)
      })
    },
    ImageUploaderButton(type) {
      if (!this.isBulkUpload) {
        this.imageKind[type] = !this.imageKind[type]
      } else {
        this.$set(this.groupImageKind[this.selectedGroup], type, !this.groupImageKind[this.selectedGroup][type])
      }
    },
    imageUpload(payload, type) {
      const newItem = {
        index: type,
        name: '',
        path: payload.base64,
        probabilities: [],
        hasLegend: type > 2,
        legends: type <= 2 ? [] : [
          { color: '#FFFF00', name: '神经纤维层' },
          { color: '#00FFFF', name: '神经节细胞层+内丛状层' },
          { color: '#FFA500', name: '内核层' },
          { color: '#0000FF', name: '外丛状层' },
          { color: '#FF0000', name: '外核层' },
          { color: '#00FF00', name: '椭圆体带' },
          { color: '#0000FF', name: '视网膜色素上皮层' },
          { color: '#A52A2A', name: '脉络膜' },
        ]
      }

      switch (type) {
        case 1:
          newItem.name = 'left'
          if (this.hasSingleUpload[1]) {
            const i = this.imageFundus.findIndex(item => item.index === 1)
            if (i !== -1) this.imageFundus.splice(i, 1, newItem)
          } else {
            this.imageFundus.push(newItem)
          }
          this.hasSingleUpload[1] = true
          break
        case 2:
          newItem.name = 'right'
          if (this.hasSingleUpload[2]) {
            const i = this.imageFundus.findIndex(item => item.index === 2)
            if (i !== -1) this.imageFundus.splice(i, 1, newItem)
          } else {
            this.imageFundus.push(newItem)
          }
          this.hasSingleUpload[2] = true
          break
        case 3:
          newItem.name = 'left-oct'
          if (this.hasSingleUpload[3]) {
            const i = this.imageOCT.findIndex(item => item.index === 3)
            if (i !== -1) this.imageOCT.splice(i, 1, newItem)
          } else {
            this.imageOCT.push(newItem)
          }
          this.hasSingleUpload[3] = true
          break
        case 4:
          newItem.name = 'right-oct'
          if (this.hasSingleUpload[4]) {
            const i = this.imageOCT.findIndex(item => item.index === 4)
            if (i !== -1) this.imageOCT.splice(i, 1, newItem)
          } else {
            this.imageOCT.push(newItem)
          }
          this.hasSingleUpload[4] = true
          break
      }

      this.imageFundus = this.sortByIndex(this.imageFundus)
      this.imageOCT = this.sortByIndex(this.imageOCT)
      this.handleImageUpload()
    },
    handleImageUpload() {
      this.images = this.sortByIndex([...this.imageFundus, ...this.imageOCT])
      this.isUploadImg = true
    },
    getBulkPreviewImage(index, originalPath) {
      const groupFlags = this.groupImageKind[this.selectedGroup] || []
      const useEnhanced = !!groupFlags[index]
      const enhanced = this.currentGroupedResults[index]?.enhanced_image
      return useEnhanced && enhanced ? enhanced : originalPath
    },
    async getResults() {
      if (!this.isUploadImg) {
        this.$alert('请先上传图片！', '注意', { confirmButtonText: '确定' })
        return
      }

      this.isLoading = true
      try {
        const res = await axios.post(getApiUrl('/aibo'), this.images)
        this.setUpName = '重新进行分析'
        const results = Array.isArray(res?.data?.data) ? res.data.data : []

        if (!this.isBulkUpload) {
          const sortedResults = this.sortByIndex(results)
          this.imageResult = sortedResults
          for (const image of sortedResults) {
            this.enforceImageResults[image.index] = image.enhanced_image
          }
        } else {
          this.groupedImagesResult = this.getGroupedImages(results)
        }

        this.activeIndex = 0
        this.isUploadImg = true
        this.hasAnalysis = true
      } catch (e) {
        this.$alert('分析失败，请稍后重试。', '错误', { confirmButtonText: '确定' })
      } finally {
        this.isLoading = false
      }
    },
    observationMode() {
      if (!this.isUploadImg) {
        this.$alert('请先上传图片！', '注意', { confirmButtonText: '确定' })
        return
      }
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
          trackingNumber: this.trackingNumber,
        },
      })
    },
    reBulkUpload() {
      this.$confirm('重新上传将不保留现有已上传图片，是否继续？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }).then(() => {
        this.isUploadImg = false
        this.hasAnalysis = false
        this.activeIndex = 0
        this.selectedGroup = 0
        this.totalGroup = 0
        this.setUpName = '启动AI分析'
        this.groupImageKind = []
        this.groupedImages = []
        this.groupedImagesResult = []
        this.groupedEnforceImagesResults = []
      }).catch(() => {})
    },
    mockSameTypeProbabilities(index) {
      const base = [
        { name: '正常', probability: 0.36 },
        { name: '其他疾病', probability: 0.16 },
        { name: '病理性近视', probability: 0.14 },
        { name: '青光眼', probability: 0.12 },
        { name: '白内障', probability: 0.10 },
        { name: '糖尿病性视网膜病变', probability: 0.08 },
        { name: '老年性黄斑部病变', probability: 0.06 },
        { name: '高血压视网膜病变', probability: 0.04 },
      ]
      const offset = (Number(index) % 5) * 0.01
      return base
        .map((item, i) => ({
          name: item.name,
          probability: Number(Math.max(0.01, item.probability + (i % 2 === 0 ? offset : -offset)).toFixed(3)),
        }))
        .sort((a, b) => b.probability - a.probability)
    },
    showProbabilities(index) {
      this.activeIndex = index
    },
  },
  watch: {
    images: {
      handler(newValue) {
        this.isUploadImg = newValue.length > 0
      },
      deep: true,
    },
  },
}
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
  
  scrollbar-width: none;
}

.probability-buttons {
  padding: 0 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.probability-buttons button {
  
  padding: 4px 6px;
  background: rgba(255, 255, 255, 0.2);
  color: #2a5e55;
  border: none;
  
  border-radius: 8px 8px 0 0;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: none;
  
  min-width: 80px;
}

.probability-buttons button::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  
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
  
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.oct-group {
  width: calc(50% - 10px);
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.batch-submit {
  width: 100%;
  height: 100%;
  
  background: linear-gradient(135deg, #d4f4ef 0%, #e4f9f5 100%);
  border-radius: 12px;
  
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  
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




.images {
  margin: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  
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


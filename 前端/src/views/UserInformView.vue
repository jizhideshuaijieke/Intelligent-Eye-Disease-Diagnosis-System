<template>
  <div id="doctorInfor">
    <div class="body">
      <el-form :model="form" class="inforForm">
        <!-- 左半部分表单 -->
        <div class="leftPart">
          <!-- 基本信息 -->
          <div class="upPart">
            <div style="display: flex; justify-content: left; align-items: center;">
              <h4>基本信息</h4>
            </div>
            <div class="inforLineContainer">
              <el-form-item label="姓名" prop="name">
                <i class="el-icon-user"></i>
                <el-input v-model="form.name" :disabled="!isEditing" />
              </el-form-item>

              <el-form-item label="年龄" prop="age">
                <i class="el-icon-s-data"></i>
                <el-input v-model="form.age" :disabled="!isEditing" />
              </el-form-item>

              <el-form-item label="性别" prop="gender">
                <img :src="require('@/assets/buttonIcons/xingbie.svg')" />
                <el-input v-model="form.gender" :disabled="!isEditing" />
              </el-form-item>

              <el-form-item label="医生工号" prop="doctorID">
                <i class="el-icon-s-order"></i>
                <el-input v-model="form.doctorID" :disabled="!isEditing" />
              </el-form-item>
            </div>

            <div class="inforLineContainer">
              <el-form-item label="科室" prop="department">
                <i class="el-icon-view"></i>
                <el-input v-model="form.department" :disabled="!isEditing" />
              </el-form-item>
              <el-form-item label="电子邮箱" prop="email">
                <i class="el-icon-message"></i>
                <el-input v-model="form.email" :disabled="!isEditing" />
              </el-form-item>
              <el-form-item label="手机号" prop="phone">
                <i class="el-icon-phone-outline"></i>
                <el-input v-model="form.phone" :disabled="!isEditing" />
              </el-form-item>
            </div>
          </div>
          <div class="downPart">
            <div style="display: flex; justify-content: left; align-items: center;">
              <h4>安全设置</h4>
            </div>
            <div class="passwordContainer">
              <div class="modify">
                <el-form-item label="原密码" prop="oldPasswordInput">
                  <i class="el-icon-lock"></i>
                  <el-input v-model="form.oldPasswordInput" :disabled="!isModifyPassword" type="password"
                    :placeholder="isModifyPassword ? '' : '********'" />
                </el-form-item>
                <el-button @click="setModifyStatus" :disabled="!isEditing" v-if="!isModifyPassword"
                  class="passwordButton">修改</el-button>
                <el-button @click="submitPassWord" v-if="isModifyPassword" class="passwordButton">提交</el-button>
              </div>
              <el-form-item label="新密码" prop="newPassword" v-if="isModifyPassword">
                <el-input v-model="form.newPassword" type="password" />
              </el-form-item>
            </div>
          </div>
        </div>
        <!-- 右半部分图片-->
        <div class="rightPart">
          <div class="imageSizeControler">
            <el-form-item label="个人照片" class="imageContainer">
              <i class="el-icon-camera-solid"></i>
              <ImageUploader :isUpload="true" @file-uploaded="imageUpload" :disabled="!isEditing" class="image" />
            </el-form-item>
          </div>
        </div>
      </el-form>

      <div class="button-group">
        <el-button v-if="!isEditing" type="primary" @click="setEditingStatus">修改</el-button>
        <el-button v-else type="success" @click="setEditingStatus">提交</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import ImageUploader from '@/components/ImageUploader.vue';

export default {
  components: {
    ImageUploader
  },
  data() {
    return {
      isEditing: false,
      isModifyPassword: false,
      isOldPasswordInputValid: false,
      form: {
        name: '',
        age: '',
        gender: '',
        doctorID: '',
        department: '',
        email: '',
        phone: '',
        image: '',
        passWord: '1433223',
        oldPasswordInput: '',
        newPassword: ''
      }
    }
  },
  methods: {
    setEditingStatus() {
      this.isEditing = !this.isEditing;
    },
    setModifyStatus() {
      this.isModifyPassword = !this.isModifyPassword;
    },
    submitPassWord() {
      if (this.form.oldPasswordInput === this.form.passWord) {
        if (this.form.newPassword === '') {
          this.$message.error("新密码不能为空！");
        } else {
          this.form.passWord = this.form.newPassword;
          this.form.newPassword = this.form.oldPasswordInput = '';
          this.$message.success("修改成功！");
          this.isModifyPassword = false;
        }
      } else {
        if (this.form.oldPasswordInput === '')
          this.$message.error("请先输入原密码！");
        else
          this.$message.error("原密码错误，请重试！");

        this.form.newPassword = '';
        this.form.oldPasswordInput = '';
      }
    },
    imageUpload({ file, base64 }) {
      this.form.image = base64;
      this.file = file;
    }
  }
}
</script>

<style scoped>
#doctorInfor {
  height: 100%;
  width: 100%;
}

.body {
  height: 100%;
  width: 100%;
  padding: 2rem 10rem 0 10rem;
  box-sizing: border-box;
  background-color: #ffffff;
}

.inforForm {
  display: flex;
  flex-wrap: wrap;
  height: 80%;
  margin-bottom: 2rem;
  margin-left: 5rem;
  margin-right: 5rem;
  gap: 2rem;
}

.leftPart {
  flex: 7;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  border-radius: 10px;
}

.upPart {
  background-color: #f8f9fa;
  border-left: 4px solid#3a86ff;
  border-radius: 10px;
  border: 1px solid #65676c;
  padding: 0 20px 20px 20px;
}

.downPart {
  background-color: #f8f9fa;
  border-left: 4px solid#219ebc;
  border-radius: 10px;
  border: 1px solid #65676c;
  padding: 0 20px 20px 20px;
}

.rightPart {
  flex: 3;
  display: flex;
  height: 50%;
  justify-content: right;
  background-color: #ffffff;
  border-radius: 10px;
}

.imageSizeControler {
  width: 100%;
  height: 100%;
  border-radius: 10px;
  background-color: #ffffff;
  border: 1px solid #65676c;
}

.imageContainer {
  width: 60%;
  margin: 0 auto;
  background-color: transparent;
}

.inforLineContainer {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.inforLineContainer .el-form-item {
  flex: 1;
  min-width: 100px;
}

.passwordContainer {
  display: flex;
  gap: 2rem;
}

.passwordButton {
  background-color: transparent;
  border-radius: 4px;
  border-color: #65676c;
  color: #67606F;
}

.passwordButton:disabled {
  background-color: transparent;
  color: #b3b0b6;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

/* 通用样式 */
.el-form-item :deep(.el-form-item__label) {
  color: #000000;
}

.el-input :deep(.el-input__inner) {
  color: #000000;
  background-color: #fcfcfc;
  border-color: #65676c;
  transition: all 0.3s;
  border-radius: 6px;
}

.el-input :deep(.el-input__inner):focus {
  border-color: #286d25;
  box-shadow: 0 0 0 2px rgba(1, 124, 77, 0.689);
}

/* 按钮样式 */
.el-button--primary,
.el-button--success {
  border-radius: 6px;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.el-button--primary {
  background-color: #204532;
  border-color: #204532;
}

.el-button--success {
  background-color: #7ee6c2;
  border-color: #dde0e5;
  color: #000000;
}

.el-input.is-disabled :deep(.el-input__inner) {
  background-color: #e6e6e6;
  color: #67606F;
}
</style>
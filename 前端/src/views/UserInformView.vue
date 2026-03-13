<template>
  <div id="doctorInfor">
    <div class="body">
      <el-form :model="form" class="inforForm">
        <div class="leftPart">
          <div class="upPart">
            <div class="section-title">
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
                <i class="el-icon-male"></i>
                <el-input v-model="form.gender" :disabled="!isEditing" />
              </el-form-item>

              <el-form-item label="医生工号" prop="doctorID">
                <i class="el-icon-s-order"></i>
                <el-input v-model="form.doctorID" disabled />
              </el-form-item>
            </div>

            <div class="inforLineContainer">
              <el-form-item label="科室" prop="department">
                <i class="el-icon-office-building"></i>
                <el-input v-model="form.department" :disabled="!isEditing" />
              </el-form-item>

              <el-form-item label="邮箱" prop="email">
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
            <div class="section-title">
              <h4>安全设置</h4>
            </div>
            <div class="passwordContainer">
              <div class="modify">
                <el-form-item label="原密码" prop="oldPasswordInput">
                  <i class="el-icon-lock"></i>
                  <el-input
                    v-model="form.oldPasswordInput"
                    :disabled="!isModifyPassword"
                    type="password"
                    :placeholder="isModifyPassword ? '' : '********'"
                  />
                </el-form-item>
                <el-button @click="setModifyStatus" v-if="!isModifyPassword" class="passwordButton">
                  设置新密码
                </el-button>
                <el-button @click="submitPassWord" v-if="isModifyPassword" class="passwordButton">
                  提交
                </el-button>
              </div>

              <el-form-item label="新密码" prop="newPassword" v-if="isModifyPassword">
                <el-input v-model="form.newPassword" type="password" />
              </el-form-item>
            </div>
          </div>
        </div>

        <div class="rightPart">
          <div class="imageSizeControler">
            <el-form-item label="个人照片" class="imageContainer">
              <i class="el-icon-camera-solid"></i>
              <ImageUploader
                :isUpload="true"
                :imageFile="form.photo"
                :disabled="!isEditing"
                @file-uploaded="imageUpload"
                class="image"
              />
            </el-form-item>
          </div>
          <div class="functionalButtons">
            <div class="button">
              <el-button v-if="!isEditing" type="primary" @click="setEditingStatus">修改资料</el-button>
              <el-button v-else type="success" @click="setEditingStatus">提交</el-button>
            </div>
            <div class="button">
              <el-button type="primary" @click="logOut">退出登录</el-button>
            </div>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

import ImageUploader from '@/components/ImageUploader.vue';
import { getApiUrl } from '@/api/config';
import { clearAuthSession, getAuthToken } from '@/utils/auth';

export default {
  components: {
    ImageUploader,
  },
  data() {
    return {
      isEditing: false,
      isModifyPassword: false,
      form: {
        name: '',
        age: '',
        gender: '',
        doctorID: '',
        department: '',
        email: '',
        phone: '',
        photo: '',
        oldPasswordInput: '',
        newPassword: '',
      },
    };
  },
  mounted() {
    this.loadProfile();
  },
  methods: {
    getTokenOrRedirect() {
      const token = getAuthToken();
      if (!token) {
        this.$router.push('/login');
        return '';
      }
      return token;
    },
    async loadProfile() {
      const token = this.getTokenOrRedirect();
      if (!token) return;

      try {
        const response = await axios.post(getApiUrl('/getPersonalInform'), { token });
        const payload = response?.data || {};
        if (payload.code !== 1) {
          throw new Error(payload.message || '获取个人信息失败');
        }

        const data = payload.data || {};
        this.form.name = data.name || '';
        this.form.age = data.age ?? '';
        this.form.gender = data.gender || '';
        this.form.doctorID = data.accountId || '';
        this.form.department = data.department || '';
        this.form.email = data.email || '';
        this.form.phone = data.phone || '';
        this.form.photo = data.photo || '';
      } catch (error) {
        this.$message.error(error?.message || '获取个人信息失败');
      }
    },
    async setEditingStatus() {
      if (!this.isEditing) {
        this.isEditing = true;
        return;
      }

      const token = this.getTokenOrRedirect();
      if (!token) return;

      try {
        const response = await axios.post(getApiUrl('/updatePersonalInform'), {
          token,
          name: this.form.name,
          gender: this.form.gender,
          age: this.form.age === '' ? null : Number(this.form.age),
          department: this.form.department,
          email: this.form.email,
          phone: this.form.phone,
          photo: this.form.photo,
        });
        const payload = response?.data || {};
        if (payload.code !== 1) {
          throw new Error(payload.message || '更新失败');
        }

        this.$message.success('资料更新成功');
        this.isEditing = false;
        await this.loadProfile();
      } catch (error) {
        this.$message.error(error?.message || '更新失败');
      }
    },
    setModifyStatus() {
      this.isModifyPassword = !this.isModifyPassword;
      if (!this.isModifyPassword) {
        this.form.oldPasswordInput = '';
        this.form.newPassword = '';
      }
    },
    async submitPassWord() {
      if (!this.form.oldPasswordInput) {
        this.$message.error('请先输入原密码');
        return;
      }
      if (!this.form.newPassword) {
        this.$message.error('新密码不能为空');
        return;
      }

      const token = this.getTokenOrRedirect();
      if (!token) return;

      try {
        const response = await axios.post(getApiUrl('/changePassword'), {
          token,
          oldPassword: this.form.oldPasswordInput,
          newPassword: this.form.newPassword,
        });
        const payload = response?.data || {};
        if (payload.code !== 1) {
          throw new Error(payload.message || '修改密码失败');
        }

        this.form.oldPasswordInput = '';
        this.form.newPassword = '';
        this.isModifyPassword = false;
        this.$message.success('密码修改成功');
      } catch (error) {
        this.$message.error(error?.message || '修改密码失败');
      }
    },
    imageUpload({ base64 }) {
      if (!this.isEditing) return;
      this.form.photo = base64;
    },
    async logOut() {
      try {
        await this.$confirm('确定退出当前账号吗？', '退出登录', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        });
        clearAuthSession();
        this.$message.success('已退出登录');
        this.$router.push('/login');
      } catch (error) {
        // User cancelled.
      }
    },
  },
};
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
  border-left: 4px solid #3a86ff;
  border-radius: 10px;
  border: 1px solid #65676c;
  padding: 0 20px 20px 20px;
}

.downPart {
  background-color: #f8f9fa;
  border-left: 4px solid #219ebc;
  border-radius: 10px;
  border: 1px solid #65676c;
  padding: 0 20px 20px 20px;
}

.section-title {
  display: flex;
  justify-content: left;
  align-items: center;
}

.rightPart {
  flex: 3;
  display: flex;
  height: 50%;
  flex-direction: column;
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
  margin: 0 auto 1rem auto;
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

.modify {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.passwordButton {
  background-color: transparent;
  border-radius: 4px;
  border-color: #286d25;
  color: #286d25;
}

.button {
  display: flex;
  justify-content: center;
  margin: 1rem;
}

.functionalButtons {
  display: flex;
  justify-content: center;
  margin: 1rem;
}

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
  color: #67606f;
}
</style>

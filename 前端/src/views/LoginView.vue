<template>
  <div id="Login">
    <div class="login-form">
      <div class="login-header">
        <img src="@/assets/logo.png" alt="Logo" class="login-logo" />
        <h2 class="login-title">{{ isRegistering ? '用户注册' : '用户登录' }}</h2>
      </div>

      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="loginRules"
        @keyup.enter.native="handleSubmit"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            prefix-icon="el-icon-user"
            :placeholder="isRegistering ? '请输入用户名' : '请输入用户名'"
            class="custom-input"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            prefix-icon="el-icon-lock"
            type="password"
            show-password
            :placeholder="isRegistering ? '请输入密码' : '请输入密码'"
            class="custom-input"
          />
        </el-form-item>

        <template v-if="isRegistering">
          <div class="inline-form-items">
            <el-form-item label="邮箱" class="inline-form-item" prop="email">
              <el-input
                v-model="loginForm.email"
                prefix-icon="el-icon-message"
                class="custom-input"
              />
            </el-form-item>
            <el-form-item label="手机号" class="inline-form-item" prop="phone">
              <el-input
                v-model="loginForm.phone"
                prefix-icon="el-icon-phone"
                class="custom-input"
              />
            </el-form-item>
          </div>
        </template>

        <div class="login-options">
          <el-button type="text" @click="toggleForm" class="login-option">
            {{ isRegistering ? '已有账号？去登录' : '没有账号？立即注册' }}
          </el-button>
        </div>

        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleSubmit" :loading="loading">
            {{ isRegistering ? '立即注册' : '立即登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isRegistering: false,
      loading: false,
      loginForm: {
        username: '',
        password: '',
        email: '',
        phone: ''
      },
      loginRules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      }
    };
  },
  methods: {
    handleSubmit() {
      this.$refs.loginForm.validate((valid) => {
        if (!valid) {
          return;
        }

        this.loading = true;
        setTimeout(() => {
          this.loading = false;
          if (this.isRegistering) {
            this.$message.success('注册成功！');
            this.$refs.loginForm.resetFields();
            this.isRegistering = false;
            return;
          }

          this.$message.success('登录成功！');
          this.$router.push('/analyses');
        }, 1000);
      });
    },
    toggleForm() {
      this.isRegistering = !this.isRegistering;
      this.$nextTick(() => {
        this.$refs.loginForm.clearValidate();
      });
    }
  }
};
</script>

<style scoped>
#Login {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
  position: relative;
  margin: 0;
  padding: 0;
}

.login-form {
  width: min(92vw, 520px);
  height: auto;
  padding: 24px;
  background: #fff;
  box-sizing: border-box;
  border: 1px solid #dfe4ea;
  border-radius: 12px;
}

.login-header {
  text-align: center;
  margin-bottom: 15px;
}

.login-logo {
  width: 80px;
  height: auto;
  margin-bottom: 10px;
}

.login-title {
  margin: 0;
  color: #2c2c2c;
  font-size: 20px;
  font-weight: 500;
}

.custom-input :deep(.el-input__inner) {
  height: 40px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.custom-input :deep(.el-input__inner):focus {
  border-color: #2c6d62;;
  box-shadow: 0 0 0 2px rgba(119, 247, 168, 0.15);
}

.inline-form-items {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.inline-form-item :deep(.el-form-item__label) {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.login-options {
  display: flex;
  justify-content: center;
  margin: 15px 0;
}

.login-option {
  color: #666;
  font-size: 14px;
  transition: color 0.3s ease;
}

.login-option:hover {
  color: #2c6d62;;
}

.login-btn {
  width: 100%;
  height: 40px;
  background: #2c6d4b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  transition: background 0.3s ease;
}

.login-btn:hover {
  background: #4ab67e;
}

@media (max-width: 480px) {
  .login-form {
    padding: 15px;
  }
}
</style>

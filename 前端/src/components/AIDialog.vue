<template>
  <div>
    <!-- 悬浮按钮 -->
    <button v-if="!isDialogOpen" id="toggle-dialog" class="toggle-button" @click="openDialog">
      <span class="button-text">AI小助手</span>
    </button>
    <!-- 人工智能对话框（侧边栏） -->
    <div :class="['dialog', { open: isDialogOpen }]">
      <div class="dialog-header">
        <div class="title">
          <h4>眼科智能小助手</h4>
        </div>
        <button id="close-dialog" class="close-button" @click="closeDialog">
          &times;
        </button>
      </div>
      <div class="dialog-content" id="dialog-content">
        <div v-for="(message, index) in conversationHistory" :key="index"
          :class="message.role === 'user' ? 'user-message-wrapper' : 'answer-wrapper'">
          <div :class="message.role === 'user' ? 'user-message' : 'answer'"
            v-html="message.role === 'assistant' && message.isTyping ? message.currentPart : message.content">
          </div>
        </div>
        <div v-if="isLoading && !hasAnswerTyping" class="loading dot-dance"></div>
      </div>
      <div class="input-section">
        <div class="shortcut-buttons">
          <div v-for="(content, index) in shortcutButtons" :key="index">
            <button @click="getExternalMessage(index)">{{ content }}</button>
          </div>
        </div>
        <div class="user-input">
          <input type="text" v-model="userInput" placeholder="输入你的消息" @keydown.enter="sendMessageByInput" />
          <button :disabled="!canSendMessage || isLoading || hasAnswerTyping" @click="sendMessageByInput">
            <span class="button-icon">
              <span v-if="!(isLoading || hasAnswerTyping)" class="el-icon-top"></span>
              <span v-else class="spinner"></span>
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { getApiUrl } from '@/api/config'
export default {
  props: {
    shortcutButtons: {
      type: Array,
      default: () => []
    },
    shortcutFunctions: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      isDialogOpen: false,
      userInput: "",
      conversationHistory: [],
      isLoading: false,
      canSendMessage: false,
      hasAnswerTyping: false,
    };
  },
  watch: {
    userInput(newValue) {
      // if (!(this.isLoading || this.hasAnswerTyping)) {
      this.canSendMessage = newValue.trim() !== "";
      // }
    },
  },
  methods: {
    openDialog() {
      this.isDialogOpen = true;
      this.$emit('open');
    },
    closeDialog() {
      this.isDialogOpen = false;
      this.$emit('close')
    },
    //这里用于获取外部函数数据并得到外部传送的答案
    async getExternalMessage(index) {
      this.isLoading = true;
      this.conversationHistory.push({ role: "user", content: this.shortcutButtons[index] });
      setTimeout(() => {
        this.scrollToBottom();
      }, 1);
      try {
        const functionNum = this.shortcutFunctions.length;
        if (functionNum === 0) {
          this.setAnswer("您还未提供外部函数接口,请重新设置!");
        } else if (functionNum < index) {
          this.setAnswer("未在提供的函数中找到想要的接口,请重新设置");
        } else {
          const functionName = this.shortcutFunctions[index];
          // 检查该函数名对应的函数是否存在
          if (typeof this.$parent[functionName] === 'function') {
            const result = await this.$parent[functionName]();
            const processedAnswer = this.processAnswer(result);
            this.setAnswer(processedAnswer);
          } else {
            this.setAnswer(`未在父组件中找到名为 ${functionName} 的函数不存在`);
          }
        }
        this.isLoading = false;
        await this.typeAnswer(this.conversationHistory.length - 1);
      } catch (error) {
        console.error("获取答案出错:", error);
        // 显示错误信息
        this.isLoading = false;
        this.conversationHistory.push({
          role: "error",
          content: "获取答案时出错",
        });
      }
    },
    sendMessageByInput() {
      if (!this.canSendMessage || this.isLoading || this.hasAnswerTyping) return;
      const message = this.userInput.trim();
      if (message === "") return;
      this.canSendMessage = false;
      // 显示用户消息
      this.conversationHistory.push({ role: "user", content: message });
      this.userInput = "";
      this.displayAnswer(message)
    },
    async displayAnswer(message) {
      setTimeout(() => {
        this.scrollToBottom();
      }, 1);
      this.isLoading = true;
      this.hasAnswerTyping = false;
      try {
        // 获取答案
        const answer = await this.getAnswer(message);
        // 处理格式
        const processedAnswer = this.processAnswer(answer);
        // 准备以打字机效果显示答案
        this.setAnswer(processedAnswer);
        this.hasAnswerTyping = true;
        this.isLoading = false;
        await this.typeAnswer(this.conversationHistory.length - 1);
      } catch (error) {
        console.error("获取答案出错:", error);
        // 显示错误信息
        this.conversationHistory.push({
          role: "error",
          content: "获取答案时出错",
        });
        this.isLoading = false;
      } finally {
        this.hasAnswerTyping = false;
        const message = this.userInput.trim();
        if (message != "")
          this.canSendMessage = true;
        else this.canSendMessage = false;
      }
    },
    setAnswer(answer) {
      this.conversationHistory.push({
        role: "assistant",
        content: answer,
        isTyping: true,
        currentPart: "",
      });
    },
    //向后端发送数据并获取原始答案
    async getAnswer(userMessage) {
      try {
        // 发送 POST 请求
        const response = await axios.post(getApiUrl("/aiQuestion"), {
          question: userMessage
        });
        // 返回响应数据
        console.log(response.data);
        return response.data.data;
      } catch (error) {
        console.error('请求出错:', error);
        // 可以根据需求返回默认值或者抛出错误
        return null;
      }
    },
    processAnswer(answer) {
      // 处理换行和加粗格式
      answer = answer.replace(/\n/g, '<br>');
      answer = answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // 替换短横线'-'为'·'
      answer = answer.replace(/-/g, '&#8226');
      // 在###和\n之间的内容用<h3></h3>包围
      answer = answer.replace(/###(.*?)(<br>)/g, '<h3>$1</h3>');
      // 处理连续换行符，只保留前两个
      answer = answer.replace(/(<br>){2,}/g, '<br>');
      return answer;
    },
    typeAnswer(index) {
      return new Promise((resolve) => {
        const message = this.conversationHistory[index];
        const typeNextChar = () => {
          if (message.currentPart.length < message.content.length) {
            message.currentPart += message.content[message.currentPart.length];
            setTimeout(typeNextChar, 5);
          } else {
            // 打字完成，移除打字机效果标识
            delete this.conversationHistory[index].isTyping;
            delete this.conversationHistory[index].currentPart;
            this.scrollToBottom();
            resolve();
          }
        };
        typeNextChar();
      });
    },
    scrollToBottom() {
      const dialogContent = this.$el.querySelector("#dialog-content");
      dialogContent.scrollTop = dialogContent.scrollHeight;
    },
  },
};
</script>

<style scoped>
/* 悬浮按钮样式 */
.toggle-button {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1001;
  padding: 20px 10px;
  background-color: #7ee6c2;
  color: #474747;
  border: none;
  border-top-right-radius: 50px;
  border-bottom-right-radius: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  width: 20px;
}

.toggle-button:hover {
  background-color: #74d4b2;
}

.button-text {
  margin-right: 5px;
}

.icon {
  font-size: 18px;
}

/* 对话框（侧边栏）样式 */
.dialog {
  position: absolute;
  left: -100%;
  width: 100%;
  height: 100%;
  background: #f0fffd;
  border-right: 1px solid #ccc;
  border-top-right-radius: 15px;
  border-bottom-right-radius: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: left 0.3s ease;
}

.dialog.open {
  left: 0;
}

.title {
  width: 90%;
  text-align: center;
  color: #4c6f68;
}

.dialog-header {
  height: 8;
  padding: 15px;
  background-color: #d4fdf7;
  border-top-right-radius: 15px;
  border-bottom-right-radius: 15px;
  border-bottom: 1px solid #b3d5e9;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #e0e0e0;
}

.close-button:hover {
  color: #ffffff;
}

.dialog-content {
  padding: 15px;
  overflow-y: auto;
  height: 63%;
}

.input-section {
  border-top: 1px solid #d2dae2;
}

.shortcut-buttons {
  width: 100%;
  height: 35px;
  padding-bottom: 3px;
  /* border-top:2px solid rgb(245, 249, 252); */
  display: flex;
  align-items: center;
  border-bottom: 1px solid #d2dae2;
}

.shortcut-buttons button {
  border: 0.5px solid rgb(190, 190, 190);
  border-radius: 5px;
  padding-top: 5px;
  padding-bottom: 5px;
  margin-left: 3px;
  cursor: pointer;
  color: rgb(114, 114, 114);
  background-color: rgb(255, 255, 255);
}

.shortcut-buttons button:hover {
  color: #4c6f68;
  background-color: rgb(255, 255, 255);
}

.user-input {
  /* width:100%; */
  height: 30%;
  padding: 15px;
  display: flex;
  background-color: #f5f9fc;
  border-bottom: 1px solid #d2dae2;
}

.user-input input {
  width: calc(100% - 80px);
  padding: 10px;
  margin-right: 10px;
  border: 1px solid #ccc;
  border-radius: 20px;
}

.user-input button {
  padding: 10px;
  color: white;
  font-size: 30px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.user-input button:disabled {
  background-color: #ccc;
}

.user-input button:not(:disabled) {
  background-color: #4c6f68;
}

.button-icon {
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.el-icon-top {
  transform: scaleX(1.3);
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 抖动的省略号样式 */
.dot-dance::after {
  content: "";
  animation: dot-dance 1.5s infinite linear;
  text-align: center;
  font-size: 12px;
  padding-left: 5px;
  border-radius: 5px;
  background-color: #8ac9bc;
  /* 设置行高，让显示更美观，可根据需求调整 */
  line-height: 1;
}

@keyframes dot-dance {
  0% {
    content: "正在分析.";
  }

  33% {
    content: "正在分析..";
  }

  66% {
    content: "正在分析...";
  }

  100% {
    content: "正在分析.";
  }
}

/* 用户消息包裹样式 */
.user-message-wrapper {
  text-align: right;
  margin-bottom: 10px;
}

/* 用户消息样式 */
.user-message {
  background-color: #ddfaf4;
  border-radius: 8px;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.05);
  font-family: 'Open Sans', sans-serif;
  font-size: 16px;
  color: #333;
  padding: 8px;
  display: inline-block;
  max-width: 80%;
  text-align: left;
}

/* AI 消息包裹样式 */
.answer-wrapper {
  text-align: left;
  margin-bottom: 10px;
}

/* AI 消息样式 */
.answer {
  background-color: #d4fdf7;
  border-radius: 8px;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.05);
  font-family: 'Open Sans', sans-serif;
  font-size: 16px;
  color: #333;
  padding: 8px;
  display: inline-block;
  max-width: 80%;
}
</style>
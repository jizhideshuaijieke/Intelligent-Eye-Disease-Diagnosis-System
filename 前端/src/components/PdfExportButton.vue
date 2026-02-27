<template>
  <el-button type="primary" @click="generatePDF" class="export-button" icon="el-icon-document-checked">
    导出PDF
  </el-button>
</template>

<script>
import { PDFDocument } from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import { saveAs } from 'file-saver';

export default {
  props: {
    formData: {
      type: Object,
      required: true
    }
  },
  methods: {
    async generatePDF() {
      try {
        // 加载PDF模板
        const templateUrl = '/template.pdf';
        //链式调用，将模板转为字节流
        const existingPdfBytes = await fetch(templateUrl).then(res => res.arrayBuffer());
        // 创建PDF文档并注册字体
        const pdfDoc = await PDFDocument.load(existingPdfBytes);
        pdfDoc.registerFontkit(fontkit);

        // 嵌入中文字体(PDF默认winansi，不支持中文字符)
        // 当使用embedFont嵌入字体时，pdf-lib会：
        // 解析字体文件的字符映射表（CMAP）
        // 将Unicode字符转换为字体内部的字形索引
        // 生成新的字体描述符覆盖WinAnsi编码
        // 在PDF中嵌入字体子集（仅包含实际使用的字符）
        const fontBytes = await fetch('/fzsongti.ttf').then(res => res.arrayBuffer());
        const customFont = await pdfDoc.embedFont(fontBytes);

        // 获取表单字段并自动匹配
        const form = pdfDoc.getForm();
        const formData = this.formData;

        // 自动填充文本字段
        Object.keys(formData).forEach(fieldName => {
          if (fieldName.includes('Image')) return; // 跳过所有图片字段

          try {
            const field = form.getTextField(fieldName);
            field.setText(formData[fieldName]);
            field.updateAppearances(customFont);
          } catch (error) {
            console.warn(`未找到字段 ${fieldName} 或不是文本字段`);
          }
        });

        // 处理左右眼图片字段
        const handleImageField = async (formFieldName, pdfFieldName) => {
          if (formData[formFieldName]) {
            try {
              const imageField = form.getButton(pdfFieldName);
              // 解析Base64数据（假设是带MIME类型的data URL）
              const base64Data = this.formData[formFieldName];
              const matches = base64Data.match(/^data:(.+);base64,(.+)$/);

              if (!matches) {
                throw new Error('无效的Base64格式，请使用data URL格式');
              }

              const imageType = matches[1];
              const pureBase64 = matches[2];
              const byteString = atob(pureBase64);
              const byteArray = new Uint8Array(byteString.length);

              for (let i = 0; i < byteString.length; i++) {
                byteArray[i] = byteString.charCodeAt(i);
              }

              // 根据MIME类型嵌入图片
              let image;
              if (imageType === 'image/jpeg') {
                image = await pdfDoc.embedJpg(byteArray);
              } else if (imageType === 'image/png') {
                image = await pdfDoc.embedPng(byteArray);
              } else {
                throw new Error(`不支持的图片格式: ${imageType}`);
              }
              imageField.setImage(image);
            } catch (error) {
              console.warn(`图片字段 ${formFieldName} 处理失败:`, error);
              throw error; // 抛出错误以便外层捕获
            }
          }
        };

        await handleImageField('leftEyeImageBase64', 'leftEyeImageBase64_af_image');
        await handleImageField('rightEyeImageBase64', 'rightEyeImageBase64_af_image');

        // 保存PDF
        const pdfBytes = await pdfDoc.save();
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        saveAs(blob, `${this.formData.name}_检查报告.pdf`);

      } catch (error) {
        this.$message.error('生成PDF失败,请稍后重试');
      }
    },
  }
}
</script>

<style scoped>
.export-button {
  padding: 10px 20px;
  transition: all 0.3s;
  background-color: #7ee6c2;
  border-color: #67606F;
}

.export-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
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
      required: true,
    },
  },
  methods: {
    async generatePDF() {
      this.$emit('before-export');

      try {
        const templateUrl = '/template.pdf';
        const existingPdfBytes = await fetch(templateUrl).then((res) => res.arrayBuffer());
        const pdfDoc = await PDFDocument.load(existingPdfBytes);
        pdfDoc.registerFontkit(fontkit);

        const fontBytes = await fetch('/fzsongti.ttf').then((res) => res.arrayBuffer());
        const customFont = await pdfDoc.embedFont(fontBytes);

        const form = pdfDoc.getForm();
        const formData = this.formData || {};

        Object.keys(formData).forEach((fieldName) => {
          if (fieldName.includes('Image')) return;
          try {
            const field = form.getTextField(fieldName);
            field.setText(String(formData[fieldName] ?? ''));
            field.updateAppearances(customFont);
          } catch (error) {
            console.warn(`未找到字段 ${fieldName} 或字段类型不匹配`, error);
          }
        });

        const handleImageField = async (formFieldName, pdfFieldName) => {
          const base64Data = formData[formFieldName];
          if (!base64Data) return;

          const imageField = form.getButton(pdfFieldName);
          const matches = String(base64Data).match(/^data:(.+);base64,(.+)$/);
          if (!matches) {
            throw new Error(`字段 ${formFieldName} 不是有效的 Base64 data URL`);
          }

          const imageType = matches[1];
          const pureBase64 = matches[2];
          const byteString = atob(pureBase64);
          const byteArray = new Uint8Array(byteString.length);
          for (let i = 0; i < byteString.length; i += 1) {
            byteArray[i] = byteString.charCodeAt(i);
          }

          let image;
          if (imageType === 'image/jpeg' || imageType === 'image/jpg') {
            image = await pdfDoc.embedJpg(byteArray);
          } else if (imageType === 'image/png') {
            image = await pdfDoc.embedPng(byteArray);
          } else {
            throw new Error(`不支持的图片格式: ${imageType}`);
          }
          imageField.setImage(image);
        };

        await handleImageField('leftEyeImageBase64', 'leftEyeImageBase64_af_image');
        await handleImageField('rightEyeImageBase64', 'rightEyeImageBase64_af_image');

        const pdfBytes = await pdfDoc.save();
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        const fileName = `${formData.name || '病例'}_检查报告.pdf`;
        saveAs(blob, fileName);

        this.$message.success('PDF 导出成功');
        this.$emit('export-success');
      } catch (error) {
        console.error('PDF 导出失败:', error);
        this.$message.error('生成PDF失败，请稍后重试');
        this.$emit('export-error', error);
      }
    },
  },
};
</script>

<style scoped>
.export-button {
  padding: 10px 20px;
  transition: all 0.3s;
  background-color: #7ee6c2;
  border-color: #67606f;
}

.export-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>

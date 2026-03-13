# 智慧眼疾诊断系统

一个用于眼科辅助诊断的前后端分离项目，入围大学生服务外包大赛省赛，支持眼底图像分析、OCT 分层、病例管理与统计可视化。

## 项目简介

一个面向眼科辅助诊断场景的智能系统，目标是在“诊断效率”和“临床可解释性”之间取得平衡。系统围绕真实就诊流程设计，整合眼底图像分析、OCT 分层、病灶标注、病例管理、PDF 报告导出与统计可视化，形成从“图像上传 -> AI 分析 -> 医生复核 -> 病例归档 -> 数据统计”的闭环体验。

项目支持浏览器端完整演示：模型服务可用时返回真实分割图和概率结果。


## 技术选型

1. **前端框架选择**：使用 Vue 2 + Vue Router 构建单页应用，配合 Element UI 完成业务表单、上传与交互组件开发。
2. **数据请求与接口管理**：使用 Axios 统一封装 API 调用，对接 FastAPI 业务后端；图像分析请求由后端统一转发至模型接口，形成稳定的前后端调用链路。
3. **可视化方案选型**：使用 ECharts 实现折线图、饼图、柱状图联动展示，覆盖月度趋势、疾病占比和年龄段分布等核心统计场景。
4. **后端与数据层选择**：使用 FastAPI 提供业务接口，结合 SQLAlchemy 访问 MySQL，存储账号、病例与统计分析所需的结构化业务数据。
5. **模型服务选型**：使用 Flask + PyTorch 提供推理服务，结合 OpenCV、Pillow 完成图像预处理与结果后处理，支持眼底分割与 OCT 分层任务，并通过 HTTP 接口与业务后端集成。

## 演示

- 眼底血管分割与 OCT 分层输出

  <p align="center"><img src="docs/images/模型分割演示.png" alt="模型分割演示" width="85%" /></p>

- 图像增强/对比/亮度  

  <p align="center">
    <img src="docs/images/增强放大演示.png" alt="增强放大演示" width="42%" />
    <img src="docs/images/亮度调节演示.png" alt="亮度调节演示" width="42%" />
  </p>

- 支持医生在前端进行病灶标注 

  <p align="center"><img src="docs/images/眼底手动绘制.png" alt="眼底手动绘制" width="85%" /></p>

- 病例导出前触发 AI 分析流程  

  <p align="center"><img src="docs/images/导出调用AI.png" alt="导出调用AI" width="85%" /></p>

- 病例统计图表和表格联动

  <p align="center"><img src="docs/images/疾病统计可视化.png" alt="疾病统计可视化" width="85%" /></p>

- 医生信息维护  

  <p align="center"><img src="docs/images/医生个人信息.png" alt="医生个人信息" height="100%" width="85%" /></p>

## 项目部署

### 安装前端依赖

```powershell
cd 前端
npm install
```

### 模型服务

```powershell
conda activate eye-model
cd 模型
python app.py
```

### 后端服务

```powershell
cd 后端
python main.py
```

### 前端服务

```powershell
cd 前端
npm run serve
```

### 前端生产构建

```powershell
cd 前端
npm run build
```

### 前端代码检查

```powershell
cd 前端
npm run lint
```

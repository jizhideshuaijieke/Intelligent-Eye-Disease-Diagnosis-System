import base64
import io
import os

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    from ietk import methods, util

    HAS_IETK = True
except Exception:
    HAS_IETK = False

from lib.pre_processing import my_PreProc
from model.main_model.model import InceptionDWConv2d, MetaNeXt
from model.oct_seg.model import UNet
from model.seg.model import LadderNet
from model.shivt.model import SHViT

app = Flask(__name__)
CORS(app)

# 设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 模型路径配置
MODEL_DIR = os.getenv('MODEL_DIR', 'model_param')
MODEL_PATHS = {
    'main': os.getenv('MAIN_MODEL_PATH', os.path.join(MODEL_DIR, 'best_model.pth')),
    'sub': os.getenv('SUB_MODEL_PATH', os.path.join(MODEL_DIR, 'son_best_model.pth')),
    'vessel': os.getenv('VESSEL_MODEL_PATH', os.path.join(MODEL_DIR, 'seg_best_model.pth')),
    'oct': os.getenv('OCT_MODEL_PATH', os.path.join(MODEL_DIR, 'oct_seg_best_model.pth')),
}


def load_models():
    # 主分类网络
    main_model = MetaNeXt(
        depths=(3, 3, 9, 3),
        dims=(96, 192, 384, 768),
        token_mixers=InceptionDWConv2d,
        num_classes=8,
    ).to(device)
    main_ckpt = torch.load(MODEL_PATHS['main'], map_location=device, weights_only=False)
    main_model.load_state_dict(main_ckpt['model_state_dict'])
    main_model.eval()

    # 子分类网络
    sub_model = SHViT(num_classes=5).to(device)
    sub_ckpt = torch.load(MODEL_PATHS['sub'], map_location=device, weights_only=False)
    sub_model.load_state_dict(sub_ckpt['model_state_dict'])
    sub_model.eval()

    # 血管分割网络
    vessel_model = LadderNet(inplanes=1, num_classes=2, layers=3, filters=16).to(device)
    vessel_ckpt = torch.load(MODEL_PATHS['vessel'], map_location=device, weights_only=False)
    vessel_model.load_state_dict(vessel_ckpt['net'])
    vessel_model.eval()

    # OCT 分层模型
    oct_model = UNet(n_channels=1, n_classes=9).to(device)
    oct_ckpt = torch.load(MODEL_PATHS['oct'], map_location=device, weights_only=False)
    oct_model.load_state_dict(oct_ckpt['model_state_dict'])
    oct_model.eval()

    return main_model, sub_model, vessel_model, oct_model


main_model, sub_model, vessel_model, oct_model = load_models()

main_transform = transforms.Compose(
    [
        transforms.Resize((640, 640)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

oct_transform = transforms.Compose(
    [
        transforms.Resize((640, 640)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ]
)


@app.route('/api/fundus_analysi', methods=['GET'])
def fundus_analysi():
    # 保持与前端健康检查路径一致（原项目拼写即为 fundus_analysi）
    return jsonify({'success': True})


@app.route('/api/fundus_analysis', methods=['POST'])
def fundus_analysis():
    try:
        image_data = request.json.get('image') if request.json else None
        if not image_data:
            return jsonify({'error': '没有提供图像数据'}), 400

        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]

        # 关键修复：强制转 RGB，避免灰度图导致 Normalize 的通道广播错误。
        image = Image.open(io.BytesIO(base64.b64decode(image_data))).convert('RGB')

        # 分类输入
        image_tensor = main_transform(image).unsqueeze(0).to(device)

        # 血管分割输入（预处理后单通道）
        vessel_image = image
        w, h = vessel_image.size
        new_w = max(8, (w // 8) * 8)
        new_h = max(8, (h // 8) * 8)
        vessel_image = vessel_image.resize((new_w, new_h))

        img_np = np.array(vessel_image)
        img_np = np.transpose(img_np, (2, 0, 1))  # [H,W,3] -> [3,H,W]
        img_np = np.expand_dims(img_np, axis=0)  # [3,H,W] -> [1,3,H,W]
        img_np = my_PreProc(img_np)  # -> [1,1,H,W]
        vessel_image_tensor = torch.from_numpy(img_np).float().to(device)

        with torch.no_grad():
            outputs = main_model(image_tensor)
            outputs = torch.sigmoid(outputs)
            probabilities = outputs[0].cpu().numpy()

            if probabilities[1] > 0.7:
                sub_outputs = sub_model(image_tensor)
                sub_probabilities = sub_outputs[0].cpu().numpy()
            else:
                sub_probabilities = np.zeros(5, dtype=np.float32)

            vessel_output = vessel_model(vessel_image_tensor)
            prob_map = torch.softmax(vessel_output, dim=1)
            vessel_pred = prob_map[:, 1].cpu().numpy()

        # 图像增强（展示用）
        if HAS_IETK:
            img_np_enhance = np.array(image).astype(np.float32) / 255.0
            I, fg = util.center_crop_and_get_foreground_mask(img_np_enhance)
            enhanced_img = methods.brighten_darken(I, 'A+B+X', focus_region=fg)
            enhanced_img = methods.sharpen(enhanced_img, bg=~fg)
            enhanced_img = np.clip(enhanced_img, 0, 1)
            enhanced_img = Image.fromarray((enhanced_img * 255).astype(np.uint8))
        else:
            bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l_channel)
            lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
            enhanced_bgr = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
            enhanced_img = Image.fromarray(enhanced_rgb)

        enhanced_buffer = io.BytesIO()
        enhanced_img.save(enhanced_buffer, format='PNG')
        enhanced_base64 = 'data:image/png;base64,' + base64.b64encode(enhanced_buffer.getvalue()).decode()

        prob_img = Image.fromarray((vessel_pred[0] * 255).astype(np.uint8))
        prob_buffer = io.BytesIO()
        prob_img.save(prob_buffer, format='PNG')
        prob_base64 = 'data:image/png;base64,' + base64.b64encode(prob_buffer.getvalue()).decode()

        main_classes = [
            '其他疾病',
            '糖尿病性视网膜病变',
            '病理性近视',
            '白内障',
            '老年性黄斑部病变',
            '青光眼',
            '高血压视网膜病变',
            '正常',
        ]
        sub_classes = [
            '正常',
            '轻度非增殖性糖网病变',
            '中度非增殖性糖网病变',
            '重度非增殖性糖网病变',
            '增殖性糖网病变',
        ]

        return jsonify(
            {
                'main_classification': {
                    'probabilities': {cls: float(prob) for cls, prob in zip(main_classes, probabilities)}
                },
                'sub_classification': {
                    'probabilities': {cls: float(prob) for cls, prob in zip(sub_classes, sub_probabilities)}
                },
                'vessel_segmentation': {
                    'probability_map': prob_base64,
                },
                'enhanced_image': enhanced_base64,
            }
        )

    except Exception as e:
        print(f'眼底分析错误: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/oct_segmentation', methods=['POST'])
def oct_segmentation():
    try:
        image_data = request.json.get('image') if request.json else None
        if not image_data:
            return jsonify({'error': '没有提供图像数据'}), 400

        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]

        image = Image.open(io.BytesIO(base64.b64decode(image_data))).convert('L')
        original_image = image.copy()
        image_tensor = oct_transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = oct_model(image_tensor)
            pred = output.argmax(dim=1).squeeze().cpu().numpy()

        original_np = np.array(original_image.resize((640, 640)))
        if len(original_np.shape) == 2:
            original_np = cv2.cvtColor(original_np, cv2.COLOR_GRAY2BGR)

        overlay = np.zeros((640, 640, 3), dtype=np.uint8)

        colors = [
            [0, 0, 0],
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
            [255, 255, 0],
            [255, 0, 255],
            [0, 255, 255],
            [128, 0, 0],
            [0, 128, 0],
        ]

        for i in range(9):
            mask = pred == i
            overlay[mask] = colors[i]

        result = cv2.addWeighted(original_np, 0.7, overlay, 0.3, 0)

        result_img = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        result_buffer = io.BytesIO()
        result_img.save(result_buffer, format='PNG')
        result_base64 = 'data:image/png;base64,' + base64.b64encode(result_buffer.getvalue()).decode()

        return jsonify({'segmentation_result': result_base64})

    except Exception as e:
        print(f'OCT 分割错误: {str(e)}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    host = os.getenv('MODEL_HOST', '0.0.0.0')
    port = int(os.getenv('MODEL_PORT', '5000'))
    app.run(host=host, port=port)

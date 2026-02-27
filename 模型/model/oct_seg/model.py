import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import os
import glob
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from torchvision import transforms


# 定义U-Net模型
class UNet(nn.Module):
    def __init__(self, n_channels=1, n_classes=9):
        super(UNet, self).__init__()

        # 编码器部分
        self.enc1 = self.conv_block(n_channels, 16)
        self.enc2 = self.conv_block(16, 32)
        self.enc3 = self.conv_block(32, 64)
        self.enc4 = self.conv_block(64, 128)
        self.enc5 = self.conv_block(128, 256)

        # 解码器部分
        self.up4 = self.up_conv(256, 128)
        self.dec4 = self.conv_block(256, 128)

        self.up3 = self.up_conv(128, 64)
        self.dec3 = self.conv_block(128, 64)

        self.up2 = self.up_conv(64, 32)
        self.dec2 = self.conv_block(64, 32)

        self.up1 = self.up_conv(32, 16)
        self.dec1 = self.conv_block(32, 16)

        self.final = nn.Conv2d(16, n_classes, kernel_size=1)

    def conv_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def up_conv(self, in_ch, out_ch):
        return nn.ConvTranspose2d(in_ch, out_ch, kernel_size=2, stride=2)

    def forward(self, x):
        # 编码器路径
        enc1 = self.enc1(x)
        enc2 = self.enc2(F.max_pool2d(enc1, 2))
        enc3 = self.enc3(F.max_pool2d(enc2, 2))
        enc4 = self.enc4(F.max_pool2d(enc3, 2))
        enc5 = self.enc5(F.max_pool2d(enc4, 2))

        # 解码器路径
        dec4 = self.up4(enc5)
        dec4 = torch.cat([dec4, enc4], dim=1)
        dec4 = self.dec4(dec4)

        dec3 = self.up3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.dec3(dec3)

        dec2 = self.up2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.dec2(dec2)

        dec1 = self.up1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.dec1(dec1)

        return self.final(dec1)
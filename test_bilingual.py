#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_bilingual_subtitle():
    """测试双语字幕功能"""
    
    # 测试数据
    data = {
        "video_id": "Am54LhN2NLk",
        "audio_type": "original",
        "hardcode_subtitles": True,
        "subtitle_type": "bilingual",
        "subtitle_style": {
            "font_name": "Arial",
            "font_size": 20,
            "primary_color": "&Hffffff",
            "outline_color": "&H000000",
            "back_color": "&H000000",
            "outline_width": 2,
            "shadow_depth": 1,
            "alignment": 2,
            "margin_v": 30,
            "auto_scale": True,
            "min_font_size": 14,
            "max_font_size": 28,
            "bilingual": {
                "secondary_font_name": "SimHei",
                "secondary_font_size": 24,
                "secondary_color": "&Hcccccc",
                "vertical_spacing": 5
            }
        }
    }
    
    print("测试双语字幕配置:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 发送请求
    try:
        response = requests.post(
            "http://localhost:10310/video_preview",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data, ensure_ascii=False)
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n任务ID: {result.get('task_id')}")
            print(f"文件名: {result.get('filename')}")
            print(f"下载URL: {result.get('download_url')}")
        
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_bilingual_subtitle()

#!/usr/bin/env python3
"""
测试视频时长修复
"""

import os
import subprocess
from src.service.video_synthesis.video_preview import _create_video_with_moviepy, _create_video_with_hardcoded_subtitles

def get_video_duration(video_path):
    """获取视频时长"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"获取视频时长失败: {e}")
        return None

def test_video_duration():
    """测试视频时长"""
    
    print("🧪 测试视频时长修复")
    print("=" * 50)
    
    # 检查测试文件是否存在
    test_files = {
        "video": "output/Am54LhN2NLk.mp4",
        "voice": "output/Am54LhN2NLk_zh.wav", 
        "bg": "output/Am54LhN2NLk_bg.wav",
        "srt": "output/Am54LhN2NLk_zh_merged.srt"
    }
    
    # 检查文件存在性
    for name, path in test_files.items():
        if os.path.exists(path):
            duration = get_video_duration(path) if name == "video" else None
            print(f"✅ {name}: {path} {'(时长: ' + str(duration) + 's)' if duration else ''}")
        else:
            print(f"❌ {name}: {path} (文件不存在)")
    
    print("\n📝 说明:")
    print("- 如果所有文件都存在，可以测试视频合成")
    print("- 如果缺少文件，请先完成完整的翻译流程")
    print("- 修复后的代码应该保持原始视频时长")

if __name__ == "__main__":
    test_video_duration()

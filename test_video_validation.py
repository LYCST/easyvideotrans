#!/usr/bin/env python3
"""
测试视频文件有效性检查功能
"""

import os
import sys
import tempfile
import subprocess
from src.utils.video_validator import validate_video_file

def test_video_validation():
    """测试视频文件有效性检查功能"""
    
    print("🧪 测试视频文件有效性检查功能")
    print("=" * 60)
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"临时目录: {temp_dir}")
        
        # 测试1: 检查不存在的文件
        print("\n1️⃣ 测试不存在的文件")
        non_existent_file = os.path.join(temp_dir, "non_existent.mp4")
        is_valid, error = validate_video_file(non_existent_file)
        print(f"   文件: {non_existent_file}")
        print(f"   结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        print(f"   错误: {error}")
        
        # 测试2: 检查空文件
        print("\n2️⃣ 测试空文件")
        empty_file = os.path.join(temp_dir, "empty.mp4")
        with open(empty_file, 'wb') as f:
            pass  # 创建空文件
        is_valid, error = validate_video_file(empty_file)
        print(f"   文件: {empty_file}")
        print(f"   结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        print(f"   错误: {error}")
        
        # 测试3: 检查损坏的文件
        print("\n3️⃣ 测试损坏的文件")
        corrupted_file = os.path.join(temp_dir, "corrupted.mp4")
        with open(corrupted_file, 'wb') as f:
            f.write(b'This is not a valid video file')
        is_valid, error = validate_video_file(corrupted_file)
        print(f"   文件: {corrupted_file}")
        print(f"   结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        print(f"   错误: {error}")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成！")

if __name__ == "__main__":
    test_video_validation()

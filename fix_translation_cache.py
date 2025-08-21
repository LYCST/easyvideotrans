#!/usr/bin/env python3
"""
修复翻译缓存工具
用于清理缓存并重新翻译有问题的字幕
"""

import os
import json
import sys
from pathlib import Path

def check_translation_cache(video_id, cache_dir="./output/translation_cache"):
    """检查翻译缓存文件"""
    cache_file = os.path.join(cache_dir, f"{video_id}_gpt_gpt_oss_120b.json")
    
    if not os.path.exists(cache_file):
        print(f"❌ 缓存文件不存在: {cache_file}")
        return False
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        print(f"📋 检查翻译缓存: {cache_file}")
        print(f"   总条目数: {len(translations)}")
        
        # 检查是否有未翻译的英文内容
        english_entries = []
        for i, translation in enumerate(translations):
            # 简单的英文检测（包含常见英文单词）
            english_words = ['the', 'and', 'with', 'for', 'that', 'this', 'you', 'are', 'can', 'will', 'have', 'has', 'had']
            text_lower = translation.lower()
            if any(word in text_lower for word in english_words) and len(text_lower.split()) > 3:
                english_entries.append((i, translation))
        
        if english_entries:
            print(f"⚠️ 发现 {len(english_entries)} 个可能未翻译的条目:")
            for index, text in english_entries:
                print(f"   第 {index + 1} 行: {text[:50]}...")
            return True
        else:
            print("✅ 所有条目都已正确翻译")
            return False
            
    except Exception as e:
        print(f"❌ 读取缓存文件失败: {e}")
        return False

def clear_translation_cache(video_id, cache_dir="./output/translation_cache"):
    """清理翻译缓存"""
    cache_file = os.path.join(cache_dir, f"{video_id}_gpt_gpt_oss_120b.json")
    
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
            print(f"🗑️ 已删除缓存文件: {cache_file}")
            return True
        except Exception as e:
            print(f"❌ 删除缓存文件失败: {e}")
            return False
    else:
        print(f"⚠️ 缓存文件不存在: {cache_file}")
        return True

def fix_translation(video_id):
    """修复翻译问题"""
    print(f"🔧 开始修复视频 {video_id} 的翻译问题")
    print("=" * 60)
    
    # 1. 检查缓存
    has_issues = check_translation_cache(video_id)
    
    if has_issues:
        print(f"\n🔄 发现翻译问题，开始修复...")
        
        # 2. 清理缓存
        if clear_translation_cache(video_id):
            print(f"✅ 缓存清理完成")
            
            # 3. 提示用户重新翻译
            print(f"\n📝 请重新执行翻译操作:")
            print(f"   1. 访问 Web 界面: http://localhost:10310")
            print(f"   2. 输入视频 ID: {video_id}")
            print(f"   3. 选择翻译服务并点击 'Translate to Chinese'")
            print(f"   4. 系统将重新翻译所有内容")
            
            return True
        else:
            print(f"❌ 缓存清理失败")
            return False
    else:
        print(f"✅ 翻译缓存正常，无需修复")
        return True

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python fix_translation_cache.py <video_id>")
        print("示例: python fix_translation_cache.py Am54LhN2NLk")
        sys.exit(1)
    
    video_id = sys.argv[1]
    fix_translation(video_id)

if __name__ == "__main__":
    main()

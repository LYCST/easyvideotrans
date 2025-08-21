import os
import subprocess
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def is_video_file_valid(video_path: str) -> Tuple[bool, Optional[str]]:
    """
    检查视频文件是否有效
    
    Args:
        video_path: 视频文件路径
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if not os.path.exists(video_path):
        return False, "文件不存在"
    
    # 检查文件大小
    file_size = os.path.getsize(video_path)
    if file_size == 0:
        return False, "文件大小为0"
    
    # 使用FFmpeg检查视频文件完整性
    return _check_video_with_ffmpeg(video_path)


def _check_video_with_ffmpeg(video_path: str) -> Tuple[bool, Optional[str]]:
    """
    使用FFmpeg检查视频文件完整性
    
    Args:
        video_path: 视频文件路径
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    try:
        # 使用FFmpeg检查视频文件，不输出任何内容
        cmd = [
            'ffmpeg',
            '-v', 'quiet',  # 静默模式
            '-i', video_path,
            '-f', 'null',
            '-'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        
        if result.returncode == 0:
            return True, None
        else:
            error_msg = result.stderr.strip() if result.stderr else "FFmpeg检查失败"
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        return False, "FFmpeg检查超时"
    except FileNotFoundError:
        return False, "FFmpeg未安装或不在PATH中"
    except Exception as e:
        return False, f"FFmpeg检查异常: {str(e)}"


def get_video_info(video_path: str) -> Optional[dict]:
    """
    获取视频文件信息
    
    Args:
        video_path: 视频文件路径
        
    Returns:
        Optional[dict]: 视频信息字典，包含时长、分辨率等
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            logger.warning(f"获取视频信息失败: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"获取视频信息异常: {e}")
        return None


def is_video_duration_valid(video_path: str, expected_duration: Optional[float] = None, 
                           tolerance: float = 10.0) -> Tuple[bool, Optional[str]]:
    """
    检查视频时长是否有效
    
    Args:
        video_path: 视频文件路径
        expected_duration: 期望的时长（秒），如果为None则不检查
        tolerance: 允许的误差范围（秒）
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    video_info = get_video_info(video_path)
    if not video_info:
        return False, "无法获取视频信息"
    
    try:
        # 获取视频时长
        duration_str = video_info.get('format', {}).get('duration')
        if not duration_str:
            return False, "无法获取视频时长"
        
        actual_duration = float(duration_str)
        
        if expected_duration is not None:
            if abs(actual_duration - expected_duration) > tolerance:
                return False, f"视频时长不匹配: 期望{expected_duration}秒，实际{actual_duration}秒"
        
        # 检查时长是否合理（大于0且小于24小时）
        if actual_duration <= 0:
            return False, "视频时长为0或负数"
        if actual_duration > 86400:  # 24小时
            return False, "视频时长超过24小时"
        
        return True, None
        
    except (ValueError, TypeError) as e:
        return False, f"解析视频时长失败: {str(e)}"


def validate_video_file(video_path: str, check_duration: bool = True, 
                       expected_duration: Optional[float] = None) -> Tuple[bool, Optional[str]]:
    """
    综合验证视频文件
    
    Args:
        video_path: 视频文件路径
        check_duration: 是否检查时长
        expected_duration: 期望的时长（秒）
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    # 基本文件检查
    is_valid, error = is_video_file_valid(video_path)
    if not is_valid:
        return False, error
    
    # 时长检查
    if check_duration:
        is_valid, error = is_video_duration_valid(video_path, expected_duration)
        if not is_valid:
            return False, error
    
    return True, None

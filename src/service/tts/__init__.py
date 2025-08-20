from .edge_tts import EdgeTTSClient
from .tts_client import TTSClient

# 检查 Python 版本和 TTS 兼容性
import sys
XTTS_AVAILABLE = False
XTTSv2Client = None

if sys.version_info >= (3, 10):
    try:
        from .xtts_v2_tts import XTTSv2Client
        XTTS_AVAILABLE = True
        print("Using XTTS v2 (Python 3.10+ compatible)")
    except ImportError as e:
        print(f"Warning: XTTS v2 not available due to import error: {e}")
    except Exception as e:
        print(f"Warning: XTTS v2 not available: {e}")
else:
    print("Warning: XTTS v2 requires Python 3.10 or higher. Current version: {}.{}".format(
        sys.version_info.major, sys.version_info.minor))

# 尝试导入兼容版本
XTTS_COMPATIBLE_AVAILABLE = False
XTTSv2CompatibleClient = None

try:
    from .xtts_v2_tts_compatible import XTTSv2CompatibleClient
    XTTS_COMPATIBLE_AVAILABLE = True
    print("Using XTTS v2 (compatible mode for Python 3.9)")
except ImportError as e:
    print(f"Warning: XTTS v2 compatible version not available: {e}")
except Exception as e:
    print(f"Warning: XTTS v2 compatible version not available: {e}")

__all__ = [
    "EdgeTTSClient",
    "TTSClient"
]

if XTTS_AVAILABLE:
    __all__.append("XTTSv2Client")
if XTTS_COMPATIBLE_AVAILABLE:
    __all__.append("XTTSv2CompatibleClient")


def get_tts_client(tts_vendor, character=None, **kwargs) -> TTSClient:
    """
    获取 TTS 客户端
    
    Args:
        tts_vendor: TTS 供应商 ('edge', 'xtts_v2')
        character: 语音角色（用于 edge TTS）
        **kwargs: 其他参数
            - reference_audio_path: 参考音频路径（用于 XTTS v2）
            - language: 目标语言（用于 XTTS v2）
            - model_name: 模型名称（用于 XTTS v2）
    """
    if tts_vendor == 'edge':
        return EdgeTTSClient(character=character)
    elif tts_vendor == 'xtts_v2':
        reference_audio_path = kwargs.get('reference_audio_path')
        language = kwargs.get('language', 'zh')
        model_name = kwargs.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2')
        
        # 优先使用 Python 3.10+ 兼容版本
        if XTTS_AVAILABLE:
            return XTTSv2Client(
                model_name=model_name,
                reference_audio_path=reference_audio_path,
                language=language
            )
        # 降级使用兼容版本
        elif XTTS_COMPATIBLE_AVAILABLE:
            print("Using XTTS v2 compatible mode (command line interface)")
            return XTTSv2CompatibleClient(
                model_name=model_name,
                reference_audio_path=reference_audio_path,
                language=language
            )
        else:
            if sys.version_info < (3, 10):
                raise ImportError("XTTS v2 requires Python 3.10 or higher. Current version: {}.{}".format(
                    sys.version_info.major, sys.version_info.minor))
            else:
                raise ImportError("XTTS v2 not available. Install with: pip install TTS==0.22.0")
    else:
        raise ValueError(f"Unknown TTS vendor: {tts_vendor}. Supported vendors: edge, xtts_v2")

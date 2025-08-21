from .edge_tts import EdgeTTSClient
from .fallback_tts import FallbackTTSClient
from .openai_tts import OpenAITTSClient
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

# 检查 CosyVoice2 可用性
COSYVOICE2_AVAILABLE = False
CosyVoice2Client = None

try:
    from .cosyvoice2_tts import CosyVoice2Client
    COSYVOICE2_AVAILABLE = True
    print("Using CosyVoice2")
except ImportError as e:
    print(f"Warning: CosyVoice2 not available: {e}")
except Exception as e:
    print(f"Warning: CosyVoice2 not available: {e}")

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
    "FallbackTTSClient",
    "OpenAITTSClient",
    "TTSClient"
]

if XTTS_AVAILABLE:
    __all__.append("XTTSv2Client")
if XTTS_COMPATIBLE_AVAILABLE:
    __all__.append("XTTSv2CompatibleClient")
if COSYVOICE2_AVAILABLE:
    __all__.append("CosyVoice2Client")


def get_tts_client(tts_vendor, character=None, **kwargs) -> TTSClient:
    """
    获取 TTS 客户端
    
    Args:
        tts_vendor: TTS 供应商 ('edge', 'openai', 'xtts_v2', 'cosyvoice2', 'fallback')
        character: 语音角色（用于 edge TTS）
        **kwargs: 其他参数
            - voice: 语音类型（用于 OpenAI TTS）
            - model: 模型名称（用于 OpenAI TTS）
            - instructions: 指令（用于 OpenAI TTS）
            - reference_audio_path: 参考音频路径（用于 XTTS v2 和 CosyVoice2）
            - language: 目标语言（用于 XTTS v2）
            - model_name: 模型名称（用于 XTTS v2 和 CosyVoice2）
            - speaker_name: 说话人名称（用于 CosyVoice2）
            - mode: 生成模式（用于 CosyVoice2）
            - instruction: 指令（用于 CosyVoice2）
            - fp16: 是否使用FP16精度（用于 CosyVoice2）
    """
    if tts_vendor == 'edge':
        return EdgeTTSClient(character=character)
    elif tts_vendor == 'openai':
        # For OpenAI, character maps to voice parameter
        voice = character or kwargs.get('voice', 'alloy')
        model = kwargs.get('model', 'tts-1')
        instructions = kwargs.get('instructions', None)
        return OpenAITTSClient(voice=voice, model=model, instructions=instructions)
    elif tts_vendor == 'fallback':
        return FallbackTTSClient(character=character)
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
    elif tts_vendor == 'cosyvoice2':
        if not COSYVOICE2_AVAILABLE:
            raise ImportError("CosyVoice2 not available. Please install CosyVoice2 first.")
        
        model_path = kwargs.get('model_path', 'pretrained_models/CosyVoice2-0.5B')
        reference_audio_path = kwargs.get('reference_audio_path')
        speaker_name = kwargs.get('speaker_name', '')
        mode = kwargs.get('mode', 'zero_shot')
        instruction = kwargs.get('instruction', '')
        load_jit = kwargs.get('load_jit', False)
        load_trt = kwargs.get('load_trt', False)
        load_vllm = kwargs.get('load_vllm', False)
        fp16 = kwargs.get('fp16', False)
        
        return CosyVoice2Client(
            model_path=model_path,
            reference_audio_path=reference_audio_path,
            speaker_name=speaker_name,
            mode=mode,
            instruction=instruction,
            load_jit=load_jit,
            load_trt=load_trt,
            load_vllm=load_vllm,
            fp16=fp16
        )
    else:
        print(f"Unknown TTS vendor '{tts_vendor}', using fallback TTS")
        return FallbackTTSClient(character=character)

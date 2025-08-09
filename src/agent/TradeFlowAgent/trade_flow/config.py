"""
配置管理
"""

import os
from typing import Union, Any, Dict
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_model_config() -> Union[str, LiteLlm]:
    """
    获取模型配置

    Returns:
        模型配置字符串或 LiteLlm 对象
    """
    model = os.getenv("MODEL", "gemini-2.0-flash")
    api_key = os.getenv("API_KEY", "")
    base_url = os.getenv("BASE_URL", None)
    temperature = float(os.getenv("TEMPERATURE", "0.7"))

    # 如果是 Gemini 模型，直接返回字符串
    if model.startswith("gemini"):
        return model

    # Claude 模型使用 LiteLlm
    if model.startswith("claude"):
        # 为 LiteLLM 格式化 Claude 模型名称
        litellm_model = f"anthropic/{model}"
    else:
        # 为 LiteLLM 格式化 OpenAI 模型名称
        litellm_model = f"openai/{model}"

    config: Dict[str, Any] = {
        "model": litellm_model,
        "api_key": api_key,
        "temperature": temperature,
    }

    # 如果有自定义 BASE_URL，添加到配置
    if base_url:
        config["api_base"] = base_url

    return LiteLlm(**config)  # type: ignore


    # 其他模型也使用 LiteLlm
    # return LiteLlm(model=model, api_key=api_key, temperature=temperature)  # type: ignore


def get_setting(key: str, default: Any = None) -> Any:
    """
    获取设置值
    
    Args:
        key: 设置键名
        default: 默认值
    
    Returns:
        设置值
    """
    return os.getenv(key, default)


# 应用配置
APP_NAME = "TradeFlow-Agent"
DEFAULT_USER_ID = "default_user"
DEFAULT_SESSION_ID = "default_session"

# Google Search API 配置
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")

# Tendata API 配置
TENDATA_API_KEY = os.getenv("TENDATA_API_KEY", "")
TENDATA_API_BASE_URL = os.getenv("TENDATA_API_BASE_URL", "https://open-api.tendata.cn")

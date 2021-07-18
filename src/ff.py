import os
from typing import Dict

_feature_flag_list = [
    "WALBOT_FEATURE_NEW_CONFIG",
]


class FF:
    """Feature flag"""

    @staticmethod
    def is_enabled(feature_flag: str) -> bool:
        if feature_flag not in _feature_flag_list:
            raise ValueError(f"Incorrect feature flag: {feature_flag}")
        value = os.getenv(feature_flag)
        return value in ("1", "ON")

    @staticmethod
    def get_list() -> Dict[str, str]:
        return {key: os.getenv(key) for key in _feature_flag_list}

import os
from typing import Dict


class FF:
    """Feature flag"""

    _feature_flag_list = [
        "WALBOT_FEATURE_NEW_CONFIG",
        "WALBOT_FEATURE_MARKOV_MONGO",
    ]

    @staticmethod
    def is_enabled(feature_flag: str) -> bool:
        """Get if feature flag is enabled"""
        if feature_flag not in FF._feature_flag_list:
            raise ValueError(f"Incorrect feature flag: {feature_flag}")
        value = (os.getenv(feature_flag) or "").upper()
        return value in ("1", "ON")

    @staticmethod
    def get_list() -> Dict[str, str]:
        """Get whole list of feature flags"""
        return {key: os.getenv(key) for key in FF._feature_flag_list}

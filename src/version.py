from src.ff import FF

CONFIG_VERSION = '0.0.35'
MARKOV_CONFIG_VERSION = '0.0.6'
if FF.is_enabled("WALBOT_FEATURE_NEW_CONFIG"):
    SECRET_CONFIG_VERSION = '0.1.0'
else:
    SECRET_CONFIG_VERSION = '0.0.2'

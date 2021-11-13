from src.info import BotInfo


def test_query_dependencies_info():
    bot_info = BotInfo()
    assert bot_info.query_dependencies_info() is not None

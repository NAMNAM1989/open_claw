from bot.access import is_allowed


class _Chat:
    def __init__(self, chat_id: int):
        self.id = chat_id


class _Update:
    def __init__(self, chat_id: int):
        self.effective_chat = _Chat(chat_id)


def test_is_allowed_when_in_list():
    assert is_allowed(_Update(-1001), {-1001, -1002}) is True


def test_is_allowed_when_not_in_list():
    assert is_allowed(_Update(99), {-1001}) is False


def test_is_allowed_empty_list_denies_all():
    assert is_allowed(_Update(-1001), set()) is False

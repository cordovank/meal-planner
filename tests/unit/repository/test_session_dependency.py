import pytest

from meal_planner.repository.sqlalchemy import session as session_module


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeSessionContext:
    def __init__(self, session: FakeSession) -> None:
        self.session = session

    async def __aenter__(self) -> FakeSession:
        return self.session

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class FakeSessionMaker:
    def __init__(self, session: FakeSession) -> None:
        self.session = session

    def __call__(self) -> FakeSessionContext:
        return FakeSessionContext(self.session)


@pytest.mark.asyncio
async def test_get_session_commits_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_session = FakeSession()
    monkeypatch.setattr(session_module, "get_sessionmaker", lambda: FakeSessionMaker(fake_session))

    generator = session_module.get_session()
    yielded_session = await generator.__anext__()

    assert yielded_session is fake_session

    with pytest.raises(StopAsyncIteration):
        await generator.__anext__()

    assert fake_session.committed is True
    assert fake_session.rolled_back is False


@pytest.mark.asyncio
async def test_get_session_rolls_back_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_session = FakeSession()
    monkeypatch.setattr(session_module, "get_sessionmaker", lambda: FakeSessionMaker(fake_session))

    generator = session_module.get_session()
    yielded_session = await generator.__anext__()

    assert yielded_session is fake_session

    with pytest.raises(RuntimeError, match="boom"):
        await generator.athrow(RuntimeError("boom"))

    assert fake_session.committed is False
    assert fake_session.rolled_back is True

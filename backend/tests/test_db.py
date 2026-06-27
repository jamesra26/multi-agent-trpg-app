from __future__ import annotations

from time import sleep
from types import SimpleNamespace

import app.db as public_db
import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import GameState, init_db
from app.db import session as db_session
from app.db.models import DeepMutableDict, DeepMutableList


# DB initialization layer: these tests should not know how game state is stored.


def test_init_db_creates_game_state_table(tmp_path) -> None:
    db_path = tmp_path / "data" / "trpg.db"

    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        table_names = inspect(engine).get_table_names()
        assert db_path.exists()
        assert "game_states" in table_names
    finally:
        engine.dispose()


def test_create_db_engine_uses_configured_database_url(monkeypatch) -> None:
    monkeypatch.setattr(
        db_session,
        "get_settings",
        lambda: SimpleNamespace(database_url="sqlite:///:memory:"),
    )

    engine = db_session.create_db_engine()

    try:
        assert engine.url.database == ":memory:"
    finally:
        engine.dispose()


def test_create_db_engine_prefers_explicit_database_url(monkeypatch, tmp_path) -> None:
    configured_db = tmp_path / "configured.db"
    explicit_db = tmp_path / "explicit.db"
    monkeypatch.setattr(
        db_session,
        "get_settings",
        lambda: SimpleNamespace(database_url=f"sqlite:///{configured_db.as_posix()}"),
    )

    engine = db_session.create_db_engine(f"sqlite:///{explicit_db.as_posix()}")

    try:
        assert engine.url.database == explicit_db.as_posix()
    finally:
        engine.dispose()


def test_database_url_helpers_handle_sqlite_and_other_urls(tmp_path) -> None:
    db_path = tmp_path / "nested" / "trpg.db"

    db_session._ensure_sqlite_parent_dir(f"sqlite:///{db_path.as_posix()}")
    db_session._ensure_sqlite_parent_dir("postgresql://user:pass@localhost/db")

    assert db_path.parent.exists()
    assert db_session._is_sqlite_url("sqlite:///:memory:")
    assert db_session._is_sqlite_url("sqlite+pysqlite:///:memory:")
    assert not db_session._is_sqlite_url("postgresql://user:pass@localhost/db")


def test_sqlite_relative_database_url_creates_parent_dir(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    db_session._ensure_sqlite_parent_dir("sqlite:///./data/trpg.db")

    assert (tmp_path / "data").exists()


def test_init_db_is_idempotent(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    first_engine = init_db(database_url)
    second_engine = init_db(database_url)

    try:
        with Session(second_engine) as session:
            session.add(GameState(save_slot="slot-1", state_json={}))
            session.commit()

            saved_state = session.scalar(select(GameState))

        assert saved_state is not None
        assert saved_state.save_slot == "slot-1"
    finally:
        first_engine.dispose()
        second_engine.dispose()


# GameState table contract layer: state_json is only a minimal valid placeholder here.


def test_game_state_table_columns_match_contract(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        columns = {column["name"] for column in inspect(engine).get_columns("game_states")}
        assert columns == {
            "id",
            "save_slot",
            "title",
            "scenario_id",
            "turn",
            "state_version",
            "state_json",
            "created_at",
            "updated_at",
        }
    finally:
        engine.dispose()


def test_game_state_persists_table_defaults(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            game_state = GameState(
                save_slot="slot-1",
                scenario_id="intro",
                state_json={},
            )
            session.add(game_state)
            session.commit()
            session.refresh(game_state)

            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )

        assert saved_state is not None
        assert saved_state.title == "未命名存档"
        assert saved_state.scenario_id == "intro"
        assert saved_state.turn == 0
        assert saved_state.state_version == 1
        assert saved_state.state_json == {}
        assert saved_state.created_at is not None
        assert saved_state.updated_at is not None
    finally:
        engine.dispose()


def test_game_state_updates_updated_at_when_record_changes(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            game_state = GameState(save_slot="slot-1", state_json={})
            session.add(game_state)
            session.commit()
            session.refresh(game_state)
            original_updated_at = game_state.updated_at

            sleep(0.01)
            game_state.turn = 1
            session.commit()
            session.refresh(game_state)

        assert game_state.updated_at > original_updated_at
    finally:
        engine.dispose()


def test_game_state_save_slot_is_unique(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add_all(
                [
                    GameState(save_slot="slot-1", state_json={}),
                    GameState(save_slot="slot-1", state_json={}),
                ]
            )

            with pytest.raises(IntegrityError):
                session.commit()
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("save_slot", "state_json"),
    [
        (None, {}),
        ("slot-1", None),
    ],
)
def test_game_state_requires_core_fields(tmp_path, save_slot, state_json) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add(GameState(save_slot=save_slot, state_json=state_json))

            with pytest.raises(IntegrityError):
                session.commit()
    finally:
        engine.dispose()


def test_game_state_string_length_contract_is_schema_metadata() -> None:
    columns = GameState.__table__.c

    assert columns.save_slot.type.length == 64
    assert columns.title.type.length == 120
    assert columns.scenario_id.type.length == 120


def test_sqlite_does_not_enforce_string_lengths(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")
    long_save_slot = "s" * 65
    long_title = "t" * 121
    long_scenario_id = "c" * 121

    try:
        with Session(engine) as session:
            session.add(
                GameState(
                    save_slot=long_save_slot,
                    title=long_title,
                    scenario_id=long_scenario_id,
                    state_json={},
                )
            )
            session.commit()

            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == long_save_slot)
            )

        assert saved_state is not None
        assert saved_state.title == long_title
        assert saved_state.scenario_id == long_scenario_id
    finally:
        engine.dispose()


def test_sqlite_datetime_round_trip_is_naive_utc(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add(GameState(save_slot="slot-1", state_json={}))
            session.commit()

            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )

        assert saved_state is not None
        assert saved_state.created_at.tzinfo is None
        assert saved_state.updated_at.tzinfo is None
    finally:
        engine.dispose()


# Temporary JSON adapter layer: replace or remove this block when state_json is split.


def test_game_state_json_adapter_persists_nested_state(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add(
                GameState(
                    save_slot="slot-1",
                    state_json={
                        "inventory": ["火把"],
                        "quests": {"main": "进入遗迹"},
                        "npc_affinity": {"守门人": 2},
                    },
                )
            )
            session.commit()

            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )

        assert saved_state is not None
        assert saved_state.state_json["inventory"] == ["火把"]
        assert saved_state.state_json["quests"]["main"] == "进入遗迹"
        assert saved_state.state_json["npc_affinity"]["守门人"] == 2
    finally:
        engine.dispose()


def test_game_state_json_adapter_nested_updates_are_persisted(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add(
                GameState(
                    save_slot="slot-1",
                    state_json={
                        "inventory": ["火把"],
                        "quests": {"main": "进入遗迹"},
                    },
                )
            )
            session.commit()

        with Session(engine) as session:
            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )
            assert saved_state is not None
            original_updated_at = saved_state.updated_at

            sleep(0.01)
            saved_state.state_json["inventory"].append("绳索")
            saved_state.state_json["quests"]["side"] = "寻找失踪商队"
            session.commit()

        with Session(engine) as session:
            updated_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )

        assert updated_state is not None
        assert updated_state.state_json["inventory"] == ["火把", "绳索"]
        assert updated_state.state_json["quests"]["side"] == "寻找失踪商队"
        assert updated_state.updated_at > original_updated_at
    finally:
        engine.dispose()


def test_game_state_json_adapter_setdefault_nested_update_is_persisted(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add(GameState(save_slot="slot-1", state_json={}))
            session.commit()

        with Session(engine) as session:
            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )
            assert saved_state is not None

            quests = saved_state.state_json.setdefault("quests", {"main": "进入遗迹"})
            quests["side"] = "寻找失踪商队"
            session.commit()

        with Session(engine) as session:
            updated_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )

        assert updated_state is not None
        assert updated_state.state_json["quests"] == {
            "main": "进入遗迹",
            "side": "寻找失踪商队",
        }
    finally:
        engine.dispose()


def test_game_state_json_adapter_insert_nested_update_is_persisted(tmp_path) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add(GameState(save_slot="slot-1", state_json={"inventory": []}))
            session.commit()

        with Session(engine) as session:
            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )
            assert saved_state is not None

            saved_state.state_json["inventory"].insert(0, {"name": "火把"})
            saved_state.state_json["inventory"][0]["count"] = 1
            session.commit()

        with Session(engine) as session:
            updated_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )

        assert updated_state is not None
        assert updated_state.state_json["inventory"] == [{"name": "火把", "count": 1}]
    finally:
        engine.dispose()


def test_game_state_json_adapter_slice_assignment_nested_update_is_persisted(
    tmp_path,
) -> None:
    db_path = tmp_path / "trpg.db"
    engine = init_db(f"sqlite:///{db_path.as_posix()}")

    try:
        with Session(engine) as session:
            session.add(
                GameState(
                    save_slot="slot-1",
                    state_json={"inventory": [{"name": "火把"}]},
                )
            )
            session.commit()

        with Session(engine) as session:
            saved_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )
            assert saved_state is not None

            saved_state.state_json["inventory"][0:1] = [{"name": "绳索"}]
            saved_state.state_json["inventory"][0]["count"] = 1
            session.commit()

        with Session(engine) as session:
            updated_state = session.scalar(
                select(GameState).where(GameState.save_slot == "slot-1")
            )

        assert updated_state is not None
        assert updated_state.state_json["inventory"] == [{"name": "绳索", "count": 1}]
    finally:
        engine.dispose()


def test_game_state_json_adapter_deep_mutable_container_edges() -> None:
    mutable_dict = DeepMutableDict({"items": []})
    mutable_list = DeepMutableList([{"name": "火把"}])

    assert DeepMutableDict.coerce("state_json", mutable_dict) is mutable_dict
    assert DeepMutableList.coerce("inventory", mutable_list) is mutable_list
    assert isinstance(DeepMutableList.coerce("inventory", []), DeepMutableList)

    mutable_list[0] = {"name": "绳索"}

    assert isinstance(mutable_list[0], DeepMutableDict)
    with pytest.raises(ValueError):
        DeepMutableList.coerce("inventory", "not-a-list")


# Public module contract layer.


def test_public_db_exports() -> None:
    assert sorted(public_db.__all__) == [
        "Base",
        "GameState",
        "create_db_engine",
        "init_db",
    ]
    assert public_db.GameState is GameState
    assert public_db.init_db is init_db

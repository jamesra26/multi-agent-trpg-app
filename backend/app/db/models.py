from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.ext.mutable import Mutable, MutableDict, MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class DeepMutableDict(MutableDict):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        dict.__init__(self)
        self.update(dict(*args, **kwargs))

    @classmethod
    def coerce(cls, key: str, value: Any) -> DeepMutableDict:
        if isinstance(value, DeepMutableDict):
            return value
        if isinstance(value, dict):
            return cls(value)
        return Mutable.coerce(key, value)

    def __setitem__(self, key: str, value: Any) -> None:
        dict.__setitem__(self, key, _coerce_nested(value, self))
        self.changed()

    def update(self, other: dict[str, Any], **kwargs: Any) -> None:
        for key, value in {**other, **kwargs}.items():
            self[key] = value

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key not in self:
            self[key] = default
        return self[key]

    def changed(self) -> None:
        super().changed()
        _notify_parent(self)


class DeepMutableList(MutableList):
    def __init__(self, iterable: list[Any] | None = None) -> None:
        list.__init__(self)
        self.extend(iterable or [])

    @classmethod
    def coerce(cls, key: str, value: Any) -> DeepMutableList:
        if isinstance(value, DeepMutableList):
            return value
        if isinstance(value, list):
            return cls(value)
        return Mutable.coerce(key, value)

    def __setitem__(self, index: int | slice, value: Any) -> None:
        if isinstance(index, slice):
            coerced_value = [_coerce_nested(item, self) for item in value]
        else:
            coerced_value = _coerce_nested(value, self)
        list.__setitem__(self, index, coerced_value)
        self.changed()

    def append(self, value: Any) -> None:
        list.append(self, _coerce_nested(value, self))
        self.changed()

    def insert(self, index: int, value: Any) -> None:
        list.insert(self, index, _coerce_nested(value, self))
        self.changed()

    def extend(self, iterable: list[Any]) -> None:
        for value in iterable:
            self.append(value)

    def changed(self) -> None:
        super().changed()
        _notify_parent(self)


def _coerce_nested(value: Any, parent: DeepMutableDict | DeepMutableList) -> Any:
    if isinstance(value, dict) and not isinstance(value, DeepMutableDict):
        value = DeepMutableDict(value)
    elif isinstance(value, list) and not isinstance(value, DeepMutableList):
        value = DeepMutableList(value)
    if isinstance(value, DeepMutableDict | DeepMutableList):
        value._parent_mutable = parent
    return value


def _notify_parent(value: DeepMutableDict | DeepMutableList) -> None:
    parent = getattr(value, "_parent_mutable", None)
    if parent is not None:
        parent.changed()


class GameState(Base):
    __tablename__ = "game_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    save_slot: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    title: Mapped[str] = mapped_column(String(120), nullable=False, default="未命名存档")
    scenario_id: Mapped[str | None] = mapped_column(String(120), nullable=True)

    turn: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    state_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # MVP 阶段将快速膨胀的 TRPG 状态集中保存为 JSON。
    # 后续稳定后应拆出背包、任务、NPC 关系、阵营、世界事件、战斗状态和短期记忆等列/表。
    state_json: Mapped[dict[str, Any]] = mapped_column(
        DeepMutableDict.as_mutable(JSON(none_as_null=True)),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from secret_santa.config import engine


class Santalist(SQLModel, table=True):
    """Table to store secret santa lists."""

    id: int | None = Field(default=None, primary_key=True)
    created: datetime
    name: str

    draws: list["Draw"] = Relationship(back_populates="santalist")
    participants: list["Participant"] = Relationship(back_populates="santalist")


class BlacklistLink(SQLModel, table=True):
    """Table to store participant blacklists (association)."""

    owner_id: int | None = Field(default=None, foreign_key="participant.id", primary_key=True)
    target_id: int | None = Field(default=None, foreign_key="participant.id", primary_key=True)


class Participant(SQLModel, table=True):
    """Table to store santa list participants."""

    id: int | None = Field(default=None, primary_key=True)
    name: str

    santalist_id: int | None = Field(default=None, foreign_key="santalist.id")
    santalist: Santalist = Relationship(back_populates="participants")

    blacklist: list["Participant"] = Relationship(
        # back_populates="blacklisted_by",
        link_model=BlacklistLink,
        sa_relationship_kwargs={
            "primaryjoin": "Participant.id==BlacklistLink.owner_id",
            "secondaryjoin": "Participant.id==BlacklistLink.target_id"
        }
    )


class DrawBase(SQLModel):
    """Table to store list draws."""

    id: int | None = Field(default=None, primary_key=True)
    created: datetime = Field(index=True)
    santalist_id: int | None = Field(default=None, foreign_key="santalist.id")


class Draw(DrawBase, table=True):
    """Actual table for Draw model."""

    items: list["DrawItem"] = Relationship(back_populates="draw")
    santalist: Santalist = Relationship(back_populates="draws")


class DrawItem(SQLModel, table=True):
    """Table to store draw items (association between participants)."""

    draw_id: int | None = Field(default=None, foreign_key="draw.id", primary_key=True)
    draw: Draw = Relationship(back_populates="items")
    giver_id: int | None = Field(default=None, foreign_key="participant.id", primary_key=True)
    giver: Draw = Relationship()
    receiver_id: int | None = Field(default=None, foreign_key="participant.id", primary_key=True)
    receiver: Draw = Relationship()


class DrawPublic(DrawBase):
    """Public version for API."""

    santalist: Santalist
    items: list[DrawItem] = []


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

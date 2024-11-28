"""API routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from secret_santa import models
from secret_santa.config import engine
from secret_santa.generator import generate_draw


router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


@router.get(
    "/lists",
    summary="Return all lists",
    response_model=list[models.Santalist],
    status_code=200,
    tags=["Lists"]
)
def get_lists(session: Session = Depends(get_session)):
    lists = session.exec(select(models.Santalist)).all()
    return lists


@router.post(
    "/lists",
    summary="Create a new list",
    response_model=models.Santalist,
    status_code=201,
    tags=["Lists"]
)
def create_list(*, session: Session = Depends(get_session), item: models.Santalist):
    item.created = datetime.now(timezone.utc)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get(
    "/lists/{list_id}/participants",
    summary="Return all participants in given list",
    response_model=list[models.Participant],
    status_code=200,
    tags=["Lists"]
)
def get_list_participants(*, session: Session = Depends(get_session), list_id: int):
    santalist = session.exec(
        select(models.Santalist).where(models.Santalist.id == list_id)
    ).first()
    if santalist is None:
        raise HTTPException(status_code=404, detail="List not found")
    return santalist.participants


@router.post(
    "/lists/{list_id}/participants",
    summary="Add a new participant to the given list",
    response_model=models.Participant,
    status_code=201,
    tags=["Lists"]
)
def add_participant(*, session: Session = Depends(get_session), list_id: int, participant: models.Participant):
    santalist = session.exec(
        select(models.Santalist).where(models.Santalist.id == list_id)
    ).first()
    if santalist is None:
        raise HTTPException(status_code=404, detail="List not found")
    participant.santalist = santalist
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


@router.post(
    "/lists/{list_id}/draws",
    summary="Create a new drap for the given list",
    response_model=models.DrawPublic,
    status_code=201,
    tags=["Lists"]
)
def create_list_draw(*, session: Session = Depends(get_session), list_id: int):
    santalist = session.exec(
        select(models.Santalist).where(models.Santalist.id == list_id)
    ).first()
    if santalist is None:
        raise HTTPException(status_code=404, detail="List not found")
    participant_ids: list[int] = []
    blacklists: dict = {}
    for participant in santalist.participants:
        participant_ids.append(participant.id)
        blacklists[participant.id] = [blacklisted_p.id for blacklisted_p in participant.blacklist]
    solution = generate_draw(participant_ids, blacklists)
    if not solution:
        raise HTTPException(
            status_code=400, detail="No draw can be generated for this list")
    draw = models.Draw(
        santalist=santalist,
        created=datetime.now(timezone.utc),
    )
    session.add(draw)
    session.commit()
    session.refresh(draw)
    for giver_id, receiver_id in solution.items():
        session.add(models.DrawItem(draw=draw, giver_id=giver_id, receiver_id=receiver_id))
    session.commit()
    session.refresh(draw)
    return draw


@router.get(
    "/lists/{list_id}/latest_draws",
    summary="Return the 5 latest draws of the given list",
    response_model=list[models.DrawPublic],
    status_code=200,
    tags=["Lists"]
)
def get_list_latest_draws(*, session: Session = Depends(get_session), list_id: int):
    draws = session.exec(
        select(models.Draw).where(models.Draw.santalist_id == list_id)
        .order_by(models.Draw.created.desc())
        .limit(5)
    ).all()
    return draws


@router.get(
    "/participants/{participant_id}/blacklist",
    summary="Return blacklist of the given participant",
    response_model=list[models.Participant],
    status_code=200,
    tags=["Participants"]
)
def get_list_participant_blacklist(*, session: Session = Depends(get_session), participant_id: int):
    participant = session.exec(
        select(models.Participant).where(models.Participant.id == participant_id)
    ).first()
    if participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant.blacklist


class BlacklistedParticipant(BaseModel):
    """Simple input model to avoid using Participant directly."""

    id: int


@router.post(
    "/participants/{participant_id}/blacklist",
    summary="Add new person into the blacklist of the given participant.",
    response_model=list[models.Participant],
    status_code=201,
    tags=["Participants"]
)
def add_list_participant_blacklist(*,
                                   session: Session = Depends(get_session),
                                   participant_id: int,
                                   payload: BlacklistedParticipant):
    participant = session.exec(
        select(models.Participant).where(models.Participant.id == participant_id)
    ).first()
    if participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")
    blacklisted_p = session.exec(
        select(models.Participant).where(models.Participant.id == payload.id)
    ).first()
    if blacklisted_p is None:
        raise HTTPException(status_code=404, detail="Blacklisted participant not found")
    if participant.id == blacklisted_p.id:
        raise HTTPException(status_code=400, detail="A participant can't be in his own blacklist")
    if participant.santalist_id != blacklisted_p.santalist_id:
        raise HTTPException(status_code=400, detail="Participants are not in the same list")
    link = session.exec(
        select(models.BlacklistLink).where(
            models.BlacklistLink.owner_id == participant.id,
            models.BlacklistLink.target_id == blacklisted_p.id
        )
    ).first()
    if link:
        raise HTTPException(status_code=400, detail="Participant already in blacklist")
    link = models.BlacklistLink(
        owner_id=participant.id,
        target_id=blacklisted_p.id
    )
    session.add(link)
    session.commit()
    session.refresh(participant)
    return participant.blacklist

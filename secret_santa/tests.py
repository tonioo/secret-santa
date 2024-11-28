import os

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app
from secret_santa.routes import get_session


def test_complete_scenario():
    engine = create_engine(
        os.environ["DB_URL"], connect_args={"check_same_thread": False}
    )

    with Session(engine) as session:
        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        SQLModel.metadata.create_all(engine)
        client = TestClient(app)

        response = client.post("/lists", json={"name": "Test list"})
        data = response.json()

        assert response.status_code == 201
        assert "id" in data
        list_id = data["id"]

        participant_names = ["Pierre", "Paul", "Jacques", "Michel"]
        for name in participant_names:
            response = client.post(f"/lists/{list_id}/participants", json={"name": name})
            assert response.status_code == 201

        response = client.get(f"/lists/{list_id}/participants")
        assert response.status_code == 200
        participants = response.json()
        assert len(participants) == 4

        # Fill some blacklists
        left_id = participants[0]["id"]
        right_id = participants[1]["id"]
        response = client.post(f"/participants/{left_id}/blacklist", json={"id": right_id})
        assert response.status_code == 201

        left_id = participants[2]["id"]
        right_id = participants[3]["id"]
        response = client.post(f"/participants/{left_id}/blacklist", json={"id": right_id})
        assert response.status_code == 201

        # Generate draw
        response = client.post(f"/lists/{list_id}/draws")
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == len(participants)

        # Get latest draws
        response = client.get(f"/lists/{list_id}/latest_draws")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

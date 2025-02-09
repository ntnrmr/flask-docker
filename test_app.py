from unittest.mock import MagicMock, patch

import pytest

from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@patch("app.db.session")
@patch("app.MarketingTouchpointData")
def test_create_touchpoint(mock_marketingtouchpointdata, mock_session, client):
    mock_instance = MagicMock()

    mock_instance.id = 1
    mock_instance.event_name = "click"
    mock_instance.user_id = "user123"
    mock_instance.channel_name = "Facebook"
    mock_marketingtouchpointdata.return_value = mock_instance

    payload = {"event_name": "click", "user_id": "user123", "channel_name": "Facebook"}

    response = client.post(
        "/touchpoints",
        json=payload,
        content_type="application/json",
    )

    assert response.status_code == 201

    mock_marketingtouchpointdata.assert_called_once_with(
        event_name="click", user_id="user123", channel_name="Facebook"
    )
    mock_session.add.assert_called_once_with(mock_instance)
    mock_session.commit.assert_called_once()

    data = response.get_json()
    assert data["id"] == 1
    assert data["event_name"] == "click"
    assert data["user_id"] == "user123"
    assert data["channel_name"] == "Facebook"

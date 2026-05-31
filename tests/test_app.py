from fastapi.testclient import TestClient
import copy

from src.app import app, activities


def client_with_reset():
    """Arrange: create TestClient and snapshot activities"""
    original = copy.deepcopy(activities)
    client = TestClient(app)

    class C:
        pass

    C.client = client
    C.original = original
    return C


def teardown_restore(original):
    activities.clear()
    activities.update(original)


def test_get_activities():
    # Arrange
    ctx = client_with_reset()

    # Act
    resp = ctx.client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_new_participant():
    # Arrange
    ctx = client_with_reset()
    activity = "Chess Club"
    email = "new_student@example.com"

    # Act
    resp = ctx.client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")
    assert email in ctx.client.get("/activities").json()[activity]["participants"]

    # Cleanup
    teardown_restore(ctx.original)


def test_signup_existing_participant():
    # Arrange
    ctx = client_with_reset()
    activity = "Chess Club"
    existing = "michael@mergington.edu"

    # Act
    resp = ctx.client.post(f"/activities/{activity}/signup", params={"email": existing})

    # Assert
    assert resp.status_code == 400

    # Cleanup
    teardown_restore(ctx.original)


def test_unregister_existing_participant():
    # Arrange
    ctx = client_with_reset()
    activity = "Chess Club"
    existing = "michael@mergington.edu"

    # Act
    resp = ctx.client.delete(f"/activities/{activity}/unregister", params={"email": existing})

    # Assert
    assert resp.status_code == 200
    assert f"Unregistered {existing}" in resp.json().get("message", "")
    assert existing not in ctx.client.get("/activities").json()[activity]["participants"]

    # Cleanup
    teardown_restore(ctx.original)


def test_unregister_nonexistent_participant():
    # Arrange
    ctx = client_with_reset()
    activity = "Chess Club"
    not_present = "noone@example.com"

    # Act
    resp = ctx.client.delete(f"/activities/{activity}/unregister", params={"email": not_present})

    # Assert
    assert resp.status_code == 404

    # Cleanup
    teardown_restore(ctx.original)

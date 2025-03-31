from fastapi.testclient import TestClient

def test_create_link_anonymous(client: TestClient):
    resp = client.post("/links/shorten", json={
        "original_url": "https://example.com/test"
    })
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["original_url"] == "https://example.com/test"
    assert data["owner_id"] is None
    assert "short_code" in data
    short_code = data["short_code"]

    resp_redirect = client.get(f"/{short_code}", allow_redirects=False)
    assert resp_redirect.status_code == 307
    assert resp_redirect.headers["Location"] == "https://example.com/test"

def test_create_link_authorized(client: TestClient):
    client.post("/auth/register", json={"username": "authuser", "password": "pass"})
    token_resp = client.post("/auth/login", json={"username": "authuser", "password": "pass"})
    token_data = token_resp.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.post("/links/shorten", json={
        "original_url": "https://example.com/secure",
        "alias": "myAlias"
    }, headers=headers)

    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["short_code"] == "myAlias"
    assert data["owner_id"] is not None
    assert data["original_url"] == "https://example.com/secure"

def test_link_stats(client: TestClient):
    client.post("/auth/register", json={"username": "statuser", "password": "spass"})
    token = client.post("/auth/login", json={"username": "statuser", "password": "spass"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/links/shorten", json={"original_url": "https://fastapi.tiangolo.com"}, headers=headers)
    data = resp.json()
    short_code = data["short_code"]

    client.get(f"/{short_code}", allow_redirects=False)

    stats = client.get(f"/links/{short_code}/stats", headers=headers)
    assert stats.status_code == 200
    stats_data = stats.json()
    assert stats_data["click_count"] == 1
    assert stats_data["original_url"] == "https://fastapi.tiangolo.com"
    assert stats_data["short_code"] == short_code

def test_update_and_delete_link(client: TestClient):
    client.post("/auth/register", json={"username": "upduser", "password": "updpass"})
    token = client.post("/auth/login", json={"username": "upduser", "password": "updpass"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp_create = client.post("/links/shorten", json={"original_url": "https://test.com/old"}, headers=headers)
    link_data = resp_create.json()
    code = link_data["short_code"]
    resp_upd = client.put(f"/links/{code}", json={"alias": "newAlias"}, headers=headers)
    assert resp_upd.status_code == 200
    updated = resp_upd.json()
    assert updated["short_code"] == "newAlias"
    assert updated["original_url"] == "https://test.com/old"

    resp_del = client.delete(f"/links/newAlias", headers=headers)
    assert resp_del.status_code == 204

    resp_redirect = client.get("/newAlias", allow_redirects=False)
    assert resp_redirect.status_code == 404

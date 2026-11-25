import pytest

TAG = {"name": "bug", "color": "#00ff00"}


@pytest.mark.parametrize("method,path", [
    ("get", "/api/tags/tags"),
    ("post", "/api/tags/tags"),
    ("get", "/api/boards/"),
    ("get", "/api/boards/1/lists/1/cards/search"),
    ("put", "/api/boards/1/lists/1/cards"),
])
def test_middleware_rejects_missing_or_invalid_token(client, method, path):
    assert getattr(client, method)(path).status_code == 401
    bad = {"Authorization": "Bearer token.invalido.xxx"}
    assert getattr(client, method)(path, headers=bad).status_code == 401


def test_public_auth_routes_do_not_need_token(client, fake):
    payload = {"email": fake.email(), "username": fake.user_name(), "password": fake.password(length=12)}
    assert client.post("/api/auth/register", json=payload).status_code == 201


def test_tags_crud_with_auth(client, auth_headers):
    created = client.post("/api/tags/tags", json=TAG, headers=auth_headers)
    assert created.status_code == 200
    tag_id = created.json()["id"]
    assert client.get("/api/tags/tags", headers=auth_headers).status_code == 200
    assert client.get(f"/api/tags/tags/{tag_id}", headers=auth_headers).json()["name"] == "bug"


def test_cannot_tag_other_users_card(client, auth_headers, other_auth_headers):
    board = client.post("/api/boards/", json={"title": "b", "color": "#fff000"}, headers=auth_headers).json()["id"]
    lst = client.post(f"/api/boards/{board}/lists/", json={"title": "l", "board_id": board}, headers=auth_headers).json()["id"]
    card = client.post(f"/api/boards/{board}/lists/{lst}/cards/create", json={"title": "c", "list_id": lst}, headers=auth_headers).json()
    tag = client.post("/api/tags/tags", json=TAG, headers=other_auth_headers).json()

    res = client.post(f"/api/tags/tags/{tag['id']}/cards/{card['id']}", headers=other_auth_headers)
    assert res.status_code == 403


def test_tags_are_isolated_per_user(client, auth_headers, other_auth_headers):
    mine = client.post("/api/tags/tags", json=TAG, headers=auth_headers)
    assert mine.status_code == 200
    tag_id = mine.json()["id"]

    # El otro usuario no los ve ni los puede tocar
    assert client.get("/api/tags/tags", headers=other_auth_headers).json() == []
    url = f"/api/tags/tags/{tag_id}"
    assert client.get(url, headers=other_auth_headers).status_code == 404
    assert client.put(url, json={"name": "x"}, headers=other_auth_headers).status_code == 404
    assert client.delete(url, headers=other_auth_headers).status_code == 404
    assert client.get(url, headers=auth_headers).status_code == 200


def test_same_tag_name_allowed_for_different_users_but_not_twice(client, auth_headers, other_auth_headers):
    assert client.post("/api/tags/tags", json=TAG, headers=auth_headers).status_code == 200
    assert client.post("/api/tags/tags", json=TAG, headers=other_auth_headers).status_code == 200
    assert client.post("/api/tags/tags", json=TAG, headers=auth_headers).status_code == 409


def test_cannot_use_other_users_tag_on_own_card(client, auth_headers, other_auth_headers):
    board = client.post("/api/boards/", json={"title": "b", "color": "#fff000"}, headers=auth_headers).json()["id"]
    lst = client.post(f"/api/boards/{board}/lists/", json={"title": "l", "board_id": board}, headers=auth_headers).json()["id"]
    card = client.post(f"/api/boards/{board}/lists/{lst}/cards/create", json={"title": "c", "list_id": lst}, headers=auth_headers).json()
    foreign_tag = client.post("/api/tags/tags", json=TAG, headers=other_auth_headers).json()

    res = client.post(f"/api/tags/tags/{foreign_tag['id']}/cards/{card['id']}", headers=auth_headers)
    assert res.status_code == 404


def test_create_card_with_tags_creates_per_user_tags(client, auth_headers, other_auth_headers):
    board = client.post("/api/boards/", json={"title": "b", "color": "#fff000"}, headers=auth_headers).json()["id"]
    lst = client.post(f"/api/boards/{board}/lists/", json={"title": "l", "board_id": board}, headers=auth_headers).json()["id"]
    res = client.post(
        f"/api/boards/{board}/lists/{lst}/cards/create",
        json={"title": "c", "list_id": lst, "tags": ["nuevo"]},
        headers=auth_headers,
    )
    assert res.status_code == 201
    assert res.json()["tags"] == ["nuevo"]
    assert [t["name"] for t in client.get("/api/tags/tags", headers=auth_headers).json()] == ["nuevo"]
    assert client.get("/api/tags/tags", headers=other_auth_headers).json() == []


def test_create_card_rejects_list_id_not_matching_route(client, auth_headers, other_auth_headers):
    my_board = client.post("/api/boards/", json={"title": "b", "color": "#fff000"}, headers=auth_headers).json()["id"]
    my_list = client.post(f"/api/boards/{my_board}/lists/", json={"title": "l", "board_id": my_board}, headers=auth_headers).json()["id"]
    v_board = client.post("/api/boards/", json={"title": "v", "color": "#fff000"}, headers=other_auth_headers).json()["id"]
    v_list = client.post(f"/api/boards/{v_board}/lists/", json={"title": "v", "board_id": v_board}, headers=other_auth_headers).json()["id"]

    res = client.post(
        f"/api/boards/{my_board}/lists/{my_list}/cards/create",
        json={"title": "inyectada", "list_id": v_list},
        headers=auth_headers,
    )
    assert res.status_code == 400

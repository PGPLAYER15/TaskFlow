BOARD = {"title": "Mi tablero", "color": "#ff0000"}


def _board(client, headers):
    r = client.post("/api/boards/", json=BOARD, headers=headers)
    assert r.status_code == 200
    return r.json()["id"]


def _list(client, headers, board_id, title="Lista"):
    r = client.post(
        f"/api/boards/{board_id}/lists/",
        json={"title": title, "board_id": board_id},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def _card(client, headers, board_id, list_id, title="Tarjeta"):
    r = client.post(
        f"/api/boards/{board_id}/lists/{list_id}/cards/create",
        json={"title": title, "list_id": list_id},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


def _url(board_id, list_id, card_id=None, suffix=""):
    base = f"/api/boards/{board_id}/lists/{list_id}/cards"
    return f"{base}/{card_id}{suffix}" if card_id else f"{base}/"


def test_move_card_updates_list_id_and_position(client, auth_headers):
    board_id = _board(client, auth_headers)
    list_a = _list(client, auth_headers, board_id, "A")
    list_b = _list(client, auth_headers, board_id, "B")
    card = _card(client, auth_headers, board_id, list_a)
    _card(client, auth_headers, board_id, list_b, "Existente en B")

    response = client.put(
        _url(board_id, list_a, card["id"], "/move"),
        json={"list_id": list_b, "position": 1},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["list_id"] == list_b
    assert data["position"] == 1
    assert [c["id"] for c in client.get(_url(board_id, list_a), headers=auth_headers).json()] == []
    assert card["id"] in [c["id"] for c in client.get(_url(board_id, list_b), headers=auth_headers).json()]


def test_delete_card_does_not_break_list(client, auth_headers):
    board_id = _board(client, auth_headers)
    list_id = _list(client, auth_headers, board_id)
    card1 = _card(client, auth_headers, board_id, list_id, "Uno")
    card2 = _card(client, auth_headers, board_id, list_id, "Dos")

    response = client.delete(_url(board_id, list_id, card1["id"]), headers=auth_headers)
    assert response.status_code == 204

    assert client.get(_url(board_id, list_id, card1["id"]), headers=auth_headers).status_code == 404
    lst = client.get(f"/api/boards/{board_id}/lists/{list_id}", headers=auth_headers)
    assert lst.status_code == 200
    assert [c["id"] for c in lst.json()["cards"]] == [card2["id"]]


def test_move_other_users_card_returns_403(client, auth_headers, other_auth_headers):
    board_id = _board(client, auth_headers)
    list_a = _list(client, auth_headers, board_id, "A")
    list_b = _list(client, auth_headers, board_id, "B")
    card = _card(client, auth_headers, board_id, list_a)

    response = client.put(
        _url(board_id, list_a, card["id"], "/move"),
        json={"list_id": list_b, "position": 0},
        headers=other_auth_headers,
    )

    assert response.status_code == 403
    assert client.get(_url(board_id, list_a, card["id"]), headers=auth_headers).json()["list_id"] == list_a


def test_cards_endpoints_require_authentication(client, auth_headers):
    board_id = _board(client, auth_headers)
    list_id = _list(client, auth_headers, board_id)
    card = _card(client, auth_headers, board_id, list_id)

    assert client.get(_url(board_id, list_id, card["id"])).status_code == 401
    assert client.delete(_url(board_id, list_id, card["id"])).status_code == 401


def test_other_user_cannot_read_update_or_delete_card(client, auth_headers, other_auth_headers):
    board_id = _board(client, auth_headers)
    list_id = _list(client, auth_headers, board_id)
    card = _card(client, auth_headers, board_id, list_id)
    url = _url(board_id, list_id, card["id"])

    assert client.get(url, headers=other_auth_headers).status_code == 403
    assert client.put(url, json={"title": "x"}, headers=other_auth_headers).status_code == 403
    assert client.delete(url, headers=other_auth_headers).status_code == 403
    assert client.get(url, headers=auth_headers).status_code == 200


def test_search_and_filter_only_return_own_cards(client, auth_headers, other_auth_headers):
    board_id = _board(client, auth_headers)
    list_id = _list(client, auth_headers, board_id)
    _card(client, auth_headers, board_id, list_id, "Secreto")
    other_board = _board(client, other_auth_headers)
    other_list = _list(client, other_auth_headers, other_board)
    _card(client, other_auth_headers, other_board, other_list, "Secreto ajeno")

    mine = client.get(_url(board_id, list_id) + "search", params={"q": "Secreto"}, headers=auth_headers)
    assert mine.status_code == 200
    assert [c["title"] for c in mine.json()] == ["Secreto"]

    # Tarjetas por etiqueta: solo las propias
    tag = client.post("/api/tags/tags", json={"name": "urgente", "color": "#ff0000"}, headers=auth_headers).json()
    mine_card = _card(client, auth_headers, board_id, list_id, "Con tag")
    other_card = _card(client, other_auth_headers, other_board, other_list, "Con tag ajena")
    assert client.post(f"/api/tags/tags/{tag['id']}/cards/{mine_card['id']}", headers=auth_headers).status_code == 204
    other_tag = client.post("/api/tags/tags", json={"name": "urgente", "color": "#ff0000"}, headers=other_auth_headers).json()
    assert client.post(f"/api/tags/tags/{other_tag['id']}/cards/{other_card['id']}", headers=other_auth_headers).status_code == 204

    res = client.get(_url(board_id, list_id) + "filter_by_tag", params={"tag_name": "urgente"}, headers=auth_headers)
    assert res.status_code == 200
    assert [c["title"] for c in res.json()] == ["Con tag"]
    assert res.json()[0]["tags"] == ["urgente"]

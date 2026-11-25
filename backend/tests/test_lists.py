BOARD = {"title": "Mi tablero", "color": "#ff0000"}


def _create_board(client, headers):
    response = client.post("/api/boards/", json=BOARD, headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def test_create_list_in_board(client, auth_headers):
    board_id = _create_board(client, auth_headers)

    response = client.post(
        f"/api/boards/{board_id}/lists/",
        json={"title": "To Do", "board_id": board_id},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "To Do"
    assert data["board_id"] == board_id


def test_create_list_in_other_users_board_returns_403(
    client, auth_headers, other_auth_headers
):
    board_id = _create_board(client, auth_headers)

    response = client.post(
        f"/api/boards/{board_id}/lists/",
        json={"title": "Intruso", "board_id": board_id},
        headers=other_auth_headers,
    )

    assert response.status_code == 403


def test_other_user_cannot_read_update_or_delete_list(
    client, auth_headers, other_auth_headers
):
    board_id = _create_board(client, auth_headers)
    list_id = client.post(
        f"/api/boards/{board_id}/lists/",
        json={"title": "Privada", "board_id": board_id},
        headers=auth_headers,
    ).json()["id"]
    url = f"/api/boards/{board_id}/lists/{list_id}"

    assert client.get(url).status_code == 401
    assert client.get(url, headers=other_auth_headers).status_code == 403
    assert client.put(
        url, json={"title": "x", "board_id": board_id}, headers=other_auth_headers
    ).status_code == 403
    assert client.delete(url, headers=other_auth_headers).status_code == 403
    assert client.get(url, headers=auth_headers).status_code == 200


def _mk_list(client, headers, board_id, title):
    return client.post(
        f"/api/boards/{board_id}/lists/",
        json={"title": title, "board_id": board_id},
        headers=headers,
    ).json()["id"]


def _mk_card(client, headers, board_id, list_id):
    return client.post(
        f"/api/boards/{board_id}/lists/{list_id}/cards/create",
        json={"title": "c", "list_id": list_id},
        headers=headers,
    ).json()["id"]


def test_update_list_cards_moves_own_cards(client, auth_headers):
    board_id = _create_board(client, auth_headers)
    a = _mk_list(client, auth_headers, board_id, "A")
    b = _mk_list(client, auth_headers, board_id, "B")
    c1, c2 = _mk_card(client, auth_headers, board_id, a), _mk_card(client, auth_headers, board_id, a)

    res = client.put(f"/api/boards/{board_id}/lists/{b}/cards", json={"cards": [c2, c1]}, headers=auth_headers)

    assert res.status_code == 200
    assert [c["id"] for c in sorted(res.json()["cards"], key=lambda c: c["position"])] == [c2, c1]


def test_update_list_cards_rejects_other_users_card(client, auth_headers, other_auth_headers):
    victim_board = _create_board(client, other_auth_headers)
    victim_list = _mk_list(client, other_auth_headers, victim_board, "V")
    victim_card = _mk_card(client, other_auth_headers, victim_board, victim_list)
    my_board = _create_board(client, auth_headers)
    my_list = _mk_list(client, auth_headers, my_board, "M")

    res = client.put(f"/api/boards/{my_board}/lists/{my_list}/cards", json={"cards": [victim_card]}, headers=auth_headers)

    assert res.status_code == 403
    still = client.get(f"/api/boards/{victim_board}/lists/{victim_list}", headers=other_auth_headers).json()
    assert [c["id"] for c in still["cards"]] == [victim_card]

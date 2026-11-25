BOARD = {"title": "Mi tablero", "description": "desc", "color": "#ff0000"}


def test_authenticated_user_can_create_board(client, auth_headers):
    response = client.post("/api/boards/", json=BOARD, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == BOARD["title"]
    assert data["color"] == BOARD["color"]
    assert "id" in data


def test_unauthenticated_user_cannot_create_board(client):
    response = client.post("/api/boards/", json=BOARD)

    assert response.status_code == 401


def test_user_cannot_see_other_users_boards(client, auth_headers, other_auth_headers):
    board_id = client.post("/api/boards/", json=BOARD, headers=auth_headers).json()["id"]

    # El listado del otro usuario no incluye el tablero
    response = client.get("/api/boards/", headers=other_auth_headers)
    assert response.status_code == 200
    assert response.json() == []

    # Acceso directo al tablero ajeno prohibido
    response = client.get(f"/api/boards/{board_id}", headers=other_auth_headers)
    assert response.status_code == 403

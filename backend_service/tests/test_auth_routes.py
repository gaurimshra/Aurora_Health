def test_register_login_and_me_flow(client):
    register = client.post(
        "/auth/register",
        json={
            "name": "Gauri",
            "username": "gauri",
            "email": "gauri@example.com",
            "password": "Password123",
        },
    )
    assert register.status_code == 200
    token = register.json()["token"]
    assert register.json()["username"] == "gauri"

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "gauri@example.com"
    assert me.json()["username"] == "gauri"

    login = client.post(
        "/auth/login",
        json={
            "email": "gauri@example.com",
            "password": "Password123",
        },
    )
    assert login.status_code == 200
    assert login.json()["email"] == "gauri@example.com"
    assert login.json()["username"] == "gauri"

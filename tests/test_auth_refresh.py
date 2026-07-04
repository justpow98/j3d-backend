from authentication import TokenManager
from models import RefreshToken


def test_token_pair_issues_working_access_and_refresh_tokens(app, user):
    access, refresh = TokenManager.create_token_pair(user.id)
    assert access
    assert refresh
    assert RefreshToken.query.count() == 1


def test_refresh_rotates_and_revokes_prior_token(client, user):
    access, refresh = TokenManager.create_token_pair(user.id)

    resp = client.post('/api/auth/refresh', json={'refresh_token': refresh})
    assert resp.status_code == 200
    new_refresh = resp.get_json()['refresh_token']
    assert new_refresh != refresh

    # Reusing the rotated-out refresh token must fail
    replay = client.post('/api/auth/refresh', json={'refresh_token': refresh})
    assert replay.status_code == 401

    # The newly issued refresh token still works
    resp2 = client.post('/api/auth/refresh', json={'refresh_token': new_refresh})
    assert resp2.status_code == 200


def test_logout_revokes_refresh_token(client, user):
    access, refresh = TokenManager.create_token_pair(user.id)

    resp = client.post(
        '/api/auth/logout',
        json={'refresh_token': refresh},
        headers={'Authorization': f'Bearer {access}'}
    )
    assert resp.status_code == 200

    replay = client.post('/api/auth/refresh', json={'refresh_token': refresh})
    assert replay.status_code == 401


def test_refresh_rejects_unknown_token(client):
    resp = client.post('/api/auth/refresh', json={'refresh_token': 'not-a-real-token'})
    assert resp.status_code == 401

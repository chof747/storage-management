from app.domain.printing.print_strategy import get_all_printing_strategies


def test_get_printing_strategies(client):
    response = client.get("/api/printing_strategies/")
    assert response.status_code == 200

    data = response.json()
    assert data == get_all_printing_strategies()

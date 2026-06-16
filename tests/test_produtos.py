import pytest


def test_listar_produtos_banco_vazio(client):
    resp = client.get("/produtos")
    assert resp.status_code == 200
    assert resp.json() == []


def test_criar_produto_retorna_201(client):
    payload = {"nome": "Mouse Gamer", "preco": 189.90, "estoque": 10}
    resp = client.post("/produtos", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["nome"] == "Mouse Gamer"
    assert data["preco"] == 189.90
    assert "id" in data


def test_criar_produto_persiste_no_banco(client):
    payload = {"nome": "Monitor 24'", "preco": 1299.00, "estoque": 5}
    criado = client.post("/produtos", json=payload).json()

    resp = client.get(f"/produtos/{criado['id']}")
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Monitor 24'"


def test_produto_criado_aparece_na_listagem(client):
    client.post("/produtos", json={"nome": "Headset", "preco": 249.90, "estoque": 20})
    client.post("/produtos", json={"nome": "Webcam", "preco": 199.00, "estoque": 8})

    resp = client.get("/produtos")
    nomes = [p["nome"] for p in resp.json()]
    assert "Headset" in nomes
    assert "Webcam" in nomes


def test_buscar_produto_por_id(produto_existente, client):
    produto_id = produto_existente["id"]
    resp = client.get(f"/produtos/{produto_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == produto_id


def test_buscar_produto_inexistente_retorna_404(client):
    resp = client.get("/produtos/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Produto não encontrado"


def test_deletar_produto_retorna_204(produto_existente, client):
    produto_id = produto_existente["id"]
    resp = client.delete(f"/produtos/{produto_id}")
    assert resp.status_code == 204


def test_deletar_produto_remove_do_banco(produto_existente, client):
    produto_id = produto_existente["id"]
    client.delete(f"/produtos/{produto_id}")

    resp = client.get(f"/produtos/{produto_id}")
    assert resp.status_code == 404


def test_deletar_produto_inexistente_retorna_404(client):
    resp = client.delete("/produtos/99999")
    assert resp.status_code == 404


def test_banco_isolado_entre_testes(client):
    # garante que nenhum dado do teste anterior vazou
    resp = client.get("/produtos")
    assert resp.json() == []


@pytest.mark.parametrize(
    "payload",
    [
        {"nome": "", "preco": 50.0},           # nome vazio
        {"nome": "Produto X", "preco": 0},     # preco zero
        {"nome": "Produto X", "preco": -10},   # preco negativo
        {"preco": 99.90},                       # sem nome
        {"nome": "Produto X"},                  # sem preco
    ],
)
def test_criar_produto_payload_invalido_retorna_422(client, payload):
    resp = client.post("/produtos", json=payload)
    assert resp.status_code == 422

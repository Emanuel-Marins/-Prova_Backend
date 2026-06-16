import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import Base, ProdutoDB, app, get_db

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/ecommerce_test"


@pytest.fixture()
def client():
    engine_test = create_engine(TEST_DATABASE_URL)
    TestingSession = sessionmaker(bind=engine_test)

    Base.metadata.create_all(bind=engine_test)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)
    engine_test.dispose()


@pytest.fixture()
def produto_existente(client):
    payload = {"nome": "Teclado Mecânico", "preco": 349.90, "estoque": 15}
    resp = client.post("/produtos", json=payload)
    return resp.json()

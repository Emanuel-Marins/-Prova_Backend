import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import Boolean, Column, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ecommerce")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class ProdutoDB(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)


Base.metadata.create_all(bind=engine)


# schemas
class ProdutoIn(BaseModel):
    nome: str
    preco: float
    estoque: int = 0
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError("nome não pode ser vazio")
        return v

    @field_validator("preco")
    @classmethod
    def preco_deve_ser_positivo(cls, v):
        if v <= 0:
            raise ValueError("preco deve ser maior que zero")
        return v


class ProdutoOut(ProdutoIn):
    id: int

    model_config = {"from_attributes": True}


app = FastAPI(title="API de Produtos")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/produtos", response_model=list[ProdutoOut])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(ProdutoDB).all()


@app.post("/produtos", response_model=ProdutoOut, status_code=201)
def criar_produto(produto: ProdutoIn, db: Session = Depends(get_db)):
    novo = ProdutoDB(**produto.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.get("/produtos/{produto_id}", response_model=ProdutoOut)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.delete("/produtos/{produto_id}", status_code=204)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()

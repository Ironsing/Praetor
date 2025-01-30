from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import create_engine, ForeignKey

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"
    username:Mapped[str] = mapped_column(primary_key=True)
    password:Mapped[str] = mapped_column()

class Passwords(Base):
    __tablename__ = "passwords"
    website:Mapped[str] = mapped_column()
    pswrd:Mapped[str] = mapped_column()
    user:Mapped[str] = mapped_column(ForeignKey("users.username"))
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

engine = create_engine('sqlite:///database/vault.db')
Base.metadata.create_all(bind=engine)
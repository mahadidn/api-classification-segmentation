from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    username: str = Field(unique=True)
    password: str = Field()
    
class Data_customers(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    gender: str = Field()
    ever_married: str = Field()
    age: int = Field()
    graduated: str = Field()
    profession: str = Field()
    spending_score: str = Field()
    family_size: str = Field()
    segmentation: str = Field()
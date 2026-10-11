from pydantic import BaseModel, EmailStr


class AuthorCreate(BaseModel):
    name: str
    email: EmailStr


class AuthorUpdate(BaseModel):
    name: str
    email: EmailStr


class AuthorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    title: str
    price: float
    author_id: int


class BookUpdate(BaseModel):
    title: str
    price: float
    author_id: int


class BookResponse(BaseModel):
    id: int
    title: str
    price: float
    author_id: int

    class Config:
        from_attributes = True


class BookWithAuthorResponse(BaseModel):
    title: str
    price: float
    author_name: str
    author_email: EmailStr


class BookRankingResponse(BaseModel):
    title: str
    price: float
    author_name: str
    rank: int

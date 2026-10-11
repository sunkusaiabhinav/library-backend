from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

app = FastAPI(title="Library Management API")


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Library API is running"}


@app.get("/test-db")
def test_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": result.scalar()}


@app.post(
    "/authors",
    response_model=schemas.AuthorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    new_author = models.Author(name=author.name, email=author.email)

    db.add(new_author)
    db.commit()
    db.refresh(new_author)

    return new_author


@app.get("/authors", response_model=list[schemas.AuthorResponse])
def get_authors(db: Session = Depends(get_db)):
    authors = db.query(models.Author).all()

    return authors


@app.get("/authors/{author_id}", response_model=schemas.AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    return author


@app.put("/authors/{author_id}", response_model=schemas.AuthorResponse)
def update_author(
    author_id: int, author_data: schemas.AuthorUpdate, db: Session = Depends(get_db)
):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    author.name = author_data.name
    author.email = author_data.email

    db.commit()
    db.refresh(author)

    return author


@app.delete("/authors/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    db.delete(author)
    db.commit()


# -------------------------
# CREATE BOOK
# -------------------------


@app.post(
    "/books", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED
)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):

    # Check whether author exists
    author = db.query(models.Author).filter(models.Author.id == book.author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    new_book = models.Book(title=book.title, price=book.price, author_id=book.author_id)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


# -------------------------
# GET ALL BOOKS
# -------------------------


@app.get("/books", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):

    books = db.query(models.Book).all()

    return books


# -------------------------
# UPDATE BOOK
# -------------------------


@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int, book_data: schemas.BookUpdate, db: Session = Depends(get_db)
):

    # Find existing book
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Verify new author exists
    author = (
        db.query(models.Author).filter(models.Author.id == book_data.author_id).first()
    )

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Update fields
    book.title = book_data.title
    book.price = book_data.price
    book.author_id = book_data.author_id

    db.commit()
    db.refresh(book)

    return book


# -------------------------
# DELETE BOOK
# -------------------------


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):

    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()


# ==========================================
# BOOKS - STATIC / SPECIFIC ROUTES FIRST
# ==========================================


@app.get("/books/with-authors")
def get_books_with_authors(db: Session = Depends(get_db)):

    results = (
        db.query(
            models.Book.title,
            models.Book.price,
            models.Author.name.label("author_name"),
            models.Author.email.label("author_email"),
        )
        .join(models.Author, models.Book.author_id == models.Author.id)
        .all()
    )

    return [
        {
            "title": row.title,
            "price": row.price,
            "author_name": row.author_name,
            "author_email": row.author_email,
        }
        for row in results
    ]


@app.get("/books/ranked")
def get_ranked_books(db: Session = Depends(get_db)):

    rank = func.row_number().over(order_by=models.Book.price.desc()).label("rank")

    results = (
        db.query(
            models.Book.title,
            models.Book.price,
            models.Author.name.label("author_name"),
            rank,
        )
        .join(models.Author, models.Book.author_id == models.Author.id)
        .all()
    )

    return [
        {
            "title": row.title,
            "price": row.price,
            "author_name": row.author_name,
            "rank": row.rank,
        }
        for row in results
    ]


# ==========================================
# GET BOOK BY ID
# ==========================================


@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):

    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book

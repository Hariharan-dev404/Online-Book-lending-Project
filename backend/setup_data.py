import os
import django
from django.core.files import File
import urllib.request
from tempfile import NamedTemporaryFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_lending_backend.settings')
django.setup()

from api.models import User, Book

def create_users():
    # Admin
    if not User.objects.filter(email='admin@pageloft.com').exists():
        User.objects.create_superuser('admin@pageloft.com', 'Admin User', 'admin123')
        print("Created Admin: admin@pageloft.com / admin123")
    
    # Normal user
    if not User.objects.filter(email='user@pageloft.com').exists():
        User.objects.create_user('user@pageloft.com', 'Regular User', 'user123')
        print("Created User: user@pageloft.com / user123")

def download_image(url):
    try:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib.request.urlopen(url).read())
        img_temp.flush()
        return img_temp
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        return None

def create_books():
    books_data = [
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'genre': 'Fiction',
            'price': 499.00,
            'lending_price': 99.00,
            'stock': 15,
            'description': 'A novel set in the Jazz Age that tells the story of millionaire Jay Gatsby.',
            'image_url': 'https://covers.openlibrary.org/b/id/8091016-L.jpg'
        },
        {
            'title': '1984',
            'author': 'George Orwell',
            'genre': 'Fiction',
            'price': 399.00,
            'lending_price': 79.00,
            'stock': 20,
            'description': 'A dystopian social science fiction novel and cautionary tale about the dangers of totalitarianism.',
            'image_url': 'https://covers.openlibrary.org/b/id/7890312-L.jpg'
        },
        {
            'title': 'Dune',
            'author': 'Frank Herbert',
            'genre': 'Fantasy',
            'price': 799.00,
            'lending_price': 149.00,
            'stock': 10,
            'description': 'Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides.',
            'image_url': 'https://covers.openlibrary.org/b/id/8739161-L.jpg'
        },
        {
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'genre': 'Romance',
            'price': 350.00,
            'lending_price': 50.00,
            'stock': 25,
            'description': 'A romantic novel of manners written by Jane Austen in 1813.',
            'image_url': 'https://covers.openlibrary.org/b/id/8259431-L.jpg'
        },
        {
            'title': 'Sapiens: A Brief History of Humankind',
            'author': 'Yuval Noah Harari',
            'genre': 'Education',
            'price': 999.00,
            'lending_price': 199.00,
            'stock': 5,
            'description': 'A book by Professor Yuval Noah Harari that surveys the history of humankind.',
            'image_url': 'https://covers.openlibrary.org/b/id/7516825-L.jpg'
        }
    ]

    for data in books_data:
        if not Book.objects.filter(title=data['title']).exists():
            print(f"Adding book: {data['title']}")
            book = Book.objects.create(
                title=data['title'],
                author=data['author'],
                genre=data['genre'],
                price=data['price'],
                lending_price=data['lending_price'],
                stock=data['stock'],
                description=data['description']
            )
            # Download and save the image
            img_temp = download_image(data['image_url'])
            if img_temp:
                filename = data['title'].replace(' ', '_').lower() + '.jpg'
                book.image.save(filename, File(img_temp), save=True)
                print(f"Added image for {data['title']}")

if __name__ == "__main__":
    create_users()
    create_books()
    print("Done!")

from django.test import TestCase


from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Book, BorrowRequest

class LibraryAPITests(APITestCase):

    def setUp(self):
        # Create a librarian user
        self.librarian = User.objects.create_user(username='librarian', password='librarianpassword')
        self.client.login(username='librarian', password='librarianpassword')

        # Create a library user
        self.library_user = User.objects.create_user(username='library_user', password='userpassword')

        # Create a book
        self.book = Book.objects.create(title='Sample Book', author='Author Name')

    def test_create_library_user(self):
        url = reverse('user-list')  # Adjust according to your URL naming
        data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "securepassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_view_borrow_requests(self):
        url = reverse('borrow-request-list')  # Adjust according to your URL naming
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_borrow_request(self):
        # Create a borrow request
        borrow_request = BorrowRequest.objects.create(user=self.library_user, book=self.book, start_date='2023-10-01', end_date='2023-10-10')
        url = reverse('borrow-request-approve', args=[borrow_request.id])  # Adjust according to your URL naming
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deny_borrow_request(self):
        # Create a borrow request
        borrow_request = BorrowRequest.objects.create(user=self.library_user, book=self.book, start_date='2023-10-01', end_date='2023-10-10')
        url = reverse('borrow-request-deny', args=[borrow_request.id])  # Adjust according to your URL naming
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_user_borrow_history(self):
        # Create a borrow request
        borrow_request = BorrowRequest.objects.create(user=self.library_user, book=self.book, start_date='2023-10-01', end_date='2023-10-10')
        url = reverse('user-borrow-history', args=[self.library_user.id])  # Adjust according to your URL naming
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submit_borrow_request(self):
        url = reverse('borrow-request-list')  # Adjust according to your URL naming
        data = {
            "book": self.book.id,
            "start_date": "2023-10-01",
            "end_date": "2023-10-10"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_overlapping_borrow_dates(self):
        # Create an initial borrow request
        BorrowRequest.objects.create(user=self.library_user, book=self.book, start_date='2023-10-01', end_date='2023-10-05')
        url = reverse('borrow-request-list')  # Adjust according to your URL naming
        data = {
            "book": self.book.id,
            "start_date": "2023-10-03",
            "end_date": "2023-10-07"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_user_id(self):
        url = reverse('user-borrow-history', args=[999])  # Non-existent user ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_book_id(self):
        url = reverse('borrow-request-list')  # Adjust according to your URL naming
        data = {
            "book": 999,  # Non-existent book ID
            "start_date": "2023-10-01",
            "end_date": "2023-10-10"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
# library/tests.py (continued)

    def test_create_borrow_request_with_missing_fields(self):
        url = reverse('borrow-request-list')  # Adjust according to your URL naming
        data = {
            "start_date": "2023-10-01"  # Missing 'book' and 'end_date'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_books(self):
        url = reverse('book-list')  # Adjust according to your URL naming
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_personal_borrow_history(self):
        # Create a borrow request for the library user
        BorrowRequest.objects.create(user=self.library_user, book=self.book, start_date='2023-10-01', end_date='2023-10-10')
        url = reverse('user-borrow-history', args=[self.library_user.id])  # Adjust according to your URL naming
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.book.title)

    def test_approve_non_existent_borrow_request(self):
        url = reverse('borrow-request-approve', args=[999])  # Non-existent request ID
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deny_non_existent_borrow_request(self):
        url = reverse('borrow-request-deny', args=[999])  # Non-existent request ID
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_borrow_request_with_invalid_dates(self):
        url = reverse('borrow-request-list')  # Adjust according to your URL naming
        data = {
            "book": self.book.id,
            "start_date": "2023-10-10",
            "end_date": "2023-10-01"  # Invalid date range
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_borrow_requests_for_non_existent_user(self):
        url = reverse('user-borrow-history', args=[999])  # Non-existent user ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# library/tests.py (continued)

    def test_create_borrow_request_with_invalid_book(self):
        url = reverse('borrow-request-list')  # Adjust according to your URL naming
        data = {
            "book": 999,  # Non-existent book ID
            "start_date": "2023-10-01",
            "end_date": "2023-10-10"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_borrow_history_for_user_with_no_requests(self):
        url = reverse('user-borrow-history', args=[self.library_user.id])  # Adjust according to your URL naming
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Expecting an empty list

    def test_approve_borrow_request_with_invalid_user(self):
        # Create a borrow request
        borrow_request = BorrowRequest.objects.create(user=self.library_user, book=self.book, start_date='2023-10-01', end_date='2023-10-10')
        self.client.logout()  # Log out the librarian
        self.client.login(username='library_user', password='userpassword')  # Log in as a regular user
        url = reverse('borrow-request-approve', args=[borrow_request.id])  # Adjust according to your URL naming
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Expecting forbidden access

    def test_deny_borrow_request_with_invalid_user(self):
        # Create a borrow request
        borrow_request = BorrowRequest.objects.create(user=self.library_user, book=self.book, start_date='2023-10-01', end_date='2023-10-10')
        self.client.logout()  # Log out the librarian
        self.client.login(username='library_user', password='userpassword')  # Log in as a regular user
        url = reverse('borrow-request-deny', args=[borrow_request.id])  # Adjust according to your URL naming
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Expecting forbidden access

    def test_get_books_with_authentication(self):
        url = reverse('book-list')  # Adjust according to your URL naming
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_books_without_authentication(self):
        self.client.logout()  # Log out
        url = reverse('book-list')  # Adjust according to your URL naming
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Expecting forbidden access
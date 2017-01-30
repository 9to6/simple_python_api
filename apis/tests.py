from django.test import TestCase, RequestFactory
from django.urls import reverse
from requests.auth import HTTPBasicAuth
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import Client
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient

from apis import views
from apis.models import CustomUser
import base64

class BaseTestCase(TestCase):
    def create_users(self):
        user_infos = list()
        user = CustomUser.objects.create_superuser('robert@test.com', '12345', nick='robert')
        user = CustomUser.objects.create(nick='jane', email='jane@test.com', age=15)
        user.set_password('12345')
        user.save()
        CustomUser.objects.create(nick='tom', email='tom@test.com', age=25)
    def login(self, nick='robert'):
        client = APIClient()
        user = CustomUser.objects.get(nick=nick)
        client.force_authenticate(user=user)
        return client

# python manage.py test apis.tests.UserListGetTestCase
class UserListGetTestCase(BaseTestCase):
    def test_check_auth(self):
        print '\n----- test_check_auth -----'
        self.create_users()
        resp = self.client.get('/users/')
        self.assertEqual(resp.status_code, 403)
    
    def test_user_list_admin(self):
        print '\n----- test_user_list_admin -----'
        self.create_users()
        client = self.login('robert')
        resp = client.get('/users/')
        self.assertEqual(resp.status_code, 200)
    
    def test_user_list_user(self):
        print '\n----- test_user_list_user -----'
        self.create_users()
        client = self.login('jane')
        resp = client.get('/users/')
        self.assertEqual(resp.status_code, 401)

class UserListPostTestCase(BaseTestCase):
    def test_user_list_post_admin(self):
        print '\n----- test_user_list_post_admin -----'
        self.create_users()
        client = self.login('robert')
        resp = client.post('/users/', {'nick': 'test2', 'email': 'test@test.com', 'password': '1234', 'age': 12, 'first_name': 'a', 'last_name': 'b'}, format='json')
        self.assertEqual(resp.status_code, 201)
        
    def test_user_list_post_user(self):
        print '\n----- test_user_list_post_user -----'
        self.create_users()
        client = self.login('jane')
        resp = client.post('/users/', {'nick': 'test2', 'email': 'test@test.com', 'password': '1234', 'age': 12, 'first_name': 'a', 'last_name': 'b'}, format='json')
        self.assertEqual(resp.status_code, 401)
        
    def test_user_list_post_unauthorized(self):
        print '\n----- test_user_list_post_unauthorized -----'
        resp = self.client.post('/users/', {'nick': 'test2', 'email': 'test@test.com', 'password': '1234', 'age': 12, 'first_name': 'a', 'last_name': 'b'}, format='json')
        self.assertEqual(resp.status_code, 403)
#         factory = APIRequestFactory()
#         request = factory.post('/users/', {'nick': 'test2', 'email': 'test@test.com', 'age': 12, 'first_name': 'a', 'last_name': 'b'}, format='json')
#         print request
#         self.client.defaults['HTTP_AUTHORIZATION'] = "Basic " + base64.b64encode('jane@test.com:12345')
#         resp = self.client.post('/users/', 
#                                 {'nick': 'test2', 'email': 'test@test.com', 'age': 12, 'first_name': 'a', 'last_name': 'b'}, format='json')

class UserDetailGetTestCase(BaseTestCase):
    def test_user_get_admin(self):
        print '\n----- test_user_get_admin -----'
        self.create_users()
        client = self.login('robert')
        resp = client.get('/users/2/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'jane', 2, 200)
        
    def test_user_get_user(self):
        print '\n----- test_user_get_user -----'
        self.create_users()
        client = self.login('jane')
        resp = client.get('/users/2/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'jane', 2, 200)
        
    def test_user_get_unauthorized(self):
        print '\n----- test_user_get_unauthorized -----'
        self.create_users()
        resp = self.client.get('/users/2/')
        self.assertEqual(resp.status_code, 403)
        
class UserDetailPutTestCase(BaseTestCase):
    def test_user_put_admin(self):
        print '\n----- test_user_put_admin -----'
        self.create_users()
        client = self.login('robert')
        resp = client.put('/users/2/', {"nick": "kane", "email": "kane@test.com", 'password': '1234', "age": 15, "first_name": "cage", "last_name": "Kane"}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'kane', 2, 200)
        
    def test_user_put_user(self):
        print '\n----- test_user_put_user -----'
        self.create_users()
        client = self.login('jane')
        resp = client.put('/users/2/', {"nick": "kane", "email": "kane@test.com", 'password': '1234', "age": 15, "first_name": "cage", "last_name": "Kane"}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'kane', 2, 200)
        
    def test_user_put_unauthorized(self):
        print '\n----- test_user_put_unauthorized -----'
        self.create_users()
        resp = self.client.put('/users/2/', {"nick": "kane", "email": "kane@test.com", 'password': '1234', "age": 15, "first_name": "cage", "last_name": "Kane"}, format='json')
        self.assertEqual(resp.status_code, 403)
        
    def test_user_put_user_invalid_params(self):
        print '\n----- test_user_put_user_invalid_params -----'
        self.create_users()
        client = self.login('jane')
        resp = client.put('/users/2/', {"email": "kane@test.com", 'password': '1234', "age": 15, "first_name": "cage", "last_name": "Kane"}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'invalid', 1, 400)
        
class UserDetailPatchTestCase(BaseTestCase):
    def test_user_patch_admin(self):
        print '\n----- test_user_patch_admin -----'
        self.create_users()
        client = self.login('robert')
        resp = client.patch('/users/2/', {"first_name": "cage", "last_name": "cage"}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'cage', 2, 200)
        
    def test_user_patch_user(self):
        print '\n----- test_user_patch_user -----'
        self.create_users()
        client = self.login('jane')
        resp = client.patch('/users/2/', {"first_name": "cage", "last_name": "cage"}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'cage', 2, 200)
        
    def test_user_patch_unauthorized(self):
        print '\n----- test_user_patch_unauthorized -----'
        self.create_users()
        resp = self.client.patch('/users/2/', {"first_name": "cage", "last_name": "cage"}, format='json')
        self.assertEqual(resp.status_code, 403)

class UserDetailDeleteTestCase(BaseTestCase):
    def test_user_delete_admin(self):
        print '\n----- test_user_delete_admin -----'
        self.create_users()
        client = self.login('robert')
        resp = client.delete('/users/2/', {}, format='json')
        self.assertEqual(resp.status_code, 204)
        
    def test_user_delete_user(self):
        print '\n----- test_user_delete_user -----'
        self.create_users()
        client = self.login('jane')
        resp = client.delete('/users/2/', {}, format='json')
        self.assertEqual(resp.status_code, 401)
        
    def test_user_delete_user_unauthorized(self):
        print '\n----- test_user_delete_user_unauthorized -----'
        self.create_users()
        resp = self.client.delete('/users/2/', {}, format='json')
        self.assertEqual(resp.status_code, 403)
        
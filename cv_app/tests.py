from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import StudentCV

class StudentCVAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create Student A
        self.cv_a = StudentCV.objects.create(
            name="Farzana Sadia Takeei",
            student_id="2211175",
            email="2211175@iub.edu.bd",
            education="BSc in CSE",
            skills=["Flutter", "Python", "Cybersecurity"],
            experience="Software Development",
            bio="Passionate about mobile security",
        )
        self.cv_a.set_passcode("1234")
        self.cv_a.save()

        # Create Student B
        self.cv_b = StudentCV.objects.create(
            name="Md. Jariful Abedin Ovi",
            student_id="2230907",
            email="2230907@iub.edu.bd",
            education="BSc in CSE",
            skills=["Flutter", "Dart", "Django"],
            experience="Mobile Apps",
            bio="Flutter developer",
        )
        self.cv_b.set_passcode("2230907")
        self.cv_b.save()

    def test_get_all_cvs(self):
        """Student B or C opens the CV directory and sees all students' CVs"""
        response = self.client.get('/api/cvs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 2)

    def test_get_single_cv(self):
        """Student B can view Student A's specific CV"""
        response = self.client.get(f'/api/cvs/{self.cv_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['id'], self.cv_a.id)
        self.assertEqual(data['name'], "Farzana Sadia Takeei")

    def test_student_login_success(self):
        """Individual login with student_id and password succeeds and returns token"""
        login_payload = {
            "student_id": "2230907",
            "password": "2230907"
        }
        response = self.client.post('/api/auth/login/', data=login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(len(data['token']) > 10)
        self.assertEqual(data['cv']['student_id'], "2230907")

    def test_student_login_wrong_password(self):
        """Individual login with incorrect password returns 401 Unauthorized"""
        login_payload = {
            "student_id": "2230907",
            "password": "wrong_password"
        }
        response = self.client.post('/api/auth/login/', data=login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Incorrect password", response.json()['error'])

    def test_student_b_cannot_modify_student_a(self):
        """Student B is logged in, but tries to update Student A's CV -> 403 Forbidden"""
        # Log in as Student B
        token_b = self.cv_b.generate_token()

        update_payload = {
            "name": "Tampered Name By Student B",
            "student_id": "2211175",
            "email": "2211175@iub.edu.bd"
        }
        response = self.client.put(
            f'/api/cvs/{self.cv_a.id}/',
            data=update_payload,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {token_b}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Verify in DB that Student A's CV was not changed
        self.cv_a.refresh_from_db()
        self.assertEqual(self.cv_a.name, "Farzana Sadia Takeei")

    def test_student_a_can_update_own_cv(self):
        """Student A is logged in and updates their own CV -> 200 OK"""
        token_a = self.cv_a.generate_token()

        update_payload = {
            "name": "Farzana Sadia Takeei (Updated)",
            "student_id": "2211175",
            "email": "2211175@iub.edu.bd",
            "education": "BSc in CSE",
            "skills": ["Flutter", "Python", "Cybersecurity", "Django REST"],
            "experience": "Lead Engineer"
        }
        response = self.client.put(
            f'/api/cvs/{self.cv_a.id}/',
            data=update_payload,
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {token_a}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cv_a.refresh_from_db()
        self.assertEqual(self.cv_a.name, "Farzana Sadia Takeei (Updated)")

    def test_student_registration(self):
        """New student registers with individual password and creates their CV"""
        reg_payload = {
            "name": "David Miller",
            "student_id": "2299881",
            "email": "david@iub.edu.bd",
            "password": "mypassword123",
            "education": "BSc in CSE",
            "skills": ["Java", "Spring Boot", "SQL"],
            "experience": "Backend Developer"
        }
        response = self.client.post('/api/auth/register/', data=reg_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cv']['student_id'], "2299881")
        # Ensure student can now log in
        login_res = self.client.post('/api/auth/login/', data={"student_id": "2299881", "password": "mypassword123"}, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

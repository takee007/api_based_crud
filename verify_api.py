import os
import sys
import django
import json

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cv_project.settings')
django.setup()

from rest_framework.test import APIClient

def run_live_verification():
    print("==================================================")
    print("🚀 RUNNING END-TO-END REST API & LOGIN VERIFICATION")
    print("==================================================")
    
    client = APIClient()

    # 1. INDIVIDUAL STUDENT LOGIN (POST /api/auth/login/)
    print("\n[TEST 1] POST /api/auth/login/ (Student B logs in individually with password)")
    login_res = client.post('/api/auth/login/', data={
        "student_id": "2230907",
        "password": "2230907"
    }, format='json')
    print(f"Status Code: {login_res.status_code}")
    login_data = login_res.json()
    assert login_res.status_code == 200
    assert login_data['success'] is True
    token_b = login_data['token']
    print(f"Logged in as: {login_data['cv']['name']} (ID: {login_data['cv']['student_id']})")
    print(f"Active Token: {token_b[:12]}...")

    # 2. INCORRECT PASSWORD CHECK
    print("\n[TEST 2] POST /api/auth/login/ with wrong password (Should return 401)")
    wrong_login = client.post('/api/auth/login/', data={
        "student_id": "2230907",
        "password": "wrongpassword123"
    }, format='json')
    print(f"Status Code: {wrong_login.status_code} (Expected 401)")
    assert wrong_login.status_code == 401

    # 3. READ DIRECTORY (GET /api/cvs/)
    print("\n[TEST 3] GET /api/cvs/ (Logged in student views all classmates' CVs)")
    r_dir = client.get('/api/cvs/', HTTP_AUTHORIZATION=f"Bearer {token_b}")
    print(f"Status Code: {r_dir.status_code}")
    all_cvs = r_dir.json()
    print(f"Total CVs visible in shared database: {len(all_cvs)}")
    assert r_dir.status_code == 200

    # 4. VIEW SPECIFIC CLASSMATE'S CV (GET /api/cvs/101/)
    print("\n[TEST 4] GET /api/cvs/101/ (Student B views Student A's CV)")
    r_a = client.get('/api/cvs/101/', HTTP_AUTHORIZATION=f"Bearer {token_b}")
    print(f"Status Code: {r_a.status_code}")
    assert r_a.status_code == 200
    cv_a = r_a.json()
    print(f"Classmate Name: {cv_a['name']} | Degree: {cv_a['education']}")

    # 5. COLLABORATIVE EDIT OF CLASSMATE'S CV (Everyone can edit)
    print("\n[TEST 5] PUT /api/cvs/101/ (Student B edits Student A's CV - Collaborative Access)")
    collab_res = client.put(
        '/api/cvs/101/',
        data={
            "name": "Farzana Sadia Takeei (Updated by Peer)",
            "student_id": "2211175",
            "email": "2211175@iub.edu.bd",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["Flutter", "Python", "Cybersecurity", "REST API", "Docker"],
            "experience": "Software Development & Mobile Apps"
        },
        format='json',
        HTTP_AUTHORIZATION=f"Bearer {token_b}"
    )
    print(f"Status Code: {collab_res.status_code} (Expected 200 OK)")
    assert collab_res.status_code == 200
    print(f"Updated Student A Name: {collab_res.json()['name']}")

    # 6. UPDATE OWN CV (Authorized 200 OK)
    print("\n[TEST 6] PUT /api/cvs/102/ (Student B updates their OWN CV with Bearer token)")
    update_own = client.put(
        '/api/cvs/102/',
        data={
            "name": "Md. Jariful Abedin Ovi",
            "student_id": "2230907",
            "email": "2230907@iub.edu.bd",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["Flutter", "Dart", "Django REST Framework", "Python", "PostgreSQL", "Docker"],
            "experience": "Senior Flutter Developer & API Architect"
        },
        format='json',
        HTTP_AUTHORIZATION=f"Bearer {token_b}"
    )
    print(f"Status Code: {update_own.status_code}")
    assert update_own.status_code == 200
    print(f"Updated Skills: {update_own.json()['skills']}")

    print("\n==================================================")
    print("🎉 INDIVIDUAL LOGIN & PERMISSION CHECKS VERIFIED 100%!")
    print("==================================================")

if __name__ == '__main__':
    run_live_verification()

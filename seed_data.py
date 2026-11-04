import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cv_project.settings')
django.setup()

from cv_app.models import StudentCV

def seed():
    print("Seeding initial student CV records...")
    
    # We clear existing records if re-seeding
    StudentCV.objects.all().delete()
    
    cvs = [
        {
            "id": 101,
            "name": "Farzana Sadia Takeei",
            "student_id": "2211175",
            "email": "2211175@iub.edu.bd",
            "phone": "+880 1712-345678",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["Flutter", "Python", "Cybersecurity", "REST API"],
            "experience": "Software Development & Mobile Apps",
            "bio": "Undergraduate CSE student at Independent University, Bangladesh (IUB). Passionate about mobile security, Flutter development, and full-stack REST APIs.",
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
            "passcode": "1234",
        },
        {
            "id": 102,
            "name": "Md. Jariful Abedin Ovi",
            "student_id": "2230907",
            "email": "2230907@iub.edu.bd",
            "phone": "+880 1812-987654",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["Flutter", "Dart", "Django REST Framework", "Python", "PostgreSQL"],
            "experience": "Flutter Developer & API Engineer",
            "bio": "Passionate about mobile app development using Flutter. Love designing intuitive, modern user interfaces and writing efficient, clean code to solve real-world problems. In my spare time, I explore backend APIs and work on open-source projects.",
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
            "passcode": "2230907",
        },
        {
            "id": 103,
            "name": "Tanvir Hasan",
            "student_id": "2220451",
            "email": "2220451@iub.edu.bd",
            "phone": "+880 1912-456789",
            "education": "BSc in Software Engineering",
            "skills": ["Python", "PostgreSQL", "Docker", "FastAPI", "Linux"],
            "experience": "Backend & Cloud Infrastructure Engineer",
            "bio": "Focused on distributed database architectures, cloud deployments on Render/AWS, and scalable RESTful API microservices.",
            "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
            "passcode": "1234",
        },
        {
            "id": 104,
            "name": "Ayesha Siddiqua",
            "student_id": "2221304",
            "email": "2221304@iub.edu.bd",
            "phone": "+880 1723-889900",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["React", "Next.js", "TypeScript", "Tailwind CSS", "Redux"],
            "experience": "Frontend Web Developer & Open-Source Contributor",
            "bio": "Specializing in high-performance Single Page Applications (SPAs) and accessible UI design. Experienced with modern component libraries and state management.",
            "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80",
            "passcode": "1234",
        },
        {
            "id": 105,
            "name": "Naimur Rahman",
            "student_id": "2231580",
            "email": "2231580@iub.edu.bd",
            "phone": "+880 1622-445566",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["Python", "Machine Learning", "PyTorch", "Computer Vision", "Scikit-Learn"],
            "experience": "AI & Deep Learning Researcher",
            "bio": "Passionate about applying deep learning to medical imaging and NLP tasks. Active Kaggle competitor and AI workshop mentor.",
            "avatar_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=400&q=80",
            "passcode": "1234",
        },
        {
            "id": 106,
            "name": "Sabrina Jahan",
            "student_id": "2210892",
            "email": "2210892@iub.edu.bd",
            "phone": "+880 1833-771122",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["UI/UX Design", "Figma", "User Research", "Wireframing", "HTML/CSS"],
            "experience": "Product Designer & UX Researcher",
            "bio": "Obsessed with human-computer interaction, clean design systems, and converting complex user flows into effortless digital experiences.",
            "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
            "passcode": "1234",
        },
        {
            "id": 107,
            "name": "Mehedi Hasan Rafi",
            "student_id": "2230419",
            "email": "2230419@iub.edu.bd",
            "phone": "+880 1944-663322",
            "education": "BSc in Software Engineering",
            "skills": ["Cybersecurity", "Penetration Testing", "Wireshark", "Network Security", "Linux"],
            "experience": "Ethical Hacker & CTF Competitor",
            "bio": "Member of university cybersecurity club and competitive CTF player. Experienced in web application vulnerability analysis and server hardening.",
            "avatar_url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=400&q=80",
            "passcode": "1234",
        },
        {
            "id": 108,
            "name": "Nusrat Sharmin",
            "student_id": "2220764",
            "email": "2220764@iub.edu.bd",
            "phone": "+880 1755-998877",
            "education": "BSc in Computer Science & Engineering",
            "skills": ["Data Science", "PostgreSQL", "SQL", "Pandas", "Power BI", "Tableau"],
            "experience": "Data Analyst & Business Intelligence Specialist",
            "bio": "Turning raw database records into actionable visual insights and predictive dashboards. Passionate about big data processing and ETL pipelines.",
            "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80",
            "passcode": "1234",
        }
    ]

    for item in cvs:
        pin = item.pop("passcode")
        cv = StudentCV.objects.create(**item)
        cv.set_passcode(pin)
        cv.save()
        print(f"Created Student CV #{cv.id}: {cv.name} ({cv.student_id}) - {cv.experience}")

    print(f"\nDatabase seeded successfully with {len(cvs)} student CV records!")

if __name__ == '__main__':
    seed()

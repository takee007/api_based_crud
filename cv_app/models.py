import hashlib
import secrets
from django.db import models

class StudentCV(models.Model):
    name = models.CharField(max_length=150, help_text="Full Name of the student")
    student_id = models.CharField(max_length=50, unique=True, db_index=True, help_text="Unique Student ID (e.g. 2230907)")
    email = models.CharField(max_length=150, help_text="Email or student contact")
    phone = models.CharField(max_length=50, blank=True, default='')
    education = models.CharField(max_length=255, default='BSc in CSE', help_text="Degree or Department")
    skills = models.JSONField(default=list, help_text="List of technical skills")
    experience = models.TextField(blank=True, default='Software Development', help_text="Work/Project Experience")
    bio = models.TextField(blank=True, default='', help_text="Bio or personal introduction")
    avatar_url = models.CharField(
        max_length=500,
        blank=True,
        default='https://api.dicebear.com/7.x/avataaars/svg?seed=student',
        help_text="URL to profile avatar or photo"
    )
    passcode_hash = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text="SHA-256 hash of student login password / secret PIN"
    )
    auth_token = models.CharField(
        max_length=64,
        blank=True,
        default='',
        db_index=True,
        help_text="Active login session token"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Student CV'
        verbose_name_plural = 'Student CVs'

    def __str__(self):
        return f"{self.name} ({self.student_id}) - #{self.id}"

    @staticmethod
    def hash_pin(pin: str) -> str:
        if not pin:
            return ''
        return hashlib.sha256(str(pin).strip().encode('utf-8')).hexdigest()

    def set_passcode(self, raw_pin: str):
        if raw_pin:
            self.passcode_hash = self.hash_pin(raw_pin)

    def check_passcode(self, raw_pin: str) -> bool:
        if not self.passcode_hash or not raw_pin:
            return False
        return self.passcode_hash == self.hash_pin(raw_pin)

    def set_password(self, raw_password: str):
        self.set_passcode(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return self.check_passcode(raw_password)

    def generate_token(self) -> str:
        self.auth_token = secrets.token_hex(24)
        self.save(update_fields=['auth_token'])
        return self.auth_token

from rest_framework import serializers
from .models import StudentCV

class StudentCVSerializer(serializers.ModelSerializer):
    passcode = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Secret PIN/Passcode. Only someone with this PIN can update or delete this CV."
    )

    class Meta:
        model = StudentCV
        fields = [
            'id',
            'name',
            'student_id',
            'email',
            'education',
            'skills',
            'experience',
            'bio',
            'phone',
            'avatar_url',
            'passcode',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_skills(self, value):
        # Handle string input (e.g. comma-separated from form or Postman)
        if isinstance(value, str):
            skills = [s.strip() for s in value.split(',') if s.strip()]
            return skills
        if isinstance(value, list):
            return [str(s).strip() for s in value if str(s).strip()]
        return []

    def create(self, validated_data):
        raw_pin = validated_data.pop('passcode', None)
        # If no PIN provided, default PIN to student_id
        if not raw_pin:
            raw_pin = validated_data.get('student_id', '1234')

        cv = StudentCV.objects.create(**validated_data)
        cv.set_passcode(raw_pin)
        cv.save()
        return cv

    def update(self, instance, validated_data):
        raw_pin = validated_data.pop('passcode', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if raw_pin:
            instance.set_passcode(raw_pin)
        instance.save()
        return instance


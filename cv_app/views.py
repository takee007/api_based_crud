from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Q
from .models import StudentCV
from .serializers import StudentCVSerializer

class StudentCVViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Student CVs.
    - POST   /api/cvs/     : Create and save a new CV
    - GET    /api/cvs/     : List all students' CVs (Directory)
    - GET    /api/cvs/<id>/: View a particular student's CV
    - PUT    /api/cvs/<id>/: Update a CV (Only authenticated owner or valid PIN)
    - PATCH  /api/cvs/<id>/: Partial update a CV (Only authenticated owner or valid PIN)
    - DELETE /api/cvs/<id>/: Delete a CV (Only authenticated owner or valid PIN)
    """
    queryset = StudentCV.objects.all()
    serializer_class = StudentCVSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get('search') or self.request.query_params.get('q')
        if query:
            query = query.strip()
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(student_id__icontains=query) |
                Q(email__icontains=query) |
                Q(education__icontains=query) |
                Q(skills__icontains=query)
            )
        return queryset

    def _extract_token(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split('Bearer ', 1)[1].strip()
        token = request.headers.get('X-Auth-Token', '')
        return token.strip() if token else ''

    def _extract_pin(self, request):
        pin = request.headers.get('X-CV-PIN')
        if not pin and hasattr(request, 'data') and isinstance(request.data, dict):
            pin = request.data.get('passcode') or request.data.get('pin') or request.data.get('password')
        if not pin:
            pin = request.query_params.get('pin') or request.query_params.get('passcode')
        return str(pin).strip() if pin else ''

    def update(self, request, *args, **kwargs):
        # Open collaborative access: everyone can edit any student's CV
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Open collaborative access: everyone can edit any student's CV
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        instance_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {"message": f"CV #{instance_id} for '{instance_name}' deleted successfully."},
            status=status.HTTP_200_OK
        )


# ==========================================
# Individual Student Authentication Views
# ==========================================

class StudentLoginView(APIView):
    """
    POST /api/auth/login/
    Individual login with student_id / email and password.
    """
    def post(self, request):
        identifier = str(request.data.get('student_id') or request.data.get('email') or '').strip()
        password = str(request.data.get('password') or '').strip()

        if not identifier or not password:
            return Response(
                {"error": "Please provide both Student ID (or Email) and Password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Look up student by student_id or email
        student = StudentCV.objects.filter(
            Q(student_id__iexact=identifier) | Q(email__iexact=identifier)
        ).first()

        if not student:
            return Response(
                {"error": f"No student CV found matching '{identifier}'."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not student.check_password(password):
            return Response(
                {"error": "Incorrect password. Please verify your password and try again."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate active login session token
        token = student.generate_token()
        cv_data = StudentCVSerializer(student).data

        return Response({
            "success": True,
            "message": f"Welcome back, {student.name}!",
            "token": token,
            "cv": cv_data
        }, status=status.HTTP_200_OK)


class StudentRegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new individual student account and CV simultaneously.
    """
    def post(self, request):
        student_id = str(request.data.get('student_id', '')).strip()
        password = str(request.data.get('password', '')).strip()
        name = str(request.data.get('name', '')).strip()
        email = str(request.data.get('email', '')).strip()

        if not student_id or not password or not name or not email:
            return Response(
                {"error": "Name, Student ID, Email, and Password are all required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if StudentCV.objects.filter(student_id=student_id).exists():
            return Response(
                {"error": f"A student CV with ID '{student_id}' already exists. Please log in instead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = StudentCVSerializer(data=request.data)
        if serializer.is_valid():
            cv = serializer.save()
            cv.set_password(password)
            cv.save()
            token = cv.generate_token()
            return Response({
                "success": True,
                "message": f"Account created and CV saved for {cv.name}!",
                "token": token,
                "cv": StudentCVSerializer(cv).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentMeView(APIView):
    """
    GET /api/auth/me/
    Retrieve the currently logged-in student's CV using Bearer token.
    """
    def get(self, request):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split('Bearer ', 1)[1].strip() if auth_header.startswith('Bearer ') else request.headers.get('X-Auth-Token', '').strip()

        if not token:
            return Response({"error": "Authentication token missing."}, status=status.HTTP_401_UNAUTHORIZED)

        student = StudentCV.objects.filter(auth_token=token).first()
        if not student:
            return Response({"error": "Invalid or expired session. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "success": True,
            "cv": StudentCVSerializer(student).data
        })


class StudentLogoutView(APIView):
    """
    POST /api/auth/logout/
    Log out and invalidate session token.
    """
    def post(self, request):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split('Bearer ', 1)[1].strip() if auth_header.startswith('Bearer ') else request.headers.get('X-Auth-Token', '').strip()

        if token:
            student = StudentCV.objects.filter(auth_token=token).first()
            if student:
                student.auth_token = ''
                student.save(update_fields=['auth_token'])

        return Response({"success": True, "message": "Logged out successfully."})

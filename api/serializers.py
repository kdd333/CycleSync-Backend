from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Workout, WorkoutExercise, Exercise, ExerciseType, WorkoutLog, Phase, Cycle, CyclePhase, CycleLog, CycleLogSymptom, Symptom

# Custom user serializer for signup
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'menstrual_length', 'follicular_length', 'ovulation_length', 'luteal_length')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


# Serializer for returning JWT tokens after login
class TokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = get_user_model().objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        else:
            raise serializers.ValidationError("Invalid credentials")
        

class ExerciseTypeSerializer(serializers.ModelSerializer):
    """Serializer for ExerciseType model"""
    class Meta:
        model = ExerciseType
        fields = ['id', 'name']


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializer for Exercise model"""
    exercise_type = ExerciseTypeSerializer()

    class Meta:
        model = Exercise
        fields = ['id', 'name', 'exercise_type']


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = WorkoutExercise
        fields = ['id', 'exercise', 'reps', 'sets', 'weight']

    
class WorkoutSerializer(serializers.ModelSerializer):
    workout_exercises = WorkoutExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Workout
        fields = ['id', 'name', 'created_at', 'workout_exercises']


class WorkoutLogSerializer(serializers.ModelSerializer):
    workout_name = serializers.CharField(source='workout.name', read_only=True)

    class Meta:
        model = WorkoutLog
        fields = ['id', 'workout', 'workout_name', 'date']


class CycleSerializer(serializers.ModelSerializer):
    """Serializer for Cycle model"""
    class Meta:
        model = Cycle
        fields = ['id', 'start_date', 'cycle_length']


class CyclePhaseSerializer(serializers.ModelSerializer):
    """Serializer for CyclePhase model"""
    phase_name = serializers.CharField(source='phase.name', read_only=True)

    class Meta:
        model = CyclePhase
        fields = ['id', 'phase_name', 'start_date', 'end_date']


class CycleLogSerializer(serializers.ModelSerializer):
    """Serializer for CycleLog model"""
    cycle_phase = CyclePhaseSerializer(many=True, read_only=True)
    symptoms = serializers.StringRelatedField(many=True)

    class Meta:
        model = CycleLog
        fields = ['id', 'cycle_phase', 'date', 'symptoms']

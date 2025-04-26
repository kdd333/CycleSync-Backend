from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """Manager for custom user model"""

    def create_user(self, email, password=None, name=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model where email is the unique identifier"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    menstrual_length = models.PositiveIntegerField(default=5) 
    follicular_length = models.PositiveIntegerField(default=9)  
    ovulation_length = models.PositiveIntegerField(default=1) 
    luteal_length = models.PositiveIntegerField(default=13)  

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class ExerciseType(models.Model):
    """Model to represent the type of exercise (e.g., compound, isolation)"""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    

class Exercise(models.Model):
    """Model to represent an exercise"""
    name = models.CharField(max_length=255)
    exercise_type = models.ForeignKey(ExerciseType, on_delete=models.CASCADE, related_name='exercises')

    def __str__(self):
        return self.name


class Workout(models.Model):
    """Model to represent a workout created by a user"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  
        return f"{self.name} by {self.user.email}"


class WorkoutExercise(models.Model):
    """Model to represent an exercise within a workout"""
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Weight in kg or lbs

    def __str__(self):
        return f"{self.exercise.name} in {self.workout.name}"
    

class WorkoutLog(models.Model):
    """Model to log a workout for a specific date"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='workout_logs')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_logs')
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'date')  # Ensure a user can only log one workout per day

    def __str__(self):
        return f"Workout {self.workout.name} logged for {self.date} by {self.user.email}"
    

class Cycle(models.Model):
    """Model to represent a full menstrual cycle"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cycles')
    start_date = models.DateField()
    cycle_length = models.PositiveIntegerField(default=28)  # Length of the cycle in days

    def __str__(self): 
        return f"Cycle for {self.user.email} from {self.start_date} for {self.cycle_length} days"
    

class Phase(models.Model):
    """Model to represent a menstrual phase"""
    name = models.CharField(max_length=255)  # e.g., Follicular, Ovulatory, Luteal

    def __str__(self):
        return self.name
    

class CyclePhase(models.Model):
    """Model to represent a phase within a menstrual cycle"""
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='phases')
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='cycle_phases', null =True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.phase.name if self.phase else 'No Phase'} phase for {self.cycle.user.email} from {self.start_date} to {self.end_date}"


class Symptom(models.Model):
    """Model to represent a symptom experienced during a cycle phase"""
    symptom_name = models.CharField(max_length=255)  # e.g., Cramps, Mood Swings

    def __str__(self):
        return f"{self.symptom_name}"


class CycleLog(models.Model):
    """Model to log symptoms or notes during a specific phase of the cycle"""
    cycle_phase = models.ForeignKey(CyclePhase, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    symptoms = models.ManyToManyField(Symptom, blank=True, related_name='cycle_logs', through='CycleLogSymptom')  # Symptoms experienced

    def __str__(self):
        return f"Log for {self.cycle_phase.phase.name} phase on {self.date} for {self.cycle_phase.cycle.user.email}"
    

class CycleLogSymptom(models.Model):
    """Through model to associate symptoms with cycle logs"""
    cycle_log = models.ForeignKey(CycleLog, on_delete=models.CASCADE, related_name='cycle_log_symptoms')
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE, related_name='cycle_log_symptoms')

    def __str__(self):
        return f"{self.symptom.symptom_name} in log for {self.cycle_log.cycle_phase.phase_name} phase on {self.cycle_log.date}"
    
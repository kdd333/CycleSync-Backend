from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .models import Workout, Exercise, WorkoutExercise, WorkoutLog, Phase, Cycle, CyclePhase, CycleLog, CycleLogSymptom, Symptom
from .serializers import WorkoutSerializer, ExerciseSerializer, WorkoutLogSerializer, CycleSerializer, CyclePhaseSerializer, CycleLogSerializer
from datetime import date as Date, timedelta

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=email, password=password, name=name)
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        print(f"Email: {email}, Password: {password}")

        user = authenticate(email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        """Logout user by blacklisting the refresh token"""
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
       

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        """fetch logged in users details"""
        user = request.user
        user_data = {
            "email": user.email,
            "name": user.name,
            "menstrual_length": user.menstrual_length,
            "follicular_length": user.follicular_length,
            "ovulation_length": user.ovulation_length,
            "luteal_length": user.luteal_length,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
        }
        return Response(user_data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """update logged in users details"""
        user = request.user
        name = request.data.get('name')
        email = request.data.get('email')
        menstrual_length = request.data.get('menstrual_length')
        follicular_length = request.data.get('follicular_length')
        ovulation_length = request.data.get('ovulation_length')
        luteal_length = request.data.get('luteal_length')
        
        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user.name = name if name else user.name
        user.email = email if email else user.email
        user.menstrual_length = menstrual_length if menstrual_length else user.menstrual_length
        user.follicular_length = follicular_length if follicular_length else user.follicular_length
        user.ovulation_length = ovulation_length if ovulation_length else user.ovulation_length
        user.luteal_length = luteal_length if luteal_length else user.luteal_length
        user.save()

        # Update users current cycle phases and cycle length if there is a current cycle 
        today = Date.today()
        current_cycle = Cycle.objects.filter(user=user, start_date__lte=today).order_by('-start_date').first()

        if current_cycle:
            # Recalculate the phases for the current cycle
            phases = [
                ("Menstrual", user.menstrual_length),
                ("Follicular", user.follicular_length),
                ("Ovulatory", user.ovulation_length),
                ("Luteal", user.luteal_length),
            ]

            start_date = current_cycle.start_date
            total_cycle_length = 0

            for phase_name, length in phases:
                phase = current_cycle.phases.filter(phase__name=phase_name).first()
                if phase:
                    phase.start_date = start_date
                    phase.end_date = start_date + timedelta(days=length - 1)
                    phase.save()
                    total_cycle_length += length
                    start_date = phase.end_date + timedelta(days=1)
            
            # Update the cycle length
            current_cycle.cycle_length = total_cycle_length
            current_cycle.save()
        
        return Response({"message": "User details updated successfully"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


class ExerciseListView(ListAPIView):
    """API endpoint to retrieve a list of exercises."""
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated] 


class WorkoutListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all workouts for the authenticated user"""
        workouts = Workout.objects.filter(user=request.user)
        serializer = WorkoutSerializer(workouts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new workout for the authenticated user"""
        data = request.data
        workout_name = data.get('name')
        exercises = data.get('exercises', [])
        
        if not workout_name:
            return Response({"error": "Workout name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        workout = Workout.objects.create(user=request.user, name=workout_name)

        for exercise_data in exercises:
            exercise = Exercise.objects.get(id=exercise_data['id'])
            WorkoutExercise.objects.create(
                workout=workout,
                exercise=exercise,
                reps=exercise_data['reps'],
                sets=exercise_data['sets'],
                weight=exercise_data['weight'],
            )

        return Response({"message": "Workout created successfully"}, status=status.HTTP_201_CREATED)
    

class WorkoutDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workout_id):
        """Retrieve a specific workout for the authenticated user"""
        try:
            workout = Workout.objects.get(id=workout_id, user=request.user)
            serializer = WorkoutSerializer(workout)
            workout_data = serializer.data
            print(workout_data)  # Debugging line to check the serialized data

            # Get current cycle and phase
            today = Date.today()
            current_cycle = Cycle.objects.filter(user=request.user, start_date__lte=today).order_by('-start_date').first()
            current_phase = None

            if current_cycle:
                for phase in current_cycle.phases.all():
                    if phase.start_date <= today <= phase.end_date:
                        current_phase = phase.phase.name
                        break

            # Add warning message for compound exercises during menstrual or luteal phases
            for exercise in workout_data['workout_exercises']:
                exercise_obj = Exercise.objects.get(id=exercise['exercise']['id'])
                if exercise_obj.exercise_type.name == "Compound" and current_phase in ["Menstrual", "Luteal"]:
                    exercise['warning'] = f"'{exercise_obj.name}' is a compound exercise which may be more challenging during this phase. A lowered weight or fewer sets is recommended. Listen to your body."
                else:
                    exercise['warning'] = ""

            return Response(workout_data, status=status.HTTP_200_OK)
        except Workout.DoesNotExist:
            return Response({"error": "Workout not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, workout_id):
        """Update a specific workout for the authenticated user"""
        try:
            workout = Workout.objects.get(id=workout_id, user=request.user)
            data = request.data
            print(f"Updating workout with ID {workout_id} with data: {data}")  # Debugging line
            workout.name = data.get('name', workout.name)
            workout.save()

            # Update workout exercises
            exercises = data.get('workout_exercises', [])
            workout.workout_exercises.all().delete()  # Clear existing exercises

            for exercise in exercises:
                print(f"Exercise data: {exercise}")
                exerciseObject = Exercise.objects.get(id=exercise['exerciseId'])
                print("exercise object:", exerciseObject)
                WorkoutExercise.objects.create(
                    workout=workout,
                    exercise=exerciseObject,
                    reps=exercise['reps'],
                    sets=exercise['sets'],
                    weight=exercise['weight'],
                )

            return Response({"message": "Workout updated successfully"}, status=status.HTTP_200_OK)
        except Workout.DoesNotExist:
            return Response({"error": "Workout not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exercise.DoesNotExist:
            return Response({"error": "One or more exercises not found"}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, workout_id):
        """Delete a specific workout for the authenticated user"""
        try:
            workout = Workout.objects.get(id=workout_id, user=request.user)
            workout.delete()
            return Response({"message": "Workout deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Workout.DoesNotExist:
            return Response({"error": "Workout not found"}, status=status.HTTP_404_NOT_FOUND)
        

class WorkoutLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all workout logs for the authenticated user"""
        workout_logs = WorkoutLog.objects.filter(user=request.user)
        serializer = WorkoutLogSerializer(workout_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Log a workout for a specific date"""
        data = request.data
        workout_id = data.get('workout')
        date = data.get('date')

        if not workout_id or not date:
            return Response({"error": "Workout ID and date are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            workout = Workout.objects.get(id=workout_id, user=request.user)
            log, created = WorkoutLog.objects.update_or_create(
                user=request.user,
                date=date,
                defaults={'workout': workout}
            )
            serializer = WorkoutLogSerializer(log)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Workout.DoesNotExist:
            return Response({"error": "Workout not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request):
        """Delete a specific workout log for the authenticated user"""
        date = request.data.get('date')
        if not date:
            return Response({"error": "Date is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            log = WorkoutLog.objects.get(user=request.user, date=date)
            log.delete()
            return Response({"message": "Workout log deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except WorkoutLog.DoesNotExist:
            return Response({"error": "Workout log not found"}, status=status.HTTP_404_NOT_FOUND)


class PeriodDatesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all period dates for the user"""
        try:
            logs = CycleLog.objects.filter(cycle_phase__cycle__user=request.user, cycle_phase__phase__name="Menstrual")
            dates = logs.values_list('date', flat=True)
            return Response({"period_dates": dates}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class LogPeriodView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, date):
        """Log a period for the authenticated user"""
        user = request.user
        date_str = date
        
        if not date_str:
            return Response({"error": "Date is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convert date string to a datetime.date object
            date_obj = Date.fromisoformat(date_str)
        except ValueError:
            return Response({"error": "Invalid date format. use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        
        # check if the user has an existing cycle that includes this date
        current_cycle = Cycle.objects.filter(user=user, start_date__lte=date_obj).order_by('-start_date').first()

        if current_cycle and date_obj <= current_cycle.start_date + timedelta(days=current_cycle.cycle_length - 1):
            # Existing cycle: Create a CycleLog for the Menstrual Phase
            menstrual_phase = current_cycle.phases.filter(phase__name='Menstrual').first()
            if not menstrual_phase:
                return Response({"error": "No Menstrual phase found for the current cycle"}, status=status.HTTP_400_BAD_REQUEST)
            
            CycleLog.objects.create(cycle_phase=menstrual_phase, date=date_obj)
            return Response({"message": "Period logged successfully"}, status=status.HTTP_201_CREATED)
        
        # No existing cycle: Create a new cycle and cyclephases
        cycle = Cycle.objects.create(user=user, start_date = date_obj)

        # set the cycle length based on the user cycle length variables
        menstrual_length = user.menstrual_length
        follicular_length = user.follicular_length
        ovulation_length = user.ovulation_length
        luteal_length = user.luteal_length

        phases = [
            ("Menstrual", menstrual_length),
            ("Follicular", follicular_length),
            ("Ovulatory", ovulation_length),
            ("Luteal", luteal_length),
        ]   

        start_date = date_obj
        for phase_name, length in phases:
            end_date = start_date + timedelta(days=length - 1)
            phase = Phase.objects.get(name=phase_name)
            CyclePhase.objects.create(cycle=cycle, phase=phase, start_date=start_date, end_date=end_date)
            start_date = end_date + timedelta(days=1)
    
        # Create a CycleLog for the Menstrual Phase
        menstrual_phase = cycle.phases.filter(phase__name='Menstrual').first()
        CycleLog.objects.create(cycle_phase=menstrual_phase, date=date_obj)

        return Response({"message": "New cycle created and period logged successfully"}, status=status.HTTP_201_CREATED)

    def delete(self, request, date):
        """Delete a period log for the user"""
        user = request.user
        date_str = date

        if not date_str:
            return Response({"error": "Date is required"}, status.HTTP_400_BAD_REQUEST)
        
        try:
            # Convert date string to a datetime.date object
            date_obj = Date.fromisoformat(date_str)
        except ValueError:
            return Response({"error": "Invalid date format. use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Now Attempting to delete period log for date: {date_obj}")

        try:
            # Find the CycleLog for the given date and delete it
            log = CycleLog.objects.get(cycle_phase__cycle__user=user, date=date_obj)
            cycle = log.cycle_phase.cycle

            print(f"CycleLog found for date: {date_obj}")
            
            if cycle.start_date == date_obj:
                # If CycleLog's date matches start date of the cycle, delete Cycle & associated CyclePhases
                cycle.delete()
                return Response({"message": "Cycle and period log deleted successfully"}, status=status.HTTP_200_OK)
            else:
                # If it's not the start date, just delete the CycleLog
                print(f"Deleting CycleLog for date: {date_obj}")
                log.delete()
                print(f"Successfully Deleted CycleLog for date: {date_obj}")
                return Response({"message": "Period log deleted successfully"}, status=status.HTTP_200_OK)
        except CycleLog.DoesNotExist:
            return Response({"error": "Period log not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Unexpected error while deleting period log: {e}")
            return Response({"error": "An unexpected error occurred while deleting the period log."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CurrentCycleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get the current cycle, phase, cycle day, and daily message for the user"""
        user = request.user
        today = Date.today()

        # Get latest cycle for the user
        current_cycle = Cycle.objects.filter(user=user, start_date__lte=today).order_by('-start_date').first()

        if not current_cycle:
            # No cycle found for current date - user not logged their period yet
            return Response({
                "current_phase": "", 
                "cycle_day": "",
                "cycle_length": "",
                "daily_message": "Period Not Logged. Log your last period in the calendar section to start tracking your cycle."
            }, status=status.HTTP_200_OK)
        
        # Get cycle length
        cycle_length = current_cycle.cycle_length
        print(f"Cycle Length: {cycle_length}")

        # Calculate cycle day
        cycle_day = (today - current_cycle.start_date).days + 1
        if cycle_day > cycle_length:
            # If current date is beyond cycle length, return empty values 
            return Response({
                "current_phase": "",
                "cycle_day": "",
                "cycle_length": "",
                "daily_message": "Cycle has ended. Log your next period to start a new cycle or edit your cycle phase lengths under your profile."
            }, status=status.HTTP_200_OK)
        
        # Determine the current cycle phase
        current_phase = ""
        daily_message = ""

        phases = current_cycle.phases.all()
        for phase in phases:
            if phase.start_date <= today <= phase.end_date:
                current_phase = phase.phase.name
                break

        # Set daily message based on current phase
        if current_phase == "Menstrual":
            daily_message = "It's your period! Rest and take care of yourself. Prioritise this time to recover. Light yoga or stretching is recommended."
        elif current_phase == "Follicular":
            daily_message = "Time to build and grow! Focus on strength training and cardio. You're in the mood to get things done!"
        elif current_phase == "Ovulatory":
            daily_message = "You're at your peak! Focus on high-intensity workouts and try pushing your limits. Body temperature is at its highest. You may feel hotter than usual."
        elif current_phase == "Luteal":
            daily_message = "Time to wind down. Focus on low-intensity workouts and yoga. You may feel more tired than usual. Rest and recovery are key."
        
        return Response({
            "current_phase": current_phase, 
            "cycle_day": cycle_day,
            "daily_message": daily_message,
            "cycle_length": cycle_length
        }, status=status.HTTP_200_OK)


class CycleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all cycles for the user"""
        cycles = Cycle.objects.filter(user=request.user).order_by('-start_date')  # order by the most recent cycles
        serializer = CycleSerializer(cycles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CyclePhaseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cycle_id):
        """Retrieve all phases for a specific cycle"""
        try:
            cycle = Cycle.objects.get(id=cycle_id, user=request.user)
            phases = CyclePhase.objects.filter(cycle=cycle).order_by('start_date')
            serializer = CyclePhaseSerializer(phases, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cycle.DoesNotExist:
            return Response({"error": "Cycle not found"}, status=status.HTTP_404_NOT_FOUND)
        

        

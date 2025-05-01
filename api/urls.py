from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, ChangePasswordView, LogoutView, WorkoutListCreateView, ExerciseListView, WorkoutDetailView, WorkoutLogView, CycleListView, PeriodDatesView, LogPeriodView, CurrentCycleView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserDetailView.as_view(), name='user_detail'), 
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('workouts/', WorkoutListCreateView.as_view(), name='workouts'),
    path('workouts/<int:workout_id>/', WorkoutDetailView.as_view(), name='workout_detail'),
    path('exercises/', ExerciseListView.as_view(), name='exercises'),
    path('workout-logs/', WorkoutLogView.as_view(), name='workout_logs'),
    path('cycles/', CycleListView.as_view(), name='cycles'),
    path('log-period/<str:date>/', LogPeriodView.as_view(), name='log_period'),
    path('period-dates/', PeriodDatesView.as_view(), name='period_dates'),
    path('cycle-data/', CurrentCycleView.as_view(), name='cycle_data'),  
]
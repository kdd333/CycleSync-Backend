from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ExerciseType, Exercise, Workout, WorkoutExercise, WorkoutLog, Phase, CyclePhase, Cycle, CycleLog, CycleLogSymptom, Symptom


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("name","email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("name","email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    search_fields = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'exercise_type')


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'created_at')


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'workout', 'exercise', 'reps', 'sets', 'weight')


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_date', 'cycle_length')


@admin.register(CyclePhase)
class CyclePhaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'cycle', 'phase', 'start_date', 'end_date')


@admin.register(CycleLog)
class CycleLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'cycle_phase', 'date', 'get_symptoms')

    def get_symptoms(self, obj):
        return ", ".join([symptom.symptom_name for symptom in obj.symptoms.all()])
    get_symptoms.short_description = 'Symptoms'


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('id', 'symptom_name')


@admin.register(CycleLogSymptom)
class CycleLogSymptomAdmin(admin.ModelAdmin):
    list_display = ('id', 'cycle_log', 'symptom')

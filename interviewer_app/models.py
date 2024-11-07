from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    maiden_name = models.CharField(max_length=255, blank=True, null=True)
    previous_name = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.CharField(max_length=255, blank=True, null=True)
    birth_place = models.CharField(max_length=255, blank=True, null=True)
    grew_up_in = models.CharField(max_length=255, blank=True, null=True)
    insights = models.TextField(blank=True, null=True)

    def get_profile_text(self):
        """Combine all fields into a single text for embedding."""
        fields = [
            self.full_name,
            self.maiden_name,
            self.previous_name,
            self.birth_place,
            self.grew_up_in,
            self.insights,
        ]
        return " ".join([str(field) for field in fields if field])


class InterviewSession(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="interview_sessions"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    current_question = models.PositiveIntegerField(
        default=1
    )  # Tracks the current question in the session
    story_text = models.TextField(
        blank=True, null=True
    )  # Optional field to store session-specific story text or notes

    def __str__(self):
        return f"Session for {self.user.username} - Status: {self.status}"

    def complete_session(self):
        """Mark the session as completed and set the end time."""
        self.status = "completed"
        self.end_time = models.DateTimeField(auto_now=True)
        self.save()

    def pause_session(self):
        """Pause the session."""
        self.status = "paused"
        self.save()

    def resume_session(self):
        """Resume a paused session."""
        self.status = "active"
        self.save()

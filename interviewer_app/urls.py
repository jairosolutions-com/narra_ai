from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("intake/<int:question_id>/", views.intake_questions, name="intake_questions"),
    path("hook_story/", views.hook_story, name="hook_story"),
    path("next_questions/", views.next_questions, name="next_questions"),
    path("voice-command/", views.voice_command, name="voice_command"),
    path("chat/", views.chat_page, name="chat_page"),
    path("response/", views.assistant_response, name="assistant_response"),
    path(
        "response/stream/",
        views.assistant_response_stream,
        name="assistant_response_stream",
    ),
]

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import UserProfile, InterviewSession
from .questions import INTAKE_QUESTIONS
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import os
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .utils import get_similar_response

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
assistant = pc.assistant.Assistant(assistant_name="narra")  # Name your assistant


def welcome(request):
    """Landing page with welcome and context setting."""
    return render(request, "interviewer_app/welcome.html")


@login_required
def intake_questions(request, question_id):
    """Handle intake questions one by one."""
    # Retrieve the current question data
    question_data = next((q for q in INTAKE_QUESTIONS if q["id"] == question_id), None)
    if not question_data:
        # Redirect to the next step if no matching question is found
        return redirect("hook_story")

    # Get or create UserProfile for the current user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        answer = request.POST.get("answer")
        if answer:
            # Save the answer to the appropriate field in UserProfile
            setattr(user_profile, question_data["field"], answer)
            user_profile.save()

            # Redirect to the next question
            next_question_id = question_id + 1
            return redirect("intake_questions", question_id=next_question_id)

    return render(
        request, "interviewer_app/intake_questions.html", {"question": question_data}
    )


@csrf_exempt
def next_questions(request):
    """Placeholder for the next set of interview questions."""
    return render(request, "interviewer_app/next_questions.html")


def hook_story(request):
    """Prompt the Storyteller to share a favorite story."""
    if request.method == "POST":
        initial_story = request.POST.get("story")

        # Generate follow-up questions based on the initial story
        follow_up_questions = get_similar_response(
            initial_story
        )  # Adjust this function as needed

        # Save initial story to the session for tracking purposes
        session, created = InterviewSession.objects.get_or_create(user=request.user)
        session.story_text = initial_story
        session.save()

        return render(
            request,
            "interviewer_app/follow_ups.html",
            {"story": initial_story, "follow_up_questions": follow_up_questions},
        )

    # First time displaying the hook question
    prompt = "Let’s start with a story that you enjoy sharing. Can you tell a favorite anecdote, one that you often find yourself telling and that your loved ones will expect to see in your memoir?"
    return render(request, "interviewer_app/hook_story.html", {"prompt": prompt})


@csrf_exempt
def voice_command(request):
    """Process voice commands and return the assistant's response."""
    if request.method == "POST":
        user_input = request.POST.get("user_input")

        # Get the most similar response from Pinecone
        bot_response = get_similar_response(user_input)

        return JsonResponse({"response": bot_response})

    return JsonResponse({"response": "No input received."})


@csrf_exempt
def assistant_response(request):
    """Process text-based input and return a response from the assistant."""
    if request.method == "POST":
        user_input = request.POST.get("user_input", "")

        # Debugging: Print the user input
        print("User input:", user_input)

        # Create a message for the assistant
        msg = Message(content=user_input)

        try:
            # Get a response from the assistant
            response = assistant.chat_completions(messages=[msg])

            # Debugging: Print the full response object
            print("Full assistant response object:", response)
            print("Response content:", response.content if response else "No content")

            # Check if response content is available
            if response and hasattr(response, "content") and response.content:
                return JsonResponse({"response": response.content})
            else:
                return JsonResponse({"response": "I'm sorry, I couldn't process that."})
        except Exception as e:
            # Print error in server log for troubleshooting
            print("Error:", e)
            return JsonResponse({"error": "Could not process request"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def assistant_response_stream(request):
    """Stream the assistant's response in chunks."""
    if request.method == "POST":
        user_input = request.POST.get("user_input", "")

        # Create a message for the assistant
        msg = Message(content=user_input)

        try:
            # Stream the response in chunks
            chunks = assistant.chat_completions(
                messages=[msg], stream=True, model="gpt-4o"
            )
            response_text = "".join(chunk.content for chunk in chunks if chunk)
            return JsonResponse({"response": response_text})
        except Exception as e:
            # Print error in server log for troubleshooting
            print("Error:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def chat_page(request):
    """Render the chat page."""
    return render(request, "interviewer_app/chat_with_narra.html")

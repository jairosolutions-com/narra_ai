import openai
from django.conf import settings
from django.http import JsonResponse

openai.api_key = settings.OPENAI_API_KEY  # Ensure you add this in settings.py


def analyze_storyteller_background(user_profile):
    # Format the profile information into a prompt for OpenAI
    prompt = f"""
    Here is some basic background information about a person. 
    Name: {user_profile.full_name}
    Maiden Name: {user_profile.maiden_name or "N/A"}
    Previous Name: {user_profile.previous_name or "N/A"}
    Birthday: {user_profile.birthday}
    Birth Place: {user_profile.birth_place}
    Grew Up In: {user_profile.grew_up_in}

    Analyze this information and provide insights into their generational story. 
    Include possible historical or cultural contexts based on their birth location and era. Suggest life themes, such as family traditions, cultural background, and how these may influence their life story.
    """

    # Call OpenAI API
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        insights = response.choices[0].text.strip()
    except Exception as e:
        insights = f"Error generating insights: {str(e)}"

    return insights


def get_story_follow_up(story_text):
    prompt = f"""
    Here is a story shared by a user: "{story_text}"

    Identify up to 3 meaningful follow-up questions that will help the user expand on their story. 
    Ask questions that encourage sensory details, emotions, or additional context. Avoid questions that could lead to yes/no answers.
    """

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            n=1,
        )
        follow_up_questions = response.choices[0].text.strip().split("\n")
    except Exception as e:
        follow_up_questions = [f"Error generating follow-up questions: {str(e)}"]

    return follow_up_questions


def process_voice_command(user_input):
    """Process the voice command using OpenAI API and return a response."""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Respond to the following in a friendly, engaging tone: {user_input}",
            max_tokens=50,
        )
        bot_response = response.choices[0].text.strip()
    except Exception as e:
        bot_response = "I'm sorry, I couldn't process your request."

    return bot_response

// static/js/voice_interaction.js

function startVoiceRecognition(inputElementId) {
    const inputElement = document.getElementById(inputElementId);

    // Check for browser compatibility with Web Speech API
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        alert("This browser does not support voice recognition.");
        return;
    }

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        inputElement.placeholder = "Listening...";
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        inputElement.value = transcript;  // Set the transcribed text as the input field's value

        // Send the transcribed text to the backend
        sendUserMessage(transcript);
    };

    recognition.onerror = function(event) {
        inputElement.placeholder = 'Error: ' + event.error;
    };

    recognition.start();
}

function sendUserMessage(userInput) {
    const csrfToken = getCsrfToken();
    const responseElement = document.getElementById('response');

    fetch('/assistant/response/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `user_input=${encodeURIComponent(userInput)}`
    })
    .then(response => response.json())
    .then(data => {
        // Display the assistant's response
        responseElement.innerHTML = data.response;
    })
    .catch(error => {
        console.error("Error:", error);
        responseElement.innerHTML = 'Error retrieving response';
    });
}

function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return '';
}

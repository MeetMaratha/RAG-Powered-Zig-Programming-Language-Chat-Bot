const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Replace with your actual API Gateway endpoint URLs
const SEND_API_URL = 'https://znoiwpxq33.execute-api.us-east-1.amazonaws.com/prod/send-query-function';
const RESULTS_API_URL = 'https://znoiwpxq33.execute-api.us-east-1.amazonaws.com/prod/get-result-function';

function addMessage(message, isUser) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message');
  messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
  
  // Check if message is an array and join with new lines
  if (Array.isArray(message)) {
      messageDiv.innerHTML = message.join('<br>');
  } else {
      messageDiv.textContent = message;
  }
  
  chatBox.appendChild(messageDiv);
  
  // Scroll to bottom with smooth behavior
  chatBox.scrollTo({
      top: chatBox.scrollHeight,
      behavior: 'smooth'
  });
}

function addStatusMessage(message, isSuccess) {
  const statusDiv = document.createElement('div');
  statusDiv.classList.add('status-message');
  statusDiv.classList.add(isSuccess ? 'success' : 'error');
  statusDiv.textContent = message;
  chatBox.appendChild(statusDiv);
  
  chatBox.scrollTo({
      top: chatBox.scrollHeight,
      behavior: 'smooth'
  });
  
  return statusDiv;
}

function addTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.classList.add('typing-indicator');
  typingDiv.id = 'typing-indicator';
  
  // Create three dots
  for (let i = 0; i < 3; i++) {
      const dot = document.createElement('div');
      dot.classList.add('typing-dot');
      typingDiv.appendChild(dot);
  }
  
  chatBox.appendChild(typingDiv);
  
  // Scroll to bottom
  chatBox.scrollTo({
      top: chatBox.scrollHeight,
      behavior: 'smooth'
  });
  
  return typingDiv;
}

function removeTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
      typingIndicator.remove();
  }
}

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0,
          v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
  });
}

async function getResultFromDynamoDB(uuid) {
  try {
      const response = await fetch(`${RESULTS_API_URL}?uuid=${uuid}`, {
          method: 'GET',
          headers: {
              'Content-Type': 'application/json'
          }
      });

      if (!response.ok) {
          throw new Error(`Failed to get result: ${response.status}`);
      }

      const data = await response.json();
      return data.result;
  } catch (error) {
      console.error('Error fetching result:', error);
      return `Error: ${error.message}`;
  }
}

async function pollForResult(uuid) {
  const maxAttempts = 60; // 60 attempts * 2.5 seconds = 150 seconds (2.5 minutes)
  let attempts = 0;
  
  return new Promise((resolve, reject) => {
      const pollInterval = setInterval(async () => {
          attempts++;
          const result = await getResultFromDynamoDB(uuid);
          
          if (result && result !== 'Processing') {
              clearInterval(pollInterval);
              resolve(result);
          } else if (attempts >= maxAttempts) {
              clearInterval(pollInterval);
              reject(new Error('Result not available after 2.5 minutes'));
          }
      }, 4000); // Check every 2.5 seconds
  });
}

async function handleUserMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  // Add user message
  addMessage(message, true);

  // Disable input and button during processing
  userInput.value = '';
  userInput.disabled = true;
  sendButton.disabled = true;

  // Add typing indicator
  const typingIndicator = addTypingIndicator();

  // Generate unique ID for the message
  const messageId = generateUUID();

  try {
      // Send request to API Gateway
      const sendResponse = await fetch(SEND_API_URL, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              query: message,
              uuid: messageId
          })
      });

      if (!sendResponse.ok) {
          throw new Error(`API request failed with status ${sendResponse.status}`);
      }

      // Show processing status
      addStatusMessage(`Processing your request (ID: ${messageId})`, true);
      
      // Poll for result
      const result = await pollForResult(messageId);
      
      // Remove typing indicator
      removeTypingIndicator();
      
      // Add bot response with the actual result
      addMessage(result, false);

  } catch (error) {
      console.error('Error:', error);
      removeTypingIndicator();
      addStatusMessage(`Error: ${error.message}`, false);
      addMessage("Sorry, I couldn't process your request. Please try again.", false);
  } finally {
      // Re-enable input and button
      userInput.disabled = false;
      sendButton.disabled = false;
      userInput.focus();
  }
}

// Event listeners
sendButton.addEventListener('click', handleUserMessage);
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleUserMessage();
  }
});

// Initial focus on input
userInput.focus();


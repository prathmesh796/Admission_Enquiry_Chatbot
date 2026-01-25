# Chatbot Configuration

# Response Mode Options:
# 'hybrid' - Use Gemini for low confidence queries, traditional for high confidence
# 'gemini_all' - Use Gemini for all queries (slower but more natural)
# 'traditional' - Use only traditional neural network responses (faster)
RESPONSE_MODE = 'hybrid'

# Confidence threshold for using Gemini (only used in hybrid mode)
# If neural network confidence is below this, Gemini will be used
CONFIDENCE_THRESHOLD = 0.7

# Enable/Disable Gemini features
USE_GEMINI = True

# Gemini Model Configuration
GEMINI_MODEL = 'gemini-3-flash-preview'

# Response settings
MAX_RESPONSE_LENGTH = 500  # Maximum characters in response
INCLUDE_HTML_FORMATTING = True  # Allow HTML tags in responses

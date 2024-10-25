chat_history = [
    {
        "role": "user",
        "parts": [
            "Given a post title and post text.\n"
            "You need to answer the comment. Answer should be compact.\n"
            "DON'T USE LISTS, TABLES, ETC.\n\n"
            "Post Title: How to learn python"
            "\nPost Text: You can use books specialized on python, there a lot of websites for this purposes"
            "\n\n"
            "Comment: Can you provide me specific websites where I can learn python",
        ],
    },
    {
        "role": "model",
        "parts": [
            "Sure! Check out websites like Codecademy, freeCodeCamp, and W3Schools. They offer interactive tutorials and exercises to help you learn Python. \n",
        ],
    },
]

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 250,
  "response_mime_type": "text/plain",
}



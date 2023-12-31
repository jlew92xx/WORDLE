import openai


openai.api_key_path = "/home/jlew92/Repos/WORDLE/myKey.txt"

def giveResponse(prompt):
    messages = [{"role" : "system", "content" : prompt}]
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages= messages
    )
    return response['choices'][0]['message']["content"]


import openai


openai.api_key_path = "myKey.txt"


def giveResponse(prompt, error):
    try:
        messages = [{"role": "system", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response['choices'][0]['message']["content"]
    except:
        print("AI failure!")
        return "AI FAILURE: " + error




if __name__ == '__main__':
    
    ps = giveResponse("Write a postscript for a guy named Jack who threatened to end your bloodline include the P.S.", "P.S it will be me who ends your bloodline")
    print("ps to jack:", ps)
      

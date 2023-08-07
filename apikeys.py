def get_api_keys():
    try:
        with open('keys.txt', 'r') as file:
            lines = file.readlines()
            bot_token = lines[0].split('=')[1].strip()
            return bot_token
    except FileNotFoundError:
        with open('keys.txt', 'w') as file:
            bot_token = input("Please enter your API Token: ")
            file.write(f"BOTTOKEN={bot_token}\n")
        return bot_token
    except Exception as e:
        print("Error reading API keys:", e)
        return None
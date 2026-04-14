from core.broker import generate_session

request_token = input("Enter request token: ")

access_token = generate_session(request_token)

print("\nCopy this token into settings.py")
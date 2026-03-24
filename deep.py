from src import api as ap
import sys

text = ""
msgId = None
thinking = False
search = False

if __name__ == "__main__":
    api = ap.connection()

    print("DEEPSEEK CLI")
    print("/help")
    status = api.islogged()
    if(not status):
        print("You are not logged, type: /login")

    print(f"Thinking mode: {thinking}\nSearch mode: {search}")

    api.newChat()
    while text != "/exit":
        try:
            text = str(input('> '))

            if(text == '/help'):
                print("/login \t\t\temail and password\n/newchat\n/thinking \t\ttrue/false\n/search \t\ttrue/false")
                

            elif(text == "/login"):
                email = str(input("Email -> "))
                password = str(input("Password -> "))
                
                status = api.login(email=email, password=password)
                del email, password

                if(not status):
                    print("Error to login try again")
                else: 
                    print("Logged!")
                    api.newChat()
            
            elif(text.startswith("/thinking")):
                try:
                    mode = text.split(" ")[1]
                except IndexError:
                    print("Invalid command")
                    continue

                match(mode.lower()):
                    case "true":
                        thinking = True
                        
                    case "false":
                        thinking = False
                print(f"Thinking mode: {thinking}")
                
            elif(text.startswith("/search")):
                try:
                    mode = text.split(" ")[1]
                except IndexError:
                    print("Invalid command")
                    continue

                match(mode.lower()):
                    case "true":
                        search = True
                        
                    case "false":
                        search = False
                    
                print(f"Search mode: {search}")
                
            
            elif(text == "/newchat" and status):
                api.newChat()
                msgId = None
                print('\033[2J')
                print("/help")
                
            else:
                if(status):
                    print(api.send(text,msgId,thinking=thinking, search=search))
                    if(msgId is None):
                        msgId = 2
                        continue
                    msgId += 2

        except KeyboardInterrupt:
            sys.exit(0)

        

    

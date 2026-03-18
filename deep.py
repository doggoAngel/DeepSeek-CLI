from api import connection
import sys


if __name__ == "__main__":
    api = connection()

    print("DEEPSEEK CLI")
    print("/help")
    status = api.islogged()
    if(not status):
        print("You are not logged, type: /login")
    text = ""
    msgId = None
    api.newChat()
    while text != "/exit":
        try:
            text = str(input('> '))

            if(text == '/help'):
                print("/login -> email and password\n/newchat\n/history")
                

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
                
            
            elif(text == "/newchat"):
                api.newChat()
                msgId = None
                

            elif(text == "/history"):
                api.getHistory(api.idChat)
                
            else:
                print(api.send(text,msgId))
                if(msgId is None):
                    msgId = 2
                    continue
                msgId += 2

        except KeyboardInterrupt:
            sys.exit(0)

        

    

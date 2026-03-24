import requests
import json
from .crack import antibot
import base64

class connection:
    def __init__(self, ):
        
        self.token = ""
        self.domain = "https://chat.deepseek.com"
        self.endpoints = {
            "login":"/api/v0/users/login",
            "challenge":"/api/v0/chat/create_pow_challenge",
            "newChat":"/api/v0/chat_session/create",
            "send":"/api/v0/chat/completion",
            "upload":"",
            "user":"/api/v0/users/current"
        }
        self.headers = {
            "X-Client-Timezone-Offset":"3600",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "X-Client-Version":"1.7.0",
            "X-Client-Platform":"web",
            "Content-Type":"application/json",
            "Origin":"https://chat.deepseek.com",
            "Accept-Encoding":"gzip, deflate, br"
        }

        self.idChat = ""


    #Login request
    def login(self, email:str, password:str) -> bool:
        if "Autorization" in self.headers:
            del self.headers["Autorization"]
        
    
        payload = {
            "email":email,
            "mobile":"",
            "password":password,
            "area_code":"",
            "device_id":"",
            "os":"web"
        }

        req = requests.post(url=self.domain + self.endpoints["login"], headers=self.headers, json=payload)
        
        if "token" not in req.text:
            return False

        del email
        del password

        self.token = json.loads(req.text)["data"]["biz_data"]["user"]["token"]
        self.headers["Authorization"] = "Bearer " + self.token
        with open(".setting", 'w') as f:
            f.write(self.token)
        return True

    #new chat
    def newChat(self):
        req = requests.post(url=self.domain+self.endpoints["newChat"], json={}, headers=self.headers)
        self.idChat = json.loads(req.text)["data"]["biz_data"]["id"]
    

    # check if is logged 
    def islogged(self) -> bool:
        try: 
            with open(".setting", 'r') as f:
                token = f.readline()
            if(token != ""):
                self.headers["Authorization"] = "Bearer " + token
                req = requests.get(url=self.domain + self.endpoints["user"], headers=self.headers)
                
                if("email" not in req.text):
                    return False
                return True
            else:
                return False
        except FileNotFoundError:
            return False

    

    #get challenge anti bot
    def challenge(self, target)-> str:
        
        payload = {
            "target_path":self.endpoints[target]
        }

        req = requests.post(url=self.domain + self.endpoints["challenge"], headers=self.headers,json=payload)

        data = json.loads(req.text)["data"]["biz_data"]["challenge"]
        
        antB = antibot(salt=data["salt"],expire=data["expire_at"],target=data["challenge"],difficult=data["difficulty"])
        pow = {
            "algorithm":data["algorithm"],
            "challenge":data["challenge"],
            "salt":data["salt"],
            "answer":antB.brute(),
            "signature":data["signature"],
            "target_path":self.endpoints[target]
        }
        pow_string = json.dumps(pow)
        return base64.b64encode(pow_string.encode("utf-8"))

    # exctract text from response
    def extractText(self, resp) -> str:

        complete_text = ""
        for line in resp.iter_lines():
            if not line or not line.startswith(b'data: '):
                continue
            
            data_json = line[6:].decode('utf-8')
            try:
                data = json.loads(data_json)
            except json.JSONDecodeError:
                continue

            if ('v' in data and isinstance(data['v'],str)) and not ('p' in data and 'v' in data and data['v'] == 'FINISHED'):
                complete_text += data['v']

            elif 'v' in data and isinstance(data['v'],dict) and 'response' in data['v']:
                r = data['v']['response']
                f = r.get('fragments', [])
                for x in f:
                    if x.get('type') == 'RESPONSE':
                        complete_text += x.get('content','')
        
        return complete_text
            
        

    # send msg into a chat ID
    def send(self, message:str, msgId,thinking:bool,search:bool) -> str:
        self.headers["X-Ds-Pow-Response"] = self.challenge("send")

        payload = {
            "chat_session_id":self.idChat,
            "parent_message_id":msgId,
            "prompt":message,
            "ref_file_ids":[],
            "thinking_enabled":thinking,
            "search_enabled":search,
            "preempt":False
        }

        resp = requests.post(url=self.domain + self.endpoints["send"], headers=self.headers, json=payload, stream=True)
        
        return self.extractText(resp)
        

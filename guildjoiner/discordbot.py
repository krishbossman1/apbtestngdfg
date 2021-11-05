from datetime import datetime
from discord.ext.commands import Bot,has_permissions
import requests,json,discord,asyncio

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID =  # Discord client ID.
CLIENT_SECRET = ""    # Discord client secret.
AUTH_HEADER_NAME = "ertyjkjhgfdsdfgddfgfdgnbvcx" #random name (required)
AUTH_HEADER_VALUE = "awesrdtfyguikjhgfvdsfdgvhfdfvgfdgsg" #random value (required)
TOKEN = "" #bot token
URL = "insert site url"
role_id = 0 # make a role called verified and paste the ID here
def fetch_data():
    headers = {AUTH_HEADER_NAME:AUTH_HEADER_VALUE}
    return requests.get(f"{URL}/users",headers=headers,verify=False).text
def refresh(refresh_token):
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
  return json.loads(r.text)["access_token"]
bot = Bot(command_prefix="!",help_command=None)
@bot.command()
@has_permissions(administrator=True)
async def join(ctx,id,count: int=None):
    global role_id
    with open("config.json",) as f:
        role_id = json.load(f)["role_id"]
    embed=discord.Embed(description=f"Adding members started...",color=0xFFFF00,timestamp=datetime.utcnow())
    embed.set_author(name="Fetching users",icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)
    joined = 0
    already = 0
    errors = 0
    data = json.loads(fetch_data())["data"]
    for user in data:
        for key in user:
            expires = user[key]["expires_at"]
            token = user[key]["access_token"]
            refresh_token = user[key]["refresh_token"]
            if datetime.fromtimestamp(expires)<datetime.now():
                token = refresh(refresh_token)
            headers = {
            "Authorization": f"Bot {TOKEN}",
            "Content-Type": "application/json"
            }
            data = {
                "access_token":token,
                "roles":[role_id]
            }
            r = requests.put(f"{API_ENDPOINT}/guilds/{id}/members/{int(key)}",headers=headers,json=data)
            remaining = r.headers['x-ratelimit-remaining']
            if remaining <=0:
                retry_after = float(r.headers['x-ratelimit-reset-after'])
                embed=discord.Embed(description=f"Bot on cooldown, will continue in {retry_after} seconds",color=0xFFFF00,timestamp=datetime.utcnow())
                embed.set_author(name="Ratelimited",icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                await asyncio.sleep(retry_after)
            if r.status_code == 201:
                joined+=1
            elif r.status_code == 204:
                already+= 1
            else:
                errors+=1
    embed=discord.Embed(description=f"Members added: {joined}\nMembers who were already joined: {already}\nErrors/Invalid users: {errors}",color=0x00FF00,timestamp=datetime.utcnow())
    embed.set_author(name="Finished!",icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)
bot.run(TOKEN)
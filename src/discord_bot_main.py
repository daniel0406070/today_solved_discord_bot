import discord
from discord.ext import tasks
import solveac_api
import datetime
import schedule
import time
from pytz import timezone
import json

token_path = "/home/daniel/coding/Python/discord_strg/Token.json"
with open(f"{token_path}","r") as f:
    tmp = json.load(f)

TOKEN = tmp["Token"]
CHANNEL_ID = '1147836035443736619'

imoji = {0:"<:lev_0:1147893192528764948>", 1:"<:lev_1:1147873556248674374>",	2:"<:lev_2:1147873557863481484>",	3:"<:lev_3:1147873560572997662>",	4:"<:lev_4:1147873562103914578>",	5:"<:lev_5:1147873565224476803>",	6:"<:lev_6:1147873568206631022>",	7:"<:lev_7:1147873569737543771>",	8:"<:lev_8:1147873572568715284>",	9:"<:lev_9:1147873574493896744>",	10:"<:lev_10:1147873577287295090>",	11:"<:lev_11:1147873579174744154>",	12:"<:lev_12:1147873582182047855>",	13:"<:lev_13:1147873584748953710>",	14:"<:lev_14:1147873587705954394>",	15:"<:lev_15:1147873589446582343>",	16:"<:lev_16:1147873592713945088>",	17:"<:lev_17:1147873719524536453>",	18:"<:lev_18:1147873595205373962>",	19:"<:lev_19:1147873598455947305>",	20:"<:lev_20:1147873722426982440>",	21:"<:lev_21:1147873602386018335>",	22:"<:lev_22:1147873605334601799>",	23:"<:lev_23:1147873724201189407>",	24:"<:lev_24:1147873727271415808>",	25:"<:lev_25:1147873609126248570>",	26:"<:lev_26:1147873729293062314>",	27:"<:lev_27:1147873615300284456>",	28:"<:lev_28:1147873616927658106>",	29:"<:lev_29:1147873619846905927>",	30:"<:lev_30:1147873732250046515>", 31:"<:lev_31:1147903912175751238>"}


intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot()

@bot.event # 시작시 실행
async def on_ready():
    print("Bot is ready")
    day_fn.start()


day_time_min= datetime.time(hour=6, minute=0, tzinfo=timezone("Asia/Seoul"))
day_time_max= datetime.time(hour=6, minute=7, tzinfo=timezone("Asia/Seoul"))

@tasks.loop(minutes=5) # 매일 6시 0분 5초에 푼 문제 갱신
async def day_fn():
    if(datetime.datetime.now(timezone("Asia/Seoul")).time() >= day_time_min and datetime.datetime.now(timezone("Asia/Seoul")).time() <= day_time_max):
        print("day_on")
        solveac_api.day_on()



@bot.command(description="오늘 푼 문제를 보여줌") # 오늘 푼 문제를 보여줌
async def 오늘(ctx, user=None):
    discord_user = ctx.author

    if user == None:
        if not solveac_api.is_reg(discord_user.id):
            await ctx.respond("등록을 진행하지 않은 유저입니다, 먼저 `등록`을 해주세요")
            return
        else:
            user=solveac_api.get_user(discord_user.id)

    
    if not solveac_api.is_user(user):
        await ctx.respond("등록되지 않은 유저입니다.")
        return
    
    count,problem_dict,total_level,tier = solveac_api.ask_today(f"{user}")

    color = 0x00ff00
    if tier == 0:
        color = 0x2d2d2d
    elif 0< tier and tier <=5 :
        color = 0xad5600
    elif 5< tier and tier <=10 :
        color = 0x435f7a
    elif 10< tier and tier <=15 :
        color = 0xec9a00
    elif 15< tier and tier <=20 :
        color = 0x27e2a4
    elif 20< tier and tier <=25 :
        color = 0x00b4fc
    elif 25< tier and tier <=30 :
        color = 0xff0062


    tmp = ""
    for problem,level in problem_dict.items():
        tmp += f"{imoji[level]}{problem} "
    tmp = tmp[:-1]
    tmp += f"\n총 푼 문제 수: {count}\n"
    if count!=0: tmp += f"평균 난이도: {imoji[round(total_level/count)]}\n"
    else : tmp += f"평균 난이도: {imoji[0]}\n"
    tmp += f"오늘의 점수: {total_level}"
    ebd=discord.Embed(title=f"{imoji[tier]}{user}",description=tmp,color=color)
    await ctx.respond(embed=ebd)


    
@bot.command(description="유저를 등록함")
async def 등록(ctx, user):
    discord_user = ctx.author
    if solveac_api.is_reg(discord_user.id):
        await ctx.respond("이미 등록을 진행한 유저입니다, 등록을 하려면 `취소`를 먼저 입력해주세요")
    elif solveac_api.is_user(user):
        await ctx.respond("이미 등록된 유저입니다.")
    
    elif not solveac_api.user_exist(user):
        await ctx.respond("존재하지 않는 유저입니다.")

    else:
        solveac_api.reg(user, discord_user.id)
        await ctx.respond(f"{user}님 등록 완료!")

@bot.command(description="유저를 등록 취소함")
async def 취소(ctx):
    discord_user = ctx.author
    if not solveac_api.is_reg(discord_user.id):
        await ctx.respond("등록을 진행하지 않은 유저입니다, 먼저 `등록`을 해주세요")
    else:
        user = solveac_api.get_user(discord_user.id)
        solveac_api.unreg(user, discord_user.id)
        await ctx.respond("등록 취소 완료!")

@bot.command(description="랭킹을 보여줌")
async def 랭킹(ctx):

    rank={}
    f_j = solveac_api.open_json()

    for user,info in f_j["user"].items():
        rank[user] = info["todaylevel"],info["todaycount"]
    
    rank = {k:v for k,v in sorted(rank.items(),key=lambda x:x[1][0],reverse=True)}

    tmp = ""

    for i,(user,(level,count)) in enumerate(rank.items()):
        if count == 0 or i == 10:
            break
        tmp += f"{i+1}위: {imoji[f_j['user'][user]['tier']]}{user} {level}점 {count}문제\n"
    
    tmp += "\n 오늘 푼 문제 수가 0인 사람\n"

    for user,(level,count) in rank.items():
        if count == 0:
            tmp += f"{user}\n"

    now=datetime.datetime.now(timezone("Asia/Seoul"))
    ebd=discord.Embed(title=f"{now.year}-{now.month}-{now.day} 오늘의 Solved!",description=tmp,color=0x00ff00)
    await ctx.respond(embed=ebd)


def run():
    bot.run(TOKEN)



if __name__ == "__main__":
    bot.run(TOKEN)
    




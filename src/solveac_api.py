import http.client
import json
import os



conn = http.client.HTTPSConnection("solved.ac")
user_db_path="/home/daniel/code_space/today_solved_discord_bot/y.json"

#리퀘스트 파트
def open_json():
    with open(f"{user_db_path}","r") as f:
        f_j = json.load(f)
    return f_j

def save_json(f_j):
    with open(f"{user_db_path}","w") as f:
        json.dump(f_j,f,indent=4)

def get_user_info(user):
    conn.request("GET", f"/api/v3/user/show?handle={user}")
    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")

    if data == "Not Found":
        return False
    else:
        json_data = json.loads(data)
        return json_data
    
def get_solve_problem(user,page):
    conn.request("GET", f"/api/v3/search/problem?query=s@{user}&sort=id&page={page}")
    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    json_data = json.loads(data)["items"]
    return json_data

def get_user(discord_id):
    f_j = open_json()
    if f"{discord_id}" not in f_j["discord_user"].keys():
        return None
    else:
        return f_j["discord_user"][f"{discord_id}"]
    
def get_user_list():
    f_j = open_json()
    return f_j["user"].keys()

#확인 파트
def user_exist(user):
    if get_user_info(user)!=False:
        return True
    else:
        return False
    
def is_reg(discord_id):
    f_j = open_json()
    if f"{discord_id}" in f_j["discord_user"].keys():
        return True
    else:
        return False

def is_user(user):
    f_j = open_json()
    if user in f_j["user"].keys():
        return True
    else:
        return False


#프로세스 파트


def solve_today_refresh(user):
    json_data=get_user_info(user)
    
    f_j=open_json()
    f_j["user"][user]["todaylevel"] = 0

    problem_tmp=dict()

    if json_data["solvedCount"] > f_j["user"][user]["solvedCount"]:
        f_j["user"][user]["solvedCount"]=json_data["solvedCount"]
        f_j["user"][user]["tier"]=json_data["tier"]
        
        for page in range(1,(json_data["solvedCount"]-1)//50+2):
            for i in get_solve_problem(user,page):
                if str(i["problemId"]) not in f_j["user"][user]["problem"].keys():
                    problem_tmp[str(i["problemId"])] = i["level"]
                    f_j["user"][user]["problem"][str(i["problemId"])] = i["level"]
                    f_j["user"][user]["todaylevel"] += i["level"]

    problem_tmp = {k:v for k,v in sorted(problem_tmp.items(),key=lambda x:int(x[1]))}
    f_j["user"][user]["todaysolved"] = problem_tmp
    f_j["user"][user]["todaycount"] = len(problem_tmp) 

    save_json(f_j)

    return problem_tmp

def reg(user,discord_id):
    f_j=open_json()
    user=f"{user}".lower()
    if not is_user(user):
        f_j["user"][user] = {"solvedCount":0,"tier":0,"problem":{}}
        f_j["discord_user"][discord_id] = user
        save_json(f_j)
        solve_today_refresh(user)
        solve_today_refresh(user)

def unreg(user,discord_id):
    f_j=open_json()
    if is_user(user):
        del f_j["user"][user]
        del f_j["discord_user"][f"{discord_id}"]
        save_json(f_j)


def day_on():
    f_j=open_json()
    user_list = get_user_list()
    for user in user_list:
        solve_today_refresh(user)


def ask_today(user):
    f_j=open_json()
    return f_j["user"][user]["todaycount"],f_j["user"][user]["todaysolved"],f_j["user"][user]["todaylevel"],f_j["user"][user]["tier"]



if __name__ == "__main__":
    day_on()


    

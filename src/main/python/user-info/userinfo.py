# -*- coding:utf-8 -*-
#env: python3
import json
import requests
import datetime

cookies = dict(JSESSIONID="6F17912A26E99F1E21C2A16276CC588C.gw1")

def currentUser():
    '''
    description: set current user by cookie.
    '''
    url = 'https://zhugeio.com/company/currentUser.jsp'
    result = requests.get(url,cookies=cookies)
    # print (result.text)

def findBase(page,platform):
    '''
    description: find all user base data.
    page: 0~ 
    platform: 1 or 2  1:Android 2:ios
    '''
    url = 'https://zhugeio.com/appuser/find.jsp'
    data = {
            "appId":48971,
            "platform":platform,
            "json":"[]",
            "page":page,
            "rows":20,
            "total":0,
            "order_by":"last_visit_time"
            }
    result = requests.post(url,cookies=cookies,data=data)
    # print (result.text)
    return result.text

def getUserid(datas):
    '''
    description: get all userid.
    '''

    it = iter(datas["values"]["users"])
    while True:
        try:
            data = next(it)
            yield data["zg_id"]
        except StopIteration:
            break
    return

def manageData(platform, exec_mode="000001"):
    '''
    mange user data by find module. multitask
    deal data by different mode.
    exec_mode: "000000"
                    || status 0: not deal, 1: write UserInfos data.
                    | status 0: not deal, 1: write base data.
                    
    '''
    #python3 range is generator
    g = range(1, 1000)
    for page in g:
        results = findBase(page, platform)
        datas = json.loads(results,encoding="utf-8")

        if "login" in datas["values"] and datas["values"]["login"] == False:
            print(results)
            break
        if len(datas["values"]["users"]) == 0:
            break

        if exec_mode[-1] == "1":
            yield getUserid(datas)

        if exec_mode[-2] == "1":
            yield datas

        if exec_mode[-3] == "1":

            pass

        if exec_mode[-4] == "1":
            pass

        if exec_mode[-5] == "1":
            pass

def buildBaseData(user_datas):

    for name,value in user_datas.items():
        if name!="zg_id":
            for data in value:
                yield data["property_name"], data["property_value"]

    return "done"

def buildUserInfosData(user_data):

    for data in user_data["app_data"]["user"]["app_user"]:
        yield data["name"],data["value"]

    return "done"

def getUserData(datas):
    it = iter(datas["values"]["users"])
    while True:
        try:
            data = next(it)
            yield data
        except StopIteration:
            break
    return

def writeBaseFile(platform,datas):
    '''
    write user base data to userbase.dat .
    '''

    with open('./user-file/userBase%s.dat' % ("Ios" if platform>1 else "Android") , 'a') as f:
        f.writelines(str(datas)+'\n')

def writeUserInfosFile(platform,datas):
    '''
    write user base data to userUserInfos.dat .
    '''

    with open('./user-file/userInfos%s.dat' % ("Ios" if platform>1 else "Android") , 'a') as f:
        f.writelines(str(datas)+'\n')

def findUserInfos(platform,uid):
    '''
    description: find all user UserInfos data.
    uid: user id  
    platform: 1 or 2  1:Android 2:ios
    '''
    result = queryUserInfos(platform, uid)
    # print (result)
    return result

def queryUserInfos(platform, uid):

    url = 'https://zhugeio.com/appuser/queryUserInfos.jsp'
    data = {
        "appId": 48971,
        "platform": platform,
        "uid": uid
    }
    result = requests.post(url, cookies=cookies, data=data)
    # print (result.text)
    return result.text

def sessions(platform, uid):
    url = 'https://zhugeio.com/appuser/sessions.jsp'
    data = {
        "appId": 48971,
        "platform": platform,
        "uid": uid,
        "beginDayId": "20171114"
    }
    result = requests.post(url, cookies=cookies, data=data)
    # print (result.text)
    return result.text

def writeUserInfosData(platform,exec_mode):
    '''
    deal data by UserInfos mode.                
    '''
    # write UserInfos data.
    app_user = {}
    for userid_generator in manageData(platform, exec_mode=exec_mode):
            for userid in userid_generator:
                print(userid)
                result = findUserInfos(platform, userid)
                result_js = json.loads(result)

                for name,value in buildUserInfosData(result_js):
                    app_user[name] = value

                result_js["app_data"]["user"]["app_user"] = app_user
                writeUserInfosFile(platform, result_js)

def writeBaseData(platform, exec_mode):
    build_data = {}
    for datas in manageData(platform, exec_mode=exec_mode):
        for user_data in getUserData(datas):
            build_data["zg_id"] = user_data["zg_id"]
            for k, v in buildBaseData(user_data):
                build_data[k] = v
            writeBaseFile(platform, build_data)

def dealData(platform,exec_mode):
    if exec_mode[-1]=="1":
        writeUserInfosData(platform,exec_mode)

    if exec_mode[-2]=="1":
        writeBaseData(platform, exec_mode)

if __name__ == "__main__":
    '''
      exec_mode: "000000"
                      || status 0: not deal, 1: write UserInfos data.
                      | status 0: not deal, 1: write base data.
                      
      platform: 1 or 2  1:Android 2:ios
      '''
    platform = 2
    # page = 2

    currentUser()

    #test find.jsp.
    # find(page,platform)

    # test find userid.
    # for userid in getUserid(platform):
    #     print(userid)

    #test write base data.
    # writeBase(platform)


    exec_mode = "000001"
    dealData(platform,exec_mode)


   

        





from nonebot import on_command, require, get_bot, get_driver
from nonebot.typing import T_State
from nonebot.params import State
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .get_problem_data import *
from .get_user_data import *
from nonebot_plugin_htmlrender import get_new_page
import os



request_today = on_command("lc每日",aliases={"lc","leetcode"},priority = 10,block = True)

request_search = on_command("lc查找",aliases={"lc搜索","leetcode搜索"},priority = 10,block = True)

request_random = on_command("lc随机",aliases={"lc随机一题","leetcode随机"},priority = 10,block = True)

request_user = on_command("lc查询",aliases={"lc查询用户","leetcode查询"},priority = 10,block = True)


try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception as e:
    logger.error("require定时插件时出错，请检查插件加载顺序。若依然不能解决，请修改__init__.py此处并查看错误原因。")
    # raise e




#查询每日一题
@request_today.handle()
async def send_today_problem(bot: Bot,event:Event):
    try:
        today_title = get_today_title()
        logger.info(f"获取今日题目成功，题目为{today_title}.")
        today_data = get_sub_problem_data(today_title)
        logger.info("获取题目内容成功。")
        logger.debug(f"题目{today_data[0]}的难度为{today_data[1]},内容略。")
    except Exception as e:
        logger.error("无法连接至leetcode，请检查网络和网络代理状态。")
        await request_today.finish("连接到leetcode失败...呜呜呜...\n请稍后再试！！")

    ##将html转为图片
    html_path = f"data/nonebot_plugin_leetcode/html"
    check_dir(html_path)
    html_file_path = html_path+f'/{today_title}.html'
    img_path = f"data/nonebot_plugin_leetcode/img"
    check_dir(img_path)
    img_file_path = img_path+f'/{today_title}.png'
    with open(html_file_path,"w+") as f:
        f.write(today_data[2])
    try:
        async with get_new_page(viewport={"width": 840, "height": 800}) as page:
                await page.goto(
                    "file://"+str(os.getcwd())+"/"+html_file_path,
                    wait_until="networkidle"
                )
                pic = await page.screenshot(full_page=True, path=img_file_path)
    except Exception as e:
        logger.error("题目内容（html）转图片出错。")
        await request_today.send("题目内容转图片时出错×")
        raise e
    await request_today.send("获取今日每日一题成功~加油哦ww\n"+"\n".join(today_data[:2])+MessageSegment.image(pic)+f"\n{today_data[3]}")






#搜索题目
@request_search.handle()
async def parse(bot: Bot, event: Event, state: T_State = State()):
    temp = str(event.get_message()).split()
    try:
        state["keyword"] = temp[1]
    except Exception:
        pass


@request_search.got("keyword",prompt="请输出要在leetcode查找的内容哦~\n可为题号、题目、题干内容哒")
async def send_today_problem(bot: Bot,event:Event,  state: T_State = State()):
    try:
        search_title = get_search_title(state["keyword"])
        if search_title:
            logger.info(f"成功搜索到关键字题目，只取第一条，题目为{search_title}.")
        else:
            logger.info("搜索成功，但并无相关题目。")
            request_search.finish("未搜索到相关题目！！\n要不...换个关键字再搜索一下吧~可为题号、题目、题干内容哒")

        today_data = get_sub_problem_data(search_title)
        logger.info("获取题目内容成功。")
        logger.debug(f"题目{today_data[0]}的难度为{today_data[1]},内容略。")
    except Exception as e:
        logger.error("无法连接至leetcode，请检查网络和网络代理状态。")
        await request_search.finish("连接到leetcode失败...呜呜呜...\n请稍后再试！！")

    ##将html转为图片
    html_path = f"data/nonebot_plugin_leetcode/html"
    check_dir(html_path)
    html_file_path = html_path+f'/{search_title}.html'
    img_path = f"data/nonebot_plugin_leetcode/img"
    check_dir(img_path)
    img_file_path = img_path+f'/{search_title}.png'
    with open(html_file_path,"w+") as f:
        f.write(today_data[2])
    try:
        async with get_new_page(viewport={"width": 840, "height": 800}) as page:
                await page.goto(
                    "file://"+str(os.getcwd())+"/"+html_file_path,
                    wait_until="networkidle"
                )
                pic = await page.screenshot(full_page=True, path=img_file_path)
    except Exception as e:
        logger.error("题目内容（html）转图片出错。")
        await request_search.send("题目内容转图片时出错×")
        raise e
    await request_search.send("搜索成功~只发送了最相关题目哦ww\n"+"\n".join(today_data[:2])+MessageSegment.image(pic)+f"\n{today_data[3]}")






#随机一题
@request_random.handle()
async def send_random_problem(bot: Bot,event:Event):
    try:
        random_title = get_random_title()
        logger.info(f"获取随机一题题目成功，题目为{random_title}.")
        random_data = get_sub_problem_data(random_title)
        logger.info("获取题目内容成功。")
        logger.debug(f"题目{random_data[0]}的难度为{random_data[1]},内容略。")
    except Exception as e:
        logger.error("无法连接至leetcode，请检查网络和网络代理状态。")
        await request_random.finish("连接到leetcode失败...呜呜呜...\n请稍后再试！！")

    ##将html转为图片
    html_path = f"data/nonebot_plugin_leetcode/html"
    check_dir(html_path)
    html_file_path = html_path+f'/{random_title}.html'
    img_path = f"data/nonebot_plugin_leetcode/img"
    check_dir(img_path)
    img_file_path = img_path+f'/{random_title}.png'
    with open(html_file_path,"w+") as f:
        f.write(random_data[2])
    try:
        async with get_new_page(viewport={"width": 840, "height": 800}) as page:
                await page.goto(
                    "file://"+str(os.getcwd())+"/"+html_file_path,
                    wait_until="networkidle"
                )
                pic = await page.screenshot(full_page=True, path=img_file_path)
    except Exception as e:
        logger.error("题目内容（html）转图片出错。")
        await request_random.send("题目内容转图片时出错×")
        raise e
    await request_random.send("成功获取随机一题~加油哦ww\n"+"\n".join(random_data[:2])+MessageSegment.image(pic)+f"\n{random_data[3]}")






#查询用户信息
@request_user.handle()
async def parse(bot: Bot, event: Event, state: T_State = State()):
    temp = str(event.get_message()).split()
    if temp[1]:
        state["user_Slug"] = temp[1]


@request_user.got("user_Slug",prompt="请输出要在leetcode查询的用户哦~\n请写入用户ID，而非用户昵称哦~")
async def send_user_data(bot: Bot,event:Event,  state: T_State = State()):
    try:
        #详细的返回json信息请查阅json/文件夹内的文本，或者参见get_user_data.py
        user_public_profile = get_user_public_profile(state["user_Slug"])
        user_question_progress = get_user_question_progress(state["user_Slug"])
        user_solution_count = get_user_solution_count(state["user_Slug"])
        user_profile_articles = get_user_profile_articles(state["user_Slug"])
        user_community_achievement = get_user_community_achievement(state["user_Slug"])
        user_question_submitstats = get_user_question_submitstats(state["user_Slug"])
        user_medals = get_user_medals(state["user_Slug"])
    except Exception as e:
        logger.error("无法连接至leetcode，请检查网络和网络代理状态。")
        await request_user.finish("连接到leetcode失败...呜呜呜...\n请稍后再试！！")
    try:
        userSlug = state["user_Slug"]
        realName = user_public_profile["data"]["userProfilePublicProfile"]["profile"]["realName"]
        userAvatar = httpx.get(user_public_profile["data"]["userProfilePublicProfile"]["profile"]["userAvatar"])
        totalSubmissions = user_public_profile["data"]["userProfilePublicProfile"]["submissionProgress"]["totalSubmissions"]
        waSubmissions = user_public_profile["data"]["userProfilePublicProfile"]["submissionProgress"]["waSubmissions"]
        acSubmissions = user_public_profile["data"]["userProfilePublicProfile"]["submissionProgress"]["acSubmissions"]
        reSubmissions = user_public_profile["data"]["userProfilePublicProfile"]["submissionProgress"]["reSubmissions"]
        otherSubmissions = user_public_profile["data"]["userProfilePublicProfile"]["submissionProgress"]["otherSubmissions"]
        acTotal = user_public_profile["data"]["userProfilePublicProfile"]["submissionProgress"]["acTotal"]
        logger.debug("user_public_profile数据解析完成")

        if user_community_achievement["data"]["profileCommunityAchievement"]:
            voteCount = user_community_achievement["data"]["profileCommunityAchievement"][0]["voteCount"]
            viewCount = user_community_achievement["data"]["profileCommunityAchievement"][0]["viewCount"]
            favoriteCount = user_community_achievement["data"]["profileCommunityAchievement"][0]["favoriteCount"]
        else:
            voteCount,viewCount,favoriteCount = 0,0,0
        logger.debug("user_community_achievement数据解析完成")

        numAcceptedQuestions_easy = user_question_progress["data"]["userProfileUserQuestionProgress"]["numAcceptedQuestions"][0]["count"]
        numAcceptedQuestions_medium = user_question_progress["data"]["userProfileUserQuestionProgress"]["numAcceptedQuestions"][1]["count"]
        numAcceptedQuestions_difficulty = user_question_progress["data"]["userProfileUserQuestionProgress"]["numAcceptedQuestions"][2]["count"]
        numFailedQuestions_easy = user_question_progress["data"]["userProfileUserQuestionProgress"]["numFailedQuestions"][0]["count"]
        numFailedQuestions_medium = user_question_progress["data"]["userProfileUserQuestionProgress"]["numFailedQuestions"][1]["count"]
        numFailedQuestions_difficulty = user_question_progress["data"]["userProfileUserQuestionProgress"]["numFailedQuestions"][2]["count"]
        numUntouchedQuestions_easy = user_question_progress["data"]["userProfileUserQuestionProgress"]["numUntouchedQuestions"][0]["count"]
        numUntouchedQuestions_medium = user_question_progress["data"]["userProfileUserQuestionProgress"]["numUntouchedQuestions"][1]["count"]
        numUntouchedQuestions_difficulty = user_question_progress["data"]["userProfileUserQuestionProgress"]["numUntouchedQuestions"][2]["count"]
        logger.debug("user_question_progress数据解析完成")

        columnsUserSolutionCount = user_solution_count["data"]["columnsUserSolutionCount"]
        logger.debug("user_solution_count数据解析完成")

        acSubmissionNum_easy = user_question_submitstats["data"]["userProfileUserQuestionSubmitStats"]["acSubmissionNum"][0]["count"]
        acSubmissionNum_medium = user_question_submitstats["data"]["userProfileUserQuestionSubmitStats"]["acSubmissionNum"][1]["count"]
        acSubmissionNum_hard = user_question_submitstats["data"]["userProfileUserQuestionSubmitStats"]["acSubmissionNum"][2]["count"]
        logger.debug("user_question_submitstats数据解析完成")

        if user_medals["data"]["userProfileUserMedals"]:
            latest_madal_name = user_medals["data"]["userProfileUserMedals"][0]["name"]
            latest_madal_date = user_medals["data"]["userProfileUserMedals"][0]["obtainDate"]
            latest_madal = f"【最近勋章】  勋章名：{latest_madal_name} |获得时间：{latest_madal_date}\n"
        else:
            latest_madal = ""
        logger.debug("user_medals数据解析完成")

        if user_profile_articles["data"]["solutionArticles"]["edges"]:
            latest_article_title = f'【最近题解】：{user_profile_articles["data"]["solutionArticles"]["edges"][0]["node"]["title"]}\n'
        else:
            latest_article_title = ""
        logger.debug("user_profile_articles数据解析完成")


    except Exception as e:
        await request_user.finish("解析用户信息出错×\n用户ID错误或不存在，请输入用户ID而非用户昵称哦~")

    await request_user.send(\
        "用户查询数据成功~\n"+\
        MessageSegment.image(userAvatar.read())+\
        f"用户名：{realName}（{userSlug}）\n"+\
            "========\n"+\
            f"【已解决问题】  EASY：{numAcceptedQuestions_easy} |MEDIUM：{numAcceptedQuestions_medium} |DIFFICULTY：{numAcceptedQuestions_difficulty}\n"+\
            f"【未答出问题】  EASY：{numFailedQuestions_easy} |MEDIUM：{numFailedQuestions_medium} |DIFFICULTY：{numFailedQuestions_difficulty}\n"+\
            f"【未接触问题】  EASY：{numUntouchedQuestions_easy} |MEDIUM：{numUntouchedQuestions_medium} |DIFFICULTY：{numUntouchedQuestions_difficulty}\n"+\
            f"【历史提交】  提交总数：{totalSubmissions} |错误提交数：{waSubmissions} |正确提交数：{acSubmissions} |重新提交数：{reSubmissions} |其他提交数：{otherSubmissions} |AC总数：{acTotal}\n"+\
            f"【提交通过数】  EASY：{acSubmissionNum_easy} |MEDIUM：{acSubmissionNum_medium} |DIFFICULTY：{acSubmissionNum_hard}\n"+\
            "========\n"
            f"【成就贡献】  阅读总数：{viewCount} |获得点赞：{voteCount} |获得收藏：{favoriteCount} |发布题解：{columnsUserSolutionCount}\n"+\
            latest_madal+latest_article_title+\
            f"用户主页：https://leetcode-cn.com/u/{userSlug}/")





#定时发送

time_list = get_driver().config.leetcode_inform_time if hasattr(get_driver().config, "leetcode_inform_time") else list()

async def send_leetcode_everyday():
    qq_list = get_bot().config.leetcode_qq_friends if hasattr(get_driver().config, "leetcode_qq_friends") else list()
    group_list = get_bot().config.leetcode_qq_groups if hasattr(get_driver().config, "leetcode_qq_groups") else list()
    try:
        today_title = get_today_title()
        logger.info(f"获取今日题目成功，题目为{today_title}.")
        today_data = get_sub_problem_data(today_title)
        logger.info("获取题目内容成功。")
        logger.debug(f"题目{today_data[0]}的难度为{today_data[1]},内容略。")
    except Exception as e:
        logger.error("无法连接至leetcode，请检查网络和网络代理状态。")
        pass
    ##将html转为图片
    html_path = f"data/nonebot_plugin_leetcode/html"
    check_dir(html_path)
    html_file_path = html_path+f'/{today_title}.html'
    img_path = f"data/nonebot_plugin_leetcode/img"
    check_dir(img_path)
    img_file_path = img_path+f'/{today_title}.png'
    with open(html_file_path,"w+") as f:
        f.write(today_data[2])
    try:
        async with get_new_page(viewport={"width": 840, "height": 800}) as page:
                await page.goto(
                    "file://"+str(os.getcwd())+"/"+html_file_path,
                    wait_until="networkidle"
                )
                pic = await page.screenshot(full_page=True, path=img_file_path)
    except Exception as e:
        logger.error("题目内容（html）转图片出错。")
        pass
        raise e
    try:
        for qq in qq_list:
            await get_bot().call_api("send_private_msg",user_id = qq ,message = "获取今日每日一题成功~加油哦ww\n"+"\n".join(today_data[:2])+MessageSegment.image(pic)+f"\n{today_data[3]}")
        for group in group_list:
            await get_bot().call_api("send_group_msg",group_id = group ,message = "获取今日每日一题成功~加油哦ww\n"+"\n".join(today_data[:2])+MessageSegment.image(pic)+f"\n{today_data[3]}")
    except TypeError:
        logger.error("插件定时发送相关设置有误，请检查.env.*文件。")





try:
    for index, time in enumerate(time_list):
        scheduler.add_job(send_leetcode_everyday, "cron", hour=time["HOUR"], minute=time["MINUTE"], id=str(index))
        logger.info(f"新建计划任务成功！！  id:{index},时间为:{time}.")
except TypeError:
    logger.error("插件定时发送相关设置有误，请检查.env.*文件。")



#创建不存在的目录
def check_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
        return "Create Successful."
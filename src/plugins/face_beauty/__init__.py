import re
import base64
from io import BytesIO

from httpx import AsyncClient
from nonebot.plugin import on_command
from nonebot.typing import T_State
from nonebot.params import State, Depends
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment

from .utils import FaceRecognition, at_send, at_finish
from .ParamsDependency import User


API_KEY = "jGL092XTL8d3V8OWEnQKG3Xl"
SECRET_KEY = "YeBXb8oYhPKDXjFmFMCqZwNVgT1VLPZm"
face_val = on_command("颜值评分", priority=50, aliases={"beauty"},block=True)
on_msg_user = User(MessageEvent)


@face_val.got("faces_pic", prompt="请发送人脸照片！")
async def beauty_score(state: T_State = State(), user: dict = Depends(on_msg_user)):
    user_id = user['user_id']
    group_id = user['group_id']
    pic_CQcode = str(state["faces_pic"])
    if "CQ:image" not in pic_CQcode:
        await at_finish(face_val, user_id, group_id, message="输入格式有误，请重新触发指令！")
    pic_url = re.findall(r"url=[^,]+", pic_CQcode)[0].rstrip(']')[4:]
    async with AsyncClient() as client:
        resp = await client.get(pic_url)
    pic_b64_str = base64.b64encode(resp.content).decode()

    faces = FaceRecognition(pic_b64_str, API_KEY, SECRET_KEY)
    result = await faces.face_beauty()
    if result['error_msg'] == 'pic not has face':
        await at_finish(face_val, user_id, group_id, message="未从图片中识别到人脸！")
    elif result['error_msg'] == 'image size is too large':
        await at_finish(face_val, user_id, group_id, message="图片尺寸过大！")

    faces_gender = []
    faces_pos = []
    faces_beauty = []
    try:
        for face in result['result']['face_list']:
            faces_gender.append('男' if face['gender']['type'] == 'male' else '女')
            faces_pos.append(face['location'])
            faces_beauty.append(face['beauty'])
    except (KeyError, TypeError):
        await at_finish(face_val, user_id, group_id, message="请重新检查图片！")

    pic = resp.content
    pic_bytes_stream = BytesIO(pic)
    buf = BytesIO()
    await faces.draw_face_rects(pic_bytes_stream, buf, faces_pos)

    msg = MessageSegment.image(buf.getvalue())
    for i in range(len(faces_beauty)):
        msg += f"Face{i + 1}:\n" \
               f"性别: {faces_gender[i]}\n" \
               f"颜值评分: {faces_beauty[i]}/100\n"
    await face_val.send(msg)

    pic_bytes_stream.close()
    buf.close()

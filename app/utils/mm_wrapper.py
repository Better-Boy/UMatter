from app import mm_client
import json, datetime
from uuid import uuid4
from io import BytesIO

def get_user_id(user_name):
    user = mm_client.users.get_user_by_username(user_name)
    return user["id"]

def upload_file(channel_id, blob):
    byte_obj = BytesIO(bytes(blob))
    form_data = {
        "channel_id": ('', channel_id),
        "files": (f"{uuid4().hex}.png", byte_obj),
    }
    upload_file_reply = mm_client.files.upload_file(form_data)
    return upload_file_reply["file_infos"][0]["id"]

def create_post(text, file_id, channel_id):
    post_param = json.dumps({
        "channel_id": channel_id,
        "message": text,
        "file_ids": [file_id] if isinstance(file_id, str) else file_id
    })
    post_ret = mm_client.posts.create_post(post_param)
    time_stamp = datetime.datetime.fromtimestamp(float(post_ret["create_at"]/1000)).strftime('%Y-%m-%d %H:%M:%S.%f')
    return post_ret["id"], time_stamp


def get_channel_type(channel_id):
    channel_res = mm_client.channels.get_channel(channel_id)
    return channel_res["type"]

def create_custom_emoji(name, byte_obj):
    try:
        _ = mm_client.emoji.create_custom_emoji(name, {"image": BytesIO(byte_obj)} )
        return True, None
    except Exception as e:
        return False, str(e)

def get_list_of_custom_emoji():
    try:
        res = mm_client.emoji.get_emoji_list()
        return True, res
    except Exception as e:
        return False, str(e)

def get_reaction_bulk(post_id_list):
    try:
        res = mm_client.reactions.bulk_get_reactions_of_post(post_id_list)
        return True, res
    except Exception as e:
        return False, str(e)
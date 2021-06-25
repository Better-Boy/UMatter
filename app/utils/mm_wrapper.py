from app import mm_client, logger
import json, datetime
from uuid import uuid4
from io import BytesIO

def get_user_id(user_name):
    logger.debug("In getting user id")
    try:
        user = mm_client.users.get_user_by_username(user_name)
        return True, user["id"]
    except Exception as e:
        logger.exception("Exception in getting user id from mattermost server")
        return False, None

def upload_file(channel_id, blob):
    logger.debug("in uploading file")
    try:
        byte_obj = BytesIO(bytes(blob))
        form_data = {
            "channel_id": ('', channel_id),
            "files": (f"{uuid4().hex}.png", byte_obj),
        }
        upload_file_reply = mm_client.files.upload_file(form_data)
        return True, upload_file_reply["file_infos"][0]["id"]
    except Exception as e:
        logger.exception("Exception in uploading file to mattermost server")
        return False, None

def upload_csv(channel_id, file_):
    logger.debug("in uploading file")
    try:
        form_data = {
            "channel_id": ('', channel_id),
            "files": (file_, open(file_, 'rb')),
        }
        upload_file_reply = mm_client.files.upload_file(form_data)
        return True, upload_file_reply["file_infos"][0]["id"]
    except Exception as e:
        logger.exception("Exception in uploading file to mattermost server")
        return False, None

def create_post(text, file_id, channel_id):
    logger.debug("Creating post")
    try:
        post_param = json.dumps({
            "channel_id": channel_id,
            "message": text,
            "file_ids": [file_id] if isinstance(file_id, str) else file_id
        })
        post_ret = mm_client.posts.create_post(post_param)
        time_stamp = datetime.datetime.fromtimestamp(float(post_ret["create_at"]/1000)).strftime('%Y-%m-%d %H:%M:%S.%f')
        return True, post_ret["id"], time_stamp
    except Exception as e:
        logger.exception("Exception in creating a post to mattermost server")
        return False, None, None


def get_channel_type(channel_id):
    channel_res = mm_client.channels.get_channel(channel_id)
    return channel_res["type"]

def create_custom_emoji(name, byte_obj):
    logger.debug("in creating custom emoji")
    try:
        _ = mm_client.emoji.create_custom_emoji(name, {"image": BytesIO(byte_obj)} )
        return True
    except Exception as e:
        logger.exception("Exception in creating custom emoji to mattermost server")
        return False

def get_list_of_custom_emoji():
    logger.debug("In getting a list of custom emojis")
    try:
        res = mm_client.emoji.get_emoji_list()
        return True, res
    except Exception as e:
        logger.exception("Exception in getting list of custom emojis from mattermost server")
        return False, str(e)

def get_reaction_bulk(post_id_list):
    logger.debug("In getting a list of custom emojis")
    try:
        res = mm_client.reactions.bulk_get_reactions_of_post(post_id_list)
        return True, res
    except Exception as e:
        logger.exception("Exception in getting bulk reaction from mattermost server")
        return False, str(e)
import textwrap
from textwrap import wrap
# from wand.color import Color
# from wand.drawing import Drawing
# from wand.image import Image
# from wand.font import Font
from app import INSERT_QUERY_STRING, color_list, WEEKLY_THRESHOLD
import os, requests, random
import matplotlib
from matplotlib import pyplot as plt
from io import BytesIO
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

matplotlib.use('agg')
dir_path = os.path.dirname(os.path.realpath(__file__))
FONT_PATH = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)), 'resources/CANDY.TTF')
IMAGE_PATH = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)), 'resources/star.png')

pattern = Image.open(IMAGE_PATH, "r").convert('RGBA')
wrapper = textwrap.TextWrapper(width=20)
size = width, height = pattern.size
draw = ImageDraw.Draw(pattern, 'RGBA')
font = ImageFont.truetype(FONT_PATH, 150)

# def generate_blob(text):
#     with Image(width=320, height=200, background=(Color('lightblue'))) as image:
#         image.caption(text, font=Font(FONT_PATH, size=32, color=(Color('white')), stroke_color=(Color('grey24'))), left=50, top=50)
#         return image.make_blob('png')
# , fill=(0,0,0,0)

def generate_blob(text):
    word_list = wrapper.wrap(text=text) 
    draw.text((600,800), '\n'.join(word_list), fill=(191, 63, 63), font=font)
    imgByteArr = BytesIO()
    pattern.save(imgByteArr, format='png')
    return imgByteArr.getvalue()

def download_image(link):
    res = requests.get(link)
    res.raise_for_status()
    return res.content

def make_plot(label, size,title):
    fig, ax1 = plt.subplots()
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    colors = random.sample(color_list, len(label))
    ax1.pie(size, colors=colors, labels=label, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode = [0.05] * len(label), labeldistance=1.2)
    ax1.axis('equal')
    ax1.set_title(title, fontdict={'fontsize': 10, 'fontweight': 'medium'})
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf.read()

def build_insert_query(data):
    query_string = INSERT_QUERY_STRING % (data['channel_id'], data['channel_name'], data['from_user_id'], data['from_user_name'], data['points'], data['to_user_id'], data['to_user_name'], data['post_id'], data['insertionTime'], data['message'])
    return query_string

def select_feed_user_query(user_id, channel_name=None, limit=None, orderby=False):
    query_string = f'select * from transaction where (from_user_id="{user_id}" or to_user_id="{user_id}")'
    if channel_name:
        query_string = f'{query_string} and channel_name="{channel_name}"'
    if orderby:
        query_string = f'{query_string} order by insertionTime'
    if limit:
        query_string = f'{query_string} limit {limit}'
    return query_string + ";"

def select_feed_user_timebound(user_id, start_date, end_date):
    query_string = f'select * from transaction where from_user_id="{user_id}" and date(insertionTime) >= "{start_date}" and date(insertionTime) <= "{end_date}";'
    return query_string

def select_feed_channel(channel_id, start_date, end_date, is_week=False):
    query_string = f'select to_user_name, sum(points) as sum_total, RANK() OVER(order by sum(points) desc) from transaction where channel_id="{channel_id}" and date(insertionTime) >= "{start_date}" and date(insertionTime) <= "{end_date}" group by to_user_name {"having sum_total > " + str(WEEKLY_THRESHOLD) if is_week else "" } order by sum_total desc;'
    return query_string

def generate_md_table(data, headers):
    writer = MarkdownTableWriter()
    writer.headers = headers
    writer.column_styles = [Style(align="center", font_weight="bold")] * len(headers)
    writer.value_matrix = data
    return writer.dumps()
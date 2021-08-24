from mcdreforged.api.all import *
from datetime import datetime
from math import floor

# -----------------------------------------
nbt_file = 'server/world/level.dat' # NBT 文件位置，设置为 -1 以使用日期模式
start_date = '2021-06-22' # 开服日期
day_text = 'The server has been running for $day days' # 显示文字
# -----------------------------------------

PLUGIN_METADATA = {
    'id': 'daycount_nbt',
    'version': '4.1',
    'name': 'DayCount-NBT',
    'description': 'To get the running time of the server',
    'author': 'Charlie_NI',
}
 
def getday():
    try:
        return (datetime.now() - datetime.strptime(start_date, '%Y-%m-%d')).days
    except Exception:
        return 0

def get_day_text():
    return day_text.replace('$day', str(getday()))

def display_days(source: CommandSource):
    source.reply(get_day_text())

def on_load(server: ServerInterface, old):
    server.register_command(Literal('!!day').runs(display_days))
    server.register_help_message('!!day', 'To get the running time of the server')

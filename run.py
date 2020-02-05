

from app import log_utils
import pymysql
# 导入Flask类
from flask import Flask, render_template


# 实例化，可视为固定格式
app = Flask(__name__)


# db = pymysql.connect("47.112.159.211:3306", "root", "root", "mysql")

connect = pymysql.connect(
    host='47.112.159.211',
    port=3306,
    user='pingpongus_test',
    passwd='pingpongus_test',
    db='pingpongus_test',
    charset='utf8'
)

logger = log_utils.get_logger("app.log")

# route()方法用于设定路由；类似spring路由配置
@app.route('/hello')
def hello_world():
	# 新建游标
    cursor = connect.cursor()
    # 执行sql语句
    cursor.execute("select * from ppu_demo")
    data = cursor.fetchone()
    print(data)
    logger.info(data)
    return 'Hello, World!'

@app.route('/index')
def htmls_t():
    return render_template('jsclient.html');

@app.route('/index2')
def htmls_t2():
    return render_template('jsclient2.html');



@app.route('/sync_state')
def sync_state():
    return render_template('sync_state.html');


@app.route('/gobang_game')
def gobang_game():
    return render_template('gobang_game.html');



@app.route('/gobang_game_demo')
def gobang_game_demo():
    return render_template('gobang_game_demo.html');



@app.route('/h5demo')
def h5demo():
    return render_template('h5demo.html');

@app.route('/h5snake')
def h5snake():
    return render_template('h5snake.html');

if __name__ == '__main__':
    # app.run(host, port, debug, options)
    # 默认值：host=127.0.0.1, port=5000, debug=false
    app.run(host='0.0.0.0', port=8080)


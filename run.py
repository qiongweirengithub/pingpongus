

import pymysql
# 导入Flask类
from flask import Flask
# 实例化，可视为固定格式
app = Flask(__name__)


db = pymysql.connect("http://db.pingpongus.com", "root", "root", "mysql")

# route()方法用于设定路由；类似spring路由配置
@app.route('/')
def hello_world():
	# 新建游标
	cursor = db.cursor()
	# 执行sql语句
	cursor.execute("select * from db")
	data = cursor.fetchone()
	print(data)
	return 'Hello, World!'

if __name__ == '__main__':
    # app.run(host, port, debug, options)
    # 默认值：host=127.0.0.1, port=5000, debug=false
    app.run(host='0.0.0.0', port=8080)


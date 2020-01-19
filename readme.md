-- this record pingpongus server bulid process
# pingpongus server build
## server 

1. aliyun cenos

2. python3.7 envirment
    2.1  wget python3.7
    2.2 ./configure   --prefix=/usr/local/python37  --with-ssl           # with ssh is important ,  if not ,  inside virtualenv pip install run fail 
    2.3 make  && make install

3. pingpongus run envirment 
    3.1 pip install virtualenv
    3.2 virtualenv -p python3.7 pingpongus
    3.3 pip install flask
    3.4 pip install guni...
    3.4 gunni -c ./guni_configure.py  controller:app
          3.4.1  must  bind : 0.0.0.0
    3.5  ip:port/ , if success ,  echo hello world

4. ngxix
    4.1  ngxin run envirment
           4.1.1yum -y install gcc pcre-devel zlib-devel openssl openssl-devel

    4.2 down load stable ngixn version 
           4.2.1 wget http://nginx.org/download/nginx-1.15.12.tar.gz
           4.2.2  tar -zxvf nginx.tar.gz
    4.3 ./configure --prefix=/usr/local/nginx
    4.4 make && make  install


5. mysql



   
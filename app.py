from flask import Flask, flash, render_template, request, redirect, url_for, session, send_from_directory
import os
from datetime import timedelta
import my_user
import requests 



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Güvenli bir oturum anahtarı

# Doğru kullanıcı adı ve şifre (güvenlik amacıyla sabitlenmiş)
CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "password123"
app.permanent_session_lifetime = timedelta(minutes=30)
default_storage_size = 1

users_list = my_user.user_list()

dosya = open("user.csv",'r')
file_content = dosya.readlines()
dosya.close()

for i in file_content[1:]:
    users_list.append(my_user.user(i))

"""
for i in users_list.list:
    print(i.username)
"""

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_user_folder(username):
    return os.path.join('uploads', username)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username = username.lower()

        user = users_list.get_user_by_name(username)
        #if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
        if user is not None and  password == user.password:
            session['logged_in'] = True  # Kullanıcı oturumu başlatılır
            session['username'] = user.username 
            session.permanent = False # Oturumun sadece bu tarayıcı oturumunda geçerli olmasını sağlar.
            #True olsaydi tarayici kapanip acilsa bile oturum acik kalmaya devam ederdi :) MUAZZAM BILGILER
            
            print("buraya girdik 4")
            return redirect(url_for('browse_root'))
        else:
            return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')


@app.route('/browse/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/browse/<path:path>', methods=['GET', 'POST'])
def browse_files(path):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    username = session['username']
    base_dir = get_user_folder(username)
    current_path = os.path.join(base_dir, path)

    if request.method == 'POST':
        if 'folder_name' in request.form:
            # Yeni klasör ekleme işlemi
            folder_name = request.form['folder_name']
            new_folder_path = os.path.join(current_path, folder_name)

            try:
                os.makedirs(new_folder_path)
            except OSError as e:
                flash(f"Klasör oluşturulurken bir hata oluştu: {e}")
            
        elif 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename:
                    file_path = os.path.join(current_path, file.filename)
                    file.save(file_path)

        elif 'delete_item' in request.form:
            # Dosya veya klasör silme işlemi
            delete_item = request.form['delete_item']
            delete_path = os.path.join(current_path, delete_item)
            try:
                if os.path.isdir(delete_path):
                    os.rmdir(delete_path)  # Klasörü sil
                else:
                    os.remove(delete_path)  # Dosyayı sil
            except OSError as e:
                flash(f"Silme işlemi sırasında bir hata oluştu: {e}")

        elif 'old_name' in request.form and 'new_name' in request.form:
            # Yeniden adlandırma işlemi
            old_name = request.form['old_name']
            new_name = request.form['new_name']
            old_path = os.path.join(current_path, old_name)
            new_path = os.path.join(current_path, new_name)
            try:
                os.rename(old_path, new_path)
            except OSError as e:
                flash(f"Yeniden adlandırma işlemi sırasında bir hata oluştu: {e}")


        return redirect(url_for('browse_files', path=path))
    if os.path.isdir(current_path):
        items = os.listdir(current_path)
        return render_template('browse.html', items=items, path=path, base_path=base_dir)
    else:
        return send_from_directory(base_dir, path)


@app.route('/browse/')
def browse_root():
    return browse_files('')

"""@app.route('/files/<folder_path>')
def show_files(folder_path):
    if not session.get('logged_in'):  # Kullanıcı oturum açmamışsa
        return redirect(url_for('login'))  # Giriş sayfasına yönlendir

    files = os.listdir(folder_path)
    return render_template('files.html', files=files,folder_path = folder_path )

"""

"""@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not session.get('logged_in'):  # Kullanıcı oturum açmamışsa
        return redirect(url_for('login'))  # Giriş sayfasına yönlendir
    else:
        print(filename)
        if os.path.isfile(os.path.join(folder_path,filename)):
            print('aynen kanka bu bir file')

        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],session.get('username')),filename)
"""


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Kullanıcı oturumunu sonlandırır
    return redirect(url_for('login'))


@app.route("/create-account",methods = ["GET","POST"])
def create_user():
    if request.method == "POST":
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        username = username.lower()


        if ' ' in username:
            return render_template('create_user.html',error = 'Username cannot contain space!')
        
        elif(users_list.get_user_by_name(username) is not None):
            return render_template('create_user.html',error = 'This username already exists. Choose another')
        elif(password1 != password2):
            return render_template('create_user.html',error = 'Both of the passwords should be same!')
        else:
            dosya = open('user.csv','a')
            id = len(users_list.list)+1
            line = str(id)+';'+username+';'+password1+';'+ str(default_storage_size)+'\n'
            dosya.write(line)
            dosya.close()
            users_list.append(my_user.user(line))
            os.mkdir("uploads/"+username)



        
        return render_template("create_user.html")

    else:
        return render_template("create_user.html")


@app.template_filter('isdir')
def isdir_filter(item, base_path):
    return os.path.isdir(os.path.join(base_path, item))

@app.route("/gettcpvalues")

def get_tcp_values():
    try:
        response = requests.get("http://127.0.0.1:4041/api/tunnels")
        tunnels = response.json()

        tunnel_list = tunnels["tunnels"]


        for tunnel in tunnel_list:
            name = tunnel["name"]
            public_url = tunnel["public_url"]
            proto = tunnel["proto"]
            addr = tunnel["config"]["addr"]
            
            return public_url
    except:
        return "aaaaa"

if __name__ == '__main__':
    app.run(debug=True,port=5001,host="0.0.0.0")

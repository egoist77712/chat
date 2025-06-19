from flask import Flask, render_template, jsonify, request,url_for
import random
import requests
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)


api_keys = []

def load_banned_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        # 去除每行的空白字符（换行符/空格），并过滤空行
        banned_words = {line.strip() for line in f if line.strip()}
    return banned_words

def check_sentence(sentence, banned_words):
    # 将句子拆分为单词（假设单词用空格分隔）
    words_in_sentence = sentence.lower().split()  # 转为小写便于匹配
    # 检查是否有单词在违禁词集合中
    has_banned = any(word in banned_words for word in words_in_sentence)
    if has_banned:
        # 可选：返回具体违禁词
        found_words = [word for word in words_in_sentence if word in banned_words]
        return True, found_words
    else:
        return False, []

def write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,sheet_name):
    # Step 1: 设置认证
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    # Step 2: 打开工作簿和第一个工作表
    sheet_id = "1wm3cfLh-AGl3Vbi_mi9nMU8IEuW0v-ZZdSgilxfDNWw"
    workbook = client.open_by_key(sheet_id)
    sheet = workbook.worksheet(sheet_name) 

    # Step 3: 准备要追加的数据
    new_row = [
        ip,
        "\n".join(user_msg),
        "\n".join(chatbot_msg),
        like_status,
        "\n".join(comment_list)
    ]

    # Step 4: 追加数据为一行
    sheet.append_row(new_row)

    print("数据已追加到第一个工作表")


@app.route('/')
def home():
    # 渲染 index.html 页面
    return render_template('index.html')

@app.route('/medium')
def home2():
    # 渲染 index.html 页面
    return render_template('index_m.html')

@app.route('/low')
def home3():
    # 渲染 index.html 页面
    return render_template('index_l.html')

@app.route('/3d_high')
def home4():
    # 渲染 index.html 页面
    return render_template('index_3D_h.html')

@app.route('/3d_medium')
def home5():
    # 渲染 index.html 页面
    return render_template('index_3D_m.html')


@app.route('/3d_low')
def home6():
    # 渲染 index.html 页面
    return render_template('index_3D_l.html')

@app.route('/comment', methods=['POST'])
def comment():
    data = request.json
    user_message = data.get('message')
    banned_words = load_banned_words('ban.txt')
    has_banned, found_words = check_sentence(user_message, banned_words)

    if has_banned:
        print("句子包含违禁词！发现的词汇：", found_words)
        return jsonify({"message": "ban_word"})
    return jsonify({"message": "good"})

@app.route('/get_message', methods=['POST'])
def get_message():
    # 获取前端发送的 JSON 数据
    data = request.json
    user_message = data.get('message')
    flow_status = data.get('flow_status')

    # 加载违禁词
    banned_words = load_banned_words('ban.txt')

    # 测试句子
    test_sentence = user_message 

    # 检查句子
    has_banned, found_words = check_sentence(test_sentence, banned_words)

    if has_banned:
        print("句子包含违禁词！发现的词汇：", found_words)
        return jsonify({"message": "ban_word"})


    base_prompt=''
    if flow_status==1:
        base_prompt = f"""I asked the user: "Did you enjoy reading my previous post?"

        Based on the user's reply, classify the response strictly into one of the following:

        - Return "yes" if the user expresses enjoyment **or neutral-positive sentiment** (e.g., "I enjoyed reading it", "Yes I liked it", "It was great", "Maybe", "A little", "Not bad", "It was okay", etc.).
        - Return "no" if the user clearly expresses dislike (e.g., "No, I didn't like it", "It was boring", "I hated it", etc.).
        - Return "redo" if the user says something unrelated, unclear, or does not address the question (e.g., "What post?", "I'm busy", "Tell me more").

        Only return one word: yes, no, or redo.

        User answer: {user_message}
        """
    elif flow_status==2:       
        base_prompt = f"""I asked the user: "What kind of content are you interested in on social media?"  

        If the user answers with a clear interest in **any content type that can be posted on social media** (e.g., "I like concert highlights", "I enjoy gaming streams", "I'm into art sketches", "I love pet tricks", "I follow tech reviews"), extract and return only the name of the interest (e.g., "concert highlights", "gaming streams", "art sketches", "pet tricks", "tech reviews").  

        
         If the user answers with a clear interest in **any content type that can be posted on social media** (e.g., "doll", "gaming", "sketches", "pet", "cat"), extract and return only the name of the interest (e.g., "doll", "gaming", "sketches", "pet", "cat").  

        Topics include (but are not limited to) all shareable content on social platforms, such as:  
        - Entertainment: concerts, movie trailers, celebrity updates  
        - Lifestyle: fashion hauls, cooking tutorials, travel diaries  
        - Creative: art, DIY projects, music covers  
        - Niche interests: gaming, tech, fitness, pet care, beers and beer, wine tasting 
        - User-generated content: personal stories, vlogs, challenges
        - Names of celebrities or famous people(Both uppercase and lowercase are acceptable.) : Jay Chou, g dragon(G-DRAGON), jj lin(JJ Lin)
        - Name of the country : singapore, SG, China, USA, Malaysia
        - the aspect of education: Educate Campus,Education

        If there are spelling mistakes, correct them and extract the appropriate interest(s).
        If there are multiple interests in one message, return each interest separated by commas (e.g., "gaming and tech reviews").
        If the user gives an unrelated, ambiguous, or off-topic answer (e.g., "I don’t use social media", "Not sure"), return "redo".  

        Only return the interest name (e.g., "concert highlights") or "redo".  

        User answer: my interest is {user_message}
        """
        
    print(base_prompt)
    url = "https://api.openai.com/v1/chat/completions"
    headers_template = {
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o",
        "temperature": 0.7,
        "messages": [
            {
                "role": "system",
                "content": base_prompt,
            }
        ],
        "max_tokens": 150
    }
    headers = headers_template.copy()
    api_key = ""
    headers["Authorization"] = f"Bearer {api_key}"
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raise exception for HTTP errors
    answer = response.json()['choices'][0]['message']['content']
    print(answer)
    cleaned = answer.strip('"')
    return jsonify({"message": cleaned})

@app.route("/save_chat", methods=["POST"])
def save_chat():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    ip = data.get("IP")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,"high")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat2", methods=["POST"])
def save_chat2():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    ip = data.get("IP")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,"medium")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat3", methods=["POST"])
def save_chat3():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    ip = data.get("IP")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,"low")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat4", methods=["POST"])
def save_chat4():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    ip = data.get("IP")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,"3d_high")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat5", methods=["POST"])
def save_chat5():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    ip = data.get("IP")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,"3d_medium")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat6", methods=["POST"])
def save_chat6():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    ip = data.get("IP")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,"3d_low")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

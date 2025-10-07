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

def write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,sheet_name):
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
        "\n".join(comment_list),
        follow,
        s_time,
        e_time
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

@app.route('/high2')
def home7():
    # 渲染 index.html 页面
    return render_template('index2.html')

@app.route('/medium2')
def home8():
    # 渲染 index.html 页面
    return render_template('index2_m.html')

@app.route('/low2')
def home9():
    # 渲染 index.html 页面
    return render_template('index2_l.html')

@app.route('/3d_high2')
def home10():
    # 渲染 index.html 页面
    return render_template('index_3d_2.html')

@app.route('/3d_medium2')
def home11():
    # 渲染 index.html 页面
    return render_template('index2_3d_m2.html')


@app.route('/3d_low2')
def home12():
    # 渲染 index.html 页面
    return render_template('index2_3d_l2.html')

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
        base_prompt = f"""
        I asked the user: "May I know which country you live in?"

        Your task:
        - If the user input contains a **valid country name** or **official/commonly used country abbreviation** (e.g., "SG" for Singapore, "US" for United States), return the **correct country name** in English (e.g., "Singapore", "United States", "Malaysia").
        - If the user input contains a **country name or abbreviation with clear spelling errors**, correct it and return the **correct country name** in English.
        - If the input is **unclear, unrelated, not a country name/abbreviation, or cannot be corrected confidently**, return the string **"redo"**.

        User answer: {user_message}

        Your response (only return the corrected country name or "redo"):
        """
        
    elif flow_status==2:       
        base_prompt = f"""I asked the user: "What kind of content are you interested in on social media?"  

        If the user answers with a clear interest in **any content type that can be posted on social media** (e.g., "I like concert highlights", "I enjoy gaming streams", "I'm into art sketches", "I love pet tricks", "I follow tech reviews","I follow politics news", "I'm into finance news", "I enjoy reading books"), extract and return only the name of the interest (e.g., "concert highlights", "gaming streams", "art sketches", "pet tricks", "tech reviews","politics news", "finance news", "books").  

        
         If the user answers with a clear interest in **any content type that can be posted on social media** (e.g., "doll", "gaming", "sketches", "pet", "cat" ， "news"), extract and return only the name of the interest (e.g., "doll", "gaming", "sketches", "pet", "cat"， "news").  

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
        If there are multiple interests in one message, return each interest connected using " and " or " & " (e.g., "book and music" or "book & music"), but do not use commas.
        If the user gives an unrelated, ambiguous, or off-topic answer (e.g., "I don’t use social media", "Not sure" ， "Fine"), return "redo".  

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

@app.route('/get_message2', methods=['POST'])
def get_message2():
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
        base_prompt = f"""
        You are a name extractor.  
        You asked the user: "How may I address you?"  

        If the user's response contains a clear **name, stage name, alias, or nickname**  
        (e.g., "I am Tom", "Call me Sarah", "My name is Alex", "I am Chen xi",  
        "Call me Abdul Rahman bin Mohd", "Call me G Dragon", "MJ", "HH", "Ng", "wong"),  
        → return only the extracted full name/alias, formatted as follows:  

        **Formatting rules:**  
        - Each word’s **first letter uppercase** and the rest lowercase.  
        - **Preserve 2-letter or all-uppercase names** (e.g., “MJ”, “HH”, “SS”).  
        - Preserve **mixed case or hyphenated** patterns (e.g., “H-h”, “Hh”).  
        - Always capitalize surnames even if input is lowercase (e.g., “wong” → “Wong”, “ng” → “Ng”).  
        - If the input is a single name or initial (e.g., “Seah”, “Ng”), still accept it as valid.  

        If the user's response does **not** contain a valid name, alias, or nickname  
        (e.g., vague phrases like "call me maybe", "whatever", "you decide"),  
        → return exactly `redo`.  

        You must only return one of the two cases:  
        1. The extracted full name/alias/nickname (properly formatted)  
        2. `redo`  

        User answer: {user_message}
        """

        
    elif flow_status==2:       
        base_prompt = f"""
       You are a music preference extractor.  
        You ask the user: "Nice to meet you! May I know what types of music do you like?"  

        If the user's response contains one or more clear music genres or styles (e.g., "I like rock", "My favorite is jazz", "I enjoy pop music", "I like piano", "chinese rock", "violin", "country music"),  
        → return only the extracted genre/style word(s) in lowercase.  

        Rules:  
        - If the user lists multiple genres/styles, return them joined with ` & ` (e.g., `pop music & rock music`, `jazz music & blues music`, `blues music & violin music`).  
        - If the user enters a shortened form (e.g., `pop`, `rock`, `jazz`, `blues`, `country`, `rock and roll`, `popular songs`, `funk`, `punk`), return the full form with “music” (e.g., `pop music`, `rock music`, `jazz music`, `blues music`, `country music`, `rock and roll`, `pop music`, `funk music`, `punk music`).  
        - If the user enters an instrument (e.g., `piano`, `guitar`, `violin`), return the full form with “music” (e.g., `piano music`, `guitar music`, `violin music`).  
        - Keep everything in lowercase.  
        - Do not add extra text beyond the genre/style(s).  
        - Normalize common variants (case-insensitive — e.g., rock music / rOCk music / rock mUsIc all treated the same).
        - If the user only enters one type of music, then simply output that one type of music. For example, if the user enters 'meditation music', then output the music type entered by the user, 'meditation music', rather than 'new age/meditation music'.
        - When listing music genres, it is essential to append the suffix 'music' after each type, for example, 'meditation music', 'new age music', and so on.
        - If the user enters multiple types of music at the same time, then output all the types of music entered by the user.
        - If the user enters 70’s, 80’s, or other similar old-era music, categorize them as oldies music and output oldies music.

        Recognized genres/styles include (but are not limited to):  
        - funk music  
        - punk music  
        - rock and roll music 
        - pop music  
        - rock music  
        - hip-hop music
        - rap music
        - r&b music  
        - soul music 
        - dance music  
        - edm music 
        - classical music  
        - jazz music  
        - blues music  
        - folk music  
        - country music  
        - piano music  
        - guitar music  
        - violin music  
        - orchestral music  
        - symphonic music 
        - ambient music  
        - instrumental  
        - soundtrack music  
        - film score music
        - reggae music  
        - latin music  
        - salsa music
        - k-pop music  
        - j-pop music 
        - metal music  
        - new age music
        - meditation music  
        - Vocaloid music
        - Indie music
        - bolero music
        - oldies music
        - gospel music
        - worship music
        - Christian music
        - Lofi music
        - Lo-fi music
        - Lofi Hip-Hop music
        - Easy Listening music
        - Adult Contemporary music
        - Lounge music
        - Chillhop music
        - Ambient and Chill-out music
        - Ballad music


        If the user's response does NOT contain a clear music genre or style,  
        → return exactly `redo`.  

        You must only return one of the two cases:  
        1. The extracted music genre/style(s) (single word or phrase or multiple joined by ` & `, all lowercase, no extra text)  
        2. `redo`  

        User answer: {user_message}
        """

    elif flow_status==3:   
        base_prompt = f"""
        You are an earbuds feature extractor.  
        You asked the user: "What function do you care about the most when choosing earbuds?"  

        If the user's response clearly mentions one or more earbuds features, return only those feature(s) in lowercase.  

        Rules:  
        - If the user lists multiple features, return them joined with ` & ` (e.g., `comfort & battery life`, `sound quality & noise cancellation`).  

        - Normalize common variants (case-insensitive — e.g., SOund / SOUND / Sound all treated the same):  
            - comfortable / fitting → comfort  
            - mic quality / microphone → call quality  
            - design / looks / appearance → style/design  
            - waterproof / sweatproof → water/sweat resistance  
            - price / cost / value for money / worth it / expensive / cheap / affordable / budget → cost-efficiency  
            - color / colours → color  
            - mute / muting / silent mode → mute  
            - sound / audio quality → sound quality  
            - weight / light / heavy → weight  
            - usability / ease of use / easy to use / good to use / 好用 / 易用 → usability  
            - cost-efficiency / value / worth → cost-efficiency  
            - eco friendly / environmentally friendly / green material → eco friendly  
            - quality / overall quality → quality  
            - function / functionality → functionality  
            - noise reduction / noise cancelling / ANC / cancellation → noise reduction  
            - good vibe / aesthetic feel / mood → good vibe  
            - sound clarity / clear sound / crisp sound → sound clarity  
            - bass function / bass boost / deep bass → bass function  
            - sound balance / balanced audio / equalized sound → sound balance  
            - easy control / voice control / without opening app → easy control  

        - Always output in **lowercase** regardless of input case.  
        - Return only the feature text(s) (no extra characters or punctuation).  

        If the response does **NOT** contain a clear earbuds feature, return exactly: `redo`.  

        You must only return one of the two cases:  
        1. the extracted earbuds feature text(s) (lowercase, normalized, joined with ` & ` if multiple)  
        2. `redo`  

        User answer: {user_message}

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
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"high")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat2", methods=["POST"])
def save_chat2():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"medium")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat3", methods=["POST"])
def save_chat3():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"low")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat4", methods=["POST"])
def save_chat4():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")
    print(ip)

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow, s_time,e_time,"3d_high")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat5", methods=["POST"])
def save_chat5():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"3d_medium")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat6", methods=["POST"])
def save_chat6():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"3d_low")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat7", methods=["POST"])
def save_chat7():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"high2")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat8", methods=["POST"])
def save_chat8():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"medium2")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat9", methods=["POST"])
def save_chat9():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"low2")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat10", methods=["POST"])
def save_chat10():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"surreal_high")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat11", methods=["POST"])
def save_chat11():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"surreal_medium")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})

@app.route("/save_chat12", methods=["POST"])
def save_chat12():
    data = request.get_json()
    user_msg = data.get("user_message")
    chatbot_msg = data.get("chatbot_message")
    like_status = data.get("like_status")
    comment_list = data.get("comment_list")
    s_time=data.get("enter_time")
    e_time=data.get("finnish_time")
    ip = data.get("IP")
    follow=data.get("follow")

    write_to_google_sheet(user_msg, chatbot_msg, like_status, comment_list, ip,follow,s_time,e_time,"surreal_low")
    return jsonify({"status": "success", "message": "数据已保存到 Google Sheet"})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

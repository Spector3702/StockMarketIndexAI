import sys
import re
import google.generativeai as genai
from firebase import firebase
from linebot import LineBotApi
from linebot.models import TextSendMessage, TextMessage

class GeminiTeacher():
    def __init__(self, event, token):
        # 初始化 LineBotApi
        self.line_bot_api = LineBotApi(token)
        
        # 配置 Gemini AI
        genai.configure(api_key='AIzaSyA8--HjDOqj7LXf3u4EHUGeIkKZEtf1nKI')
        self.model = genai.GenerativeModel('gemini-pro')
        
        # 初始化 Firebase
        self.fdb = firebase.FirebaseApplication('https://gemini-b0270-default-rtdb.firebaseio.com/', None)
        self.user_chat_path = f'chat/{event.source.user_id}'
        
        self.handle_event(event)

    def handle_event(self, event):
        reply_token = event.reply_token
        chatgpt = self.fdb.get(self.user_chat_path, None)
        
        # 處理文字訊息
        if isinstance(event.message, TextMessage):
            user_message = event.message.text
            
            if chatgpt is None:
                messages = []
            else:
                messages = chatgpt

            if user_message == '!清空':
                reply_msg = TextSendMessage(text='對話歷史紀錄已經清空！')
                self.fdb.delete(self.user_chat_path, None)
            elif user_message == '理財規劃書':
                response_text = (
                    "請提供您的基本資料：\n"
                    "1. 年齡:\n"
                    "2. 月收入:\n"
                    "3. 預計退休年齡:\n"
                    "4. 存款:\n"
                    "5. 財務目標(夢想):"
                )
                reply_msg = TextSendMessage(text=response_text)
            else:
                is_valid, message, extracted_data = self.validate_and_extract_input(user_message)
                if not is_valid:
                    self.line_bot_api.reply_message(reply_token, TextSendMessage(text=f"回傳資料格式錯誤: {message}"))
                    return
                user_data = extracted_data  # 正確時存取extracted_data
                messages.append({'role': 'user', 'parts': [user_message]})
                prompt = self.generate_financial_plan_prompt(user_data)
                response = self.model.generate_content([{'role': 'user', 'parts': [{'text': prompt}]}])
                messages.append({'role': 'model', 'parts': [response.text]})
                reply_msg = TextSendMessage(text=response.text)
                
                # 更新 firebase 中的對話紀錄
                self.fdb.put_async(self.user_chat_path, None, messages)
            # 回覆訊息
            self.line_bot_api.reply_message(reply_token, reply_msg)

    def validate_and_extract_input(self, input_text):
        # 定義每一項的正則表達式模式
        patterns = {
            "age": r"1\.年齡:\s*(\d+)",
            "monthly_income": r"2\.月收入:\s*(\d+)",
            "retirement_age": r"3\.預計退休年齡:\s*(\d+)",
            "savings": r"4\.存款:\s*(\d+)",
            "goal": r"5\.財務目標\(夢想\):\s*(.+)"
        }
        
        extracted_data = {}
        
        # 檢查每一項是否存在且格式正確
        for key, pattern in patterns.items():
            match = re.search(pattern, input_text)
            if not match:
                return False, f"缺少或格式錯誤: {key}", {}
            extracted_data[key] = match.group(1)
        
        # 將數字轉換為整數
        extracted_data['age'] = int(extracted_data['age'])
        extracted_data['monthly_income'] = int(extracted_data['monthly_income'])
        extracted_data['retirement_age'] = int(extracted_data['retirement_age'])
        extracted_data['savings'] = int(extracted_data['savings'])
        
        return True, "所有項目都已正確填寫", extracted_data

    def generate_financial_plan_prompt(self, user_data):
        # 判斷資產等級
        asset_level = self.determine_asset_level(user_data)

        # 生成理財規劃建議的 prompt
        if asset_level == 'low':
            prompt = self.generate_low_asset_prompt(user_data)
        elif asset_level == 'middle':
            prompt = self.generate_middle_asset_prompt(user_data)
        elif asset_level == 'high':
            prompt = self.generate_high_asset_prompt(user_data)

        return prompt

    def determine_asset_level(self, user_data):
        # 模擬資產等級的判斷邏輯
        if user_data['savings'] < 500000:
            return 'low'
        elif user_data['savings'] < 2000000:
            return 'middle'
        else:
            return 'high'

    def generate_low_asset_prompt(self, user_data):
        monthly_savings_needed = self.calculate_monthly_savings(user_data)
        prompt = (
            f"你將做為一個擁有CFP執照的理財規劃師，請收集客戶的基本資料（年齡、月收入、預計退休年齡等）。\n"
            f"收集客戶的財務資料（存款等）。了解客戶的財務目標(夢想)來完成理財的規劃。\n\n"
            f"客戶資料如下：\n"
            f"年齡：{user_data['age']}歲\n"
            f"月收入：{user_data['monthly_income']}元\n"
            f"預計退休年齡：{user_data['retirement_age']}歲\n"
            f"現有存款：{user_data['savings']}元\n"
            f"財務目標：{user_data['goal']}\n\n"
            f"請使用6(生活開銷等於月收入*0.6)/3(投資與儲蓄等於月收入*0.3)/1(保險等於月收入*0.1)的原則分配客戶的收入。\n"
            # f"例如：如果客戶的月收入為 {user_data['monthly_income']} 元，\n"
            # f"則每月花 {user_data['monthly_income'] * 0.6} 元在生活開銷上，\n"
            # f"每月儲蓄與投資 {user_data['monthly_income'] * 0.3} 元，\n"
            # f"每月花 {user_data['monthly_income'] * 0.1} 元在保險上。\n"
            f"為了實現客戶的財務目標 {user_data['goal']}，\n"
            f"客戶需要每年儲蓄 {monthly_savings_needed} 元。\n"
            f"請在投資規劃中提到'使用我們的 LINE Bot 輔助投資策略'來達成客戶的財務目標。"
        )
        return prompt

    def generate_middle_asset_prompt(self, user_data):
        monthly_savings_needed = self.calculate_monthly_savings(user_data)
        prompt = (
            f"你將做為一個擁有CFP執照的理財規劃師，請收集客戶的基本資料（年齡、月收入、預計退休年齡等）。\n"
            f"收集客戶的財務資料（存款等）。了解客戶的財務目標(夢想)來完成理財的規劃。\n\n"
            f"客戶資料如下：\n"
            f"年齡：{user_data['age']}歲\n"
            f"月收入：{user_data['monthly_income']}元\n"
            f"預計退休年齡：{user_data['retirement_age']}歲\n"
            f"現有存款：{user_data['savings']}元\n"
            f"財務目標：{user_data['goal']}\n\n"
            f"請使用4(生活開銷等於月收入*0.4)/4(投資與儲蓄等於月收入*0.4)/2(保險等於月收入*0.2)的原則分配客戶的收入。\n"
            # f"例如：如果客戶的月收入為 {user_data['monthly_income']} 元，\n"
            # f"則每月花 {user_data['monthly_income'] * 0.4} 元在生活開銷上，\n"
            # f"每月儲蓄與投資 {user_data['monthly_income'] * 0.4} 元，\n"
            # f"每月花 {user_data['monthly_income'] * 0.2} 元在保險上。\n"
            f"記得不要因收入增加而讓生活開銷變大。\n"
            f"為了實現客戶的財務目標 {user_data['goal']}，\n"
            f"客戶需要每年儲蓄 {monthly_savings_needed} 元。\n"
            f"請在投資規劃中提到'使用我們的 LINE Bot 輔助投資策略'來達成客戶的財務目標。"
        )
        return prompt

    def generate_high_asset_prompt(self, user_data):
        monthly_savings_needed = self.calculate_monthly_savings(user_data)
        prompt = (
            f"你將做為一個擁有CFP執照的理財規劃師，請收集客戶的基本資料（年齡、月收入、預計退休年齡等）。\n"
            f"收集客戶的財務資料（存款等）。了解客戶的財務目標(夢想)來完成理財的規劃。\n\n"
            f"客戶資料如下：\n"
            f"年齡：{user_data['age']}歲\n"
            f"月收入：{user_data['monthly_income']}元\n"
            f"預計退休年齡：{user_data['retirement_age']}歲\n"
            f"現有存款：{user_data['savings']}元\n"
            f"財務目標：{user_data['goal']}\n\n"
            f"請使用保險的規劃來合法節稅。\n"
             f"請使用3(生活開銷等於月收入*0.3)/5(投資與儲蓄等於月收入*0.5)/2(保險等於月收入*0.2)的原則分配客戶的收入。\n"
            # f"例如：如果客戶的月收入為 {user_data['monthly_income']} 元，\n"
            # f"則每月花 {user_data['monthly_income'] * 0.4} 元在生活開銷上，\n"
            # f"每月儲蓄與投資 {user_data['monthly_income'] * 0.4} 元，\n"
            # f"每月花 {user_data['monthly_income'] * 0.2} 元在保險上。\n"
            f"記得不要因收入增加而讓生活開銷變大。\n"
            f"為了實現客戶的財務目標 {user_data['goal']}，\n"
            f"客戶需要每年儲蓄 {monthly_savings_needed} 元。\n"
            f"請在投資規劃中提到'使用我們的 LINE Bot 輔助投資策略'來達成客戶的財務目標。"
        )
        return prompt

    def calculate_monthly_savings(self, user_data):
        # 假設的儲蓄計算邏輯
        years_to_save = user_data['retirement_age'] - user_data['age']
        total_savings_needed = 1000000  # 根據夢想計算
        monthly_savings_needed = total_savings_needed / (years_to_save * 12)
        return monthly_savings_needed

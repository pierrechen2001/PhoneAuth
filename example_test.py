"""
API 測試工具（API Testing Tool）

【用途說明】
這是一個專門用於測試手機驗證 API 的測試工具。
它會直接呼叫後端 API 端點，模擬前端發送請求的行為，用來驗證 API 是否正常運作。

【主要功能】
1. 測試 API 端點是否正常運作
2. 驗證 API 回應格式是否正確
3. 測試錯誤處理機制（Rate Limiting、錯誤次數限制等）
4. 驗證輸入格式驗證是否正確
5. 提供視覺化的測試結果報告

【使用場景】
- 開發時快速測試 API 功能
- 驗證 API 是否符合規格
- 除錯 API 問題
- 作為 API 使用範例參考

【與前端的差異】
- 前端：使用 Firebase JS SDK 在前端完成 OTP 發送與驗證
- 此工具：直接呼叫後端 API，模擬 API 請求流程
- 此工具：不需要 Firebase JS SDK，純粹測試後端 API 邏輯

【測試涵蓋範圍】
1. 發送 OTP（對應 phone_auth/views.py -> send_otp()）
2. Rate Limiting 測試（對應 phone_auth/views.py -> send_otp()）
3. 驗證 OTP（對應 phone_auth/views.py -> verify_otp()）
4. 重新發送 OTP（對應 phone_auth/views.py -> resend_otp()）
5. 格式驗證測試（對應 phone_auth/serializers.py）

【執行方式】
python example_test.py

【注意事項】
- 需要先啟動 Django 伺服器：python manage.py runserver
- 需要建立測試使用者帳號
- 此工具僅測試後端 API，實際的 OTP 發送需在前端使用 Firebase JS SDK
"""

import requests
import time
import sys

# ===== 設定 =====
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "testuser"  # 替換為你的使用者名稱
PASSWORD = "testpass"  # 替換為你的密碼

# 測試手機號碼（建議使用 Firebase 測試號碼）
COUNTRY_CODE = "+886"
PHONE_NUMBER = "987654321"

# 顏色輸出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_step(message):
    """顯示測試步驟"""
    print(f"{Colors.CYAN}▶ {message}{Colors.END}")

def print_file_ref(file_path, function_name=None):
    """顯示對應的檔案和函式參考"""
    if function_name:
        print(f"{Colors.MAGENTA}📁 對應檔案: {file_path} -> {function_name}(){Colors.END}")
    else:
        print(f"{Colors.MAGENTA}📁 對應檔案: {file_path}{Colors.END}")

def print_api_endpoint(method, endpoint):
    """顯示 API 端點資訊"""
    print(f"{Colors.BOLD}🔗 API: {method} {endpoint}{Colors.END}")

def print_section(title, subtitle=None):
    """顯示測試區塊標題"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.END}")
    if subtitle:
        print(f"{Colors.BLUE}{subtitle:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")

def print_progress(current, total, test_name):
    """顯示測試進度"""
    percentage = int((current / total) * 100)
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\n{Colors.BOLD}[{bar}] 測試 {current}/{total} ({percentage}%) - {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{'─' * 70}{Colors.END}\n")

# ===== 測試函數 =====

def test_send_otp():
    """
    測試發送 OTP 驗證碼
    
    測試目標：
    - 驗證 API 端點：POST /auth/phone/send-otp/
    - 對應函式：phone_auth/views.py -> send_otp()
    - 對應 Serializer：phone_auth/serializers.py -> SendOTPSerializer
    
    測試內容：
    1. 發送正確格式的手機號碼
    2. 檢查後端正確記錄狀態
    3. 驗證回傳的狀態碼和訊息
    """
    print_section("測試 1: 發送 OTP 驗證碼", "POST /auth/phone/send-otp/")
    
    # 顯示對應的檔案和函式
    print_file_ref("phone_auth/views.py", "send_otp")
    print_api_endpoint("POST", "/auth/phone/send-otp/")
    print_file_ref("phone_auth/serializers.py", "SendOTPSerializer")
    print()
    
    url = f"{BASE_URL}/auth/phone/send-otp/"
    data = {
        "country_code": COUNTRY_CODE,
        "phone_number": PHONE_NUMBER
    }
    
    print_step(f"步驟 1: 準備請求資料")
    print_info(f"  國碼: {COUNTRY_CODE}")
    print_info(f"  手機號碼: {PHONE_NUMBER}")
    print_info(f"  完整號碼: {COUNTRY_CODE}{PHONE_NUMBER}")
    print()
    
    print_step(f"步驟 2: 發送 POST 請求到 {url}")
    print_info("  使用 Basic Authentication")
    print_info(f"  使用者: {USERNAME}")
    print()
    
    try:
        response = requests.post(
            url,
            json=data,
            auth=(USERNAME, PASSWORD)
        )
        
        print_step("步驟 3: 檢查回應")
        print_info(f"HTTP 狀態碼: {response.status_code}")
        
        response_data = response.json()
        print_info(f"回應內容: {response_data}")
        print()
        
        if response.status_code == 200:
            print_success("✓ OTP 發送請求成功！")
            print_info(f"  狀態: {response_data.get('status', 'N/A')}")
            print_info(f"  訊息: {response_data.get('message', 'N/A')}")
            if 'expires_in' in response_data:
                print_info(f"  有效期限: {response_data['expires_in']} 秒")
            print()
            print_warning("⚠ 注意：實際的 OTP 發送需在前端使用 Firebase JS SDK 完成")
            print_warning("  此 API 主要用於記錄後端狀態")
            return True
        else:
            print_error("✗ OTP 發送請求失敗")
            print_error(f"  錯誤訊息: {response_data.get('message', 'N/A')}")
            if 'details' in response_data:
                print_error(f"  詳細錯誤: {response_data['details']}")
            return False
            
    except Exception as e:
        print_error(f"✗ 發生未預期的錯誤: {str(e)}")
        print_error(f"  錯誤類型: {type(e).__name__}")
        return False


def test_rate_limiting():
    """
    測試 Rate Limiting（頻率限制）
    
    測試目標：
    - 驗證 API 端點：POST /auth/phone/send-otp/
    - 對應函式：phone_auth/views.py -> send_otp()
    - 檢查 Rate Limiting 邏輯（60 秒限制）
    
    測試內容：
    1. 發送第一次 OTP 請求（應該成功）
    2. 立即發送第二次請求（應該被限制，返回 429）
    3. 驗證 retry_after 欄位
    """
    print_section("測試 2: Rate Limiting 測試", "60 秒內限制重複請求")
    
    # 顯示對應的檔案和函式
    print_file_ref("phone_auth/views.py", "send_otp")
    print_api_endpoint("POST", "/auth/phone/send-otp/")
    print_info("後端邏輯：檢查 last_otp_sent_at 欄位，60 秒內限制重複請求")
    print()
    
    url = f"{BASE_URL}/auth/phone/send-otp/"
    data = {
        "country_code": COUNTRY_CODE,
        "phone_number": PHONE_NUMBER
    }
    
    try:
        # 第一次請求（應該成功）
        print_step("步驟 1: 發送第一次 OTP 請求")
        print_info("  預期結果：成功（200 OK）")
        print()
        
        response1 = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
        print_info(f"  狀態碼: {response1.status_code}")
        
        if response1.status_code == 200:
            print_success("  ✓ 第一次請求成功")
        else:
            print_warning(f"  ⚠ 第一次請求狀態異常: {response1.status_code}")
        print()
        
        # 立即發送第二次請求（應該被限制）
        print_step("步驟 2: 立即發送第二次請求（測試 Rate Limiting）")
        print_info("  預期結果：被限制（429 Too Many Requests）")
        print_warning("  注意：如果第一次請求也失敗，此測試可能無法正確驗證")
        print()
        
        time.sleep(1)  # 稍微等待一下，避免請求過快
        
        response2 = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
        response2_data = response2.json()
        
        print_info(f"  狀態碼: {response2.status_code}")
        print_info(f"  回應內容: {response2_data}")
        print()
        
        if response2.status_code == 429:
            print_success("✓ Rate Limiting 運作正常！")
            retry_after = response2_data.get('retry_after', 60)
            print_info(f"  需要等待: {retry_after} 秒")
            print_info(f"  狀態: {response2_data.get('status', 'N/A')}")
            print_info(f"  訊息: {response2_data.get('message', 'N/A')}")
            print()
            print_warning("⚠ 提示：60 秒後才能再次發送 OTP")
            return True
        else:
            print_warning("⚠ Rate Limiting 可能未正常運作")
            print_warning(f"  預期狀態碼: 429")
            print_warning(f"  實際狀態碼: {response2.status_code}")
            print()
            print_info("  可能原因：")
            print_info("  1. 第一次請求失敗，沒有記錄 last_otp_sent_at")
            print_info("  2. 時間間隔超過 60 秒")
            print_info("  3. Rate Limiting 邏輯未正確實作")
            return False
            
    except Exception as e:
        print_error(f"✗ 發生錯誤: {str(e)}")
        print_error(f"  錯誤類型: {type(e).__name__}")
        return False


def test_verify_otp_invalid():
    """
    測試驗證無效的 OTP（錯誤次數限制）
    
    測試目標：
    - 驗證 API 端點：POST /auth/phone/verify-otp/
    - 對應函式：phone_auth/views.py -> verify_otp()
    - 對應 Serializer：phone_auth/serializers.py -> VerifyOTPSerializer
    - 檢查錯誤次數限制邏輯（最多 3 次）
    
    測試內容：
    1. 連續輸入錯誤的驗證碼（最多 3 次）
    2. 檢查每次失敗後剩餘嘗試次數
    3. 驗證達到 3 次後是否被鎖定（LOCKED）
    """
    print_section("測試 3: 驗證無效的 OTP", "錯誤次數限制測試（最多 3 次）")
    
    # 顯示對應的檔案和函式
    print_file_ref("phone_auth/views.py", "verify_otp")
    print_api_endpoint("POST", "/auth/phone/verify-otp/")
    print_file_ref("phone_auth/serializers.py", "VerifyOTPSerializer")
    print_info("後端邏輯：檢查 otp_attempts 欄位，達到 3 次後鎖定")
    print()
    
    url = f"{BASE_URL}/auth/phone/verify-otp/"
    
    print_warning("⚠ 重要提示：")
    print_warning("  此測試會模擬輸入錯誤的 6 位驗證碼")
    print_warning("  連續錯誤 3 次後帳號會被鎖定（LOCKED）")
    print_warning("  鎖定後需要重新發送 OTP 才能解鎖")
    print()
    
    for attempt in range(1, 4):
        print_step(f"嘗試 {attempt}/3: 輸入錯誤的驗證碼")
        
        data = {
            "verification_id": "test_invalid_id",
            "otp_code": "000000"  # 錯誤的 6 位驗證碼
        }
        
        print_info(f"  驗證碼: {data['otp_code']} (錯誤的驗證碼)")
        print_info(f"  Verification ID: {data['verification_id']}")
        print()
        
        try:
            response = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
            response_data = response.json()
            
            print_info(f"  HTTP 狀態碼: {response.status_code}")
            print_info(f"  回應內容: {response_data}")
            print()
            
            if response.status_code == 403:
                print_warning("⚠ 帳號已被鎖定！")
                print_info(f"  狀態: {response_data.get('status', 'N/A')}")
                print_info(f"  訊息: {response_data.get('message', 'N/A')}")
                print()
                print_warning("  需要重新發送 OTP 來解鎖帳號")
                break
            elif response.status_code == 400:
                remaining = response_data.get('remaining_attempts', 0)
                print_warning(f"  ⚠ 驗證失敗，剩餘 {remaining} 次機會")
                print_info(f"  狀態: {response_data.get('status', 'N/A')}")
                print_info(f"  訊息: {response_data.get('message', 'N/A')}")
            else:
                print_info(f"  狀態: {response_data.get('status', 'N/A')}")
            
            print()
            time.sleep(1)  # 避免請求過快
            
        except Exception as e:
            print_error(f"  ✗ 發生錯誤: {str(e)}")
            print_error(f"    錯誤類型: {type(e).__name__}")
            break
    
    print_step("測試完成")
    print_info("✓ 已測試錯誤次數限制機制")
    print_warning("⚠ 如果帳號被鎖定，請使用 test_resend_otp() 來解鎖")
    return True


def test_resend_otp():
    """
    測試重新發送 OTP
    
    測試目標：
    - 驗證 API 端點：POST /auth/phone/resend-otp/
    - 對應函式：phone_auth/views.py -> resend_otp()
    - 對應 Serializer：phone_auth/serializers.py -> ResendOTPSerializer
    
    測試內容：
    1. 重新發送 OTP 到指定手機號碼
    2. 檢查 Rate Limiting（60 秒限制）
    3. 驗證錯誤次數是否重置
    """
    print_section("測試 4: 重新發送 OTP", "POST /auth/phone/resend-otp/")
    
    # 顯示對應的檔案和函式
    print_file_ref("phone_auth/views.py", "resend_otp")
    print_api_endpoint("POST", "/auth/phone/resend-otp/")
    print_file_ref("phone_auth/serializers.py", "ResendOTPSerializer")
    print_info("後端邏輯：重新發送 OTP，重置 otp_attempts，解除 LOCKED 狀態")
    print()
    
    url = f"{BASE_URL}/auth/phone/resend-otp/"
    full_phone = f"{COUNTRY_CODE}{PHONE_NUMBER}"
    data = {
        "phone_number": full_phone
    }
    
    print_step("步驟 1: 準備重新發送請求")
    print_info(f"  完整手機號碼: {full_phone}")
    print()
    
    print_step("步驟 2: 發送 POST 請求")
    print_info("  預期結果：成功（200 OK）或 Rate Limited（429）")
    print()
    
    try:
        response = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
        response_data = response.json()
        
        print_step("步驟 3: 檢查回應")
        print_info(f"  HTTP 狀態碼: {response.status_code}")
        print_info(f"  回應內容: {response_data}")
        print()
        
        if response.status_code == 200:
            print_success("✓ OTP 重新發送成功！")
            print_info(f"  狀態: {response_data.get('status', 'N/A')}")
            print_info(f"  訊息: {response_data.get('message', 'N/A')}")
            if 'retry_after' in response_data:
                print_info(f"  下次可重發時間: {response_data['retry_after']} 秒後")
            print()
            print_success("  ✓ 錯誤次數已重置")
            print_success("  ✓ 帳號已解鎖（如果之前被鎖定）")
            return True
        elif response.status_code == 429:
            retry_after = response_data.get('retry_after', 60)
            print_warning("⚠ 請求過於頻繁（Rate Limited）")
            print_info(f"  狀態: {response_data.get('status', 'N/A')}")
            print_info(f"  訊息: {response_data.get('message', 'N/A')}")
            print_warning(f"  ⚠ 需等待 {retry_after} 秒後才能再次發送")
            print()
            print_info("  這是正常的 Rate Limiting 行為")
            return False
        else:
            print_error("✗ 重新發送失敗")
            print_error(f"  錯誤訊息: {response_data.get('message', 'N/A')}")
            if 'details' in response_data:
                print_error(f"  詳細錯誤: {response_data['details']}")
            return False
            
    except Exception as e:
        print_error(f"✗ 發生錯誤: {str(e)}")
        print_error(f"  錯誤類型: {type(e).__name__}")
        return False


def test_invalid_phone_format():
    """
    測試無效的手機號碼格式驗證
    
    測試目標：
    - 驗證 API 端點：POST /auth/phone/send-otp/
    - 對應 Serializer：phone_auth/serializers.py -> SendOTPSerializer
    - 檢查格式驗證邏輯（RegexValidator）
    
    測試內容：
    1. 測試缺少 + 號的國碼
    2. 測試包含字母的手機號碼
    3. 測試號碼太短的情況
    """
    print_section("測試 5: 無效的手機號碼格式驗證", "格式驗證測試")
    
    # 顯示對應的檔案和函式
    print_file_ref("phone_auth/serializers.py", "SendOTPSerializer")
    print_api_endpoint("POST", "/auth/phone/send-otp/")
    print_info("後端邏輯：使用 RegexValidator 驗證格式")
    print()
    
    url = f"{BASE_URL}/auth/phone/send-otp/"
    
    invalid_cases = [
        {
            "country_code": "886", 
            "phone_number": "987654321", 
            "reason": "缺少 + 號",
            "expected_error": "國碼格式錯誤，應為 +1 到 +999"
        },
        {
            "country_code": "+886", 
            "phone_number": "abc", 
            "reason": "包含字母",
            "expected_error": "手機號碼格式錯誤，應為 7-15 位數字"
        },
        {
            "country_code": "+886", 
            "phone_number": "123", 
            "reason": "號碼太短",
            "expected_error": "手機號碼格式錯誤，應為 7-15 位數字"
        },
    ]
    
    print_info(f"將測試 {len(invalid_cases)} 個無效格式案例")
    print()
    
    passed_cases = 0
    
    for idx, case in enumerate(invalid_cases, 1):
        print_step(f"測試案例 {idx}/{len(invalid_cases)}: {case['reason']}")
        print_info(f"  國碼: {case['country_code']}")
        print_info(f"  手機號碼: {case['phone_number']}")
        print_info(f"  預期錯誤: {case['expected_error']}")
        print()
        
        data = {
            "country_code": case["country_code"],
            "phone_number": case["phone_number"]
        }
        
        try:
            response = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
            response_data = response.json()
            
            print_info(f"  HTTP 狀態碼: {response.status_code}")
            print_info(f"  回應內容: {response_data}")
            print()
            
            if response.status_code == 400:
                print_success(f"  ✓ 正確拒絕了無效格式")
                error_msg = response_data.get('message', '')
                if 'details' in response_data:
                    print_info(f"  錯誤訊息: {error_msg}")
                    print_info(f"  詳細錯誤: {response_data['details']}")
                else:
                    print_info(f"  錯誤訊息: {error_msg}")
                passed_cases += 1
            else:
                print_warning(f"  ⚠ 未正確驗證格式")
                print_warning(f"  預期狀態碼: 400")
                print_warning(f"  實際狀態碼: {response.status_code}")
                
            print()
                
        except Exception as e:
            print_error(f"  ✗ 發生錯誤: {str(e)}")
            print_error(f"    錯誤類型: {type(e).__name__}")
            print()
    
    print_step("測試完成")
    print_info(f"✓ 通過 {passed_cases}/{len(invalid_cases)} 個格式驗證測試")
    
    if passed_cases == len(invalid_cases):
        print_success("✓ 所有格式驗證測試通過！")
    else:
        print_warning(f"⚠ {len(invalid_cases) - passed_cases} 個測試未通過預期")
    
    return True


def check_api_availability():
    """
    檢查 API 是否可用
    
    測試目標：
    - 檢查 API 伺服器是否正在運行
    - 驗證 API 文件端點是否可訪問
    """
    print_section("前置檢查: API 伺服器可用性", "確認伺服器正在運行")
    
    print_step("步驟 1: 檢查 API 伺服器連線")
    print_info(f"  目標 URL: {BASE_URL}")
    print_info(f"  檢查端點: /api/docs/")
    print()
    
    try:
        print_step("步驟 2: 發送 GET 請求到 API 文件頁面")
        response = requests.get(f"{BASE_URL}/api/docs/", timeout=5)
        
        print_info(f"  HTTP 狀態碼: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print_success("✓ API 伺服器正在運行")
            print_info("  伺服器狀態: 正常")
            print_info(f"  API 文件: {BASE_URL}/api/docs/")
            print()
            return True
        else:
            print_error("✗ API 伺服器回應異常")
            print_error(f"  狀態碼: {response.status_code}")
            print_warning("  請檢查伺服器是否正常運行")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("✗ 無法連接到 API 伺服器")
        print_error("  連線錯誤: Connection refused")
        print()
        print_warning("⚠ 解決方法：")
        print_warning("  1. 確認伺服器正在運行")
        print_warning("  2. 執行指令: python manage.py runserver")
        print_warning("  3. 檢查 BASE_URL 設定是否正確")
        return False
        
    except Exception as e:
        print_error(f"✗ 發生錯誤: {str(e)}")
        print_error(f"  錯誤類型: {type(e).__name__}")
        return False


# ===== 主程式 =====

def main():
    """
    執行所有測試
    
    測試流程：
    1. 檢查 API 伺服器可用性
    2. 執行 5 個主要測試案例
    3. 顯示測試摘要和結果
    """
    # 顯示程式標題
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'手機驗證 API 測試程式':^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")
    
    # 顯示測試設定
    print_section("測試設定", "配置資訊")
    print_info(f"目標 API: {BASE_URL}")
    print_info(f"測試使用者: {USERNAME}")
    print_info(f"測試手機號碼: {COUNTRY_CODE}{PHONE_NUMBER}")
    print_info(f"完整手機號碼: {COUNTRY_CODE}{PHONE_NUMBER}")
    print()
    print_warning("⚠ 注意：請確保以上設定正確，否則測試可能失敗")
    print()
    
    # 檢查 API 是否可用
    print()
    if not check_api_availability():
        print()
        print_error("✗ 測試中止：API 伺服器未運行")
        print()
        print_warning("請先啟動伺服器：")
        print_warning("  python manage.py runserver")
        print()
        return
    
    print()
    print_section("開始執行測試", "將執行 5 個測試案例")
    
    # 執行測試
    tests = [
        ("測試 1: 發送 OTP", test_send_otp),
        ("測試 2: Rate Limiting", test_rate_limiting),
        ("測試 3: 驗證錯誤處理", test_verify_otp_invalid),
        ("測試 4: 重新發送 OTP", test_resend_otp),
        ("測試 5: 無效格式驗證", test_invalid_phone_format),
    ]
    
    total_tests = len(tests)
    results = []
    
    print_info(f"將執行 {total_tests} 個測試案例")
    print()
    
    for idx, (test_name, test_func) in enumerate(tests, 1):
        # 顯示進度
        print_progress(idx, total_tests, test_name)
        
        try:
            result = test_func()
            results.append((test_name, result))
            print()
            
            # 測試之間暫停
            if idx < total_tests:
                print_info("等待 2 秒後繼續下一個測試...")
                time.sleep(2)
                print()
                
        except KeyboardInterrupt:
            print_warning("\n\n⚠ 測試被使用者中斷")
            print_info("已完成的測試結果仍會顯示在摘要中")
            break
        except Exception as e:
            print_error(f"✗ 測試 '{test_name}' 發生未預期的錯誤: {str(e)}")
            print_error(f"  錯誤類型: {type(e).__name__}")
            results.append((test_name, False))
            print()
    
    # 顯示測試摘要
    print_section("測試摘要", "最終結果")
    
    print_info("測試結果：")
    print()
    
    for test_name, result in results:
        if result:
            print_success(f"  ✓ {test_name}: 通過")
        else:
            print_error(f"  ✗ {test_name}: 失敗")
    
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = int((passed / total) * 100) if total > 0 else 0
    
    # 顯示統計
    print_step("測試統計")
    print_info(f"  總測試數: {total}")
    print_info(f"  通過: {passed}")
    print_info(f"  失敗: {total - passed}")
    print_info(f"  通過率: {percentage}%")
    print()
    
    if passed == total:
        print_success(f"✓ 所有測試通過！({passed}/{total})")
    else:
        print_warning(f"⚠ 部分測試失敗 ({passed}/{total} 通過)")
    
    print()
    
    # 重要提示
    print_section("重要提示", "使用注意事項")
    print_warning("1. 認證方式：此測試使用 Basic Authentication")
    print_warning("   請確保使用者帳號存在且密碼正確")
    print()
    print_warning("2. 帳號鎖定：連續錯誤測試後帳號會被鎖定")
    print_warning("   鎖定後需重新發送 OTP 來解鎖")
    print()
    print_warning("3. Rate Limiting：測試之間需要等待 60 秒")
    print_warning("   如果收到 429 錯誤，請等待 60 秒後再試")
    print()
    print_info("4. Firebase 測試：建議使用 Firebase 測試號碼")
    print_info("   可避免真實 SMS 費用")
    print_info("   設定位置：Firebase Console -> Authentication -> Phone -> Testing")
    print()
    print_info("5. 完整文件：")
    print_info("   - README.md: 完整使用說明")
    print_info("   - guides/API_TESTING_GUIDE.md: API 測試指南")
    print_info("   - API 文件: http://127.0.0.1:8000/api/docs/")
    print()
    
    print_section("測試完成", "感謝使用！")


if __name__ == "__main__":
    main()


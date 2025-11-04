"""
API 測試範例

此檔案提供完整的 Python 測試範例，可以直接執行。
"""

import requests
import time

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
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}\n")

# ===== 測試函數 =====

def test_send_otp():
    """測試發送 OTP"""
    print_section("測試 1: 發送 OTP")
    
    url = f"{BASE_URL}/auth/phone/send-otp/"
    data = {
        "country_code": COUNTRY_CODE,
        "phone_number": PHONE_NUMBER
    }
    
    try:
        response = requests.post(
            url,
            json=data,
            auth=(USERNAME, PASSWORD)
        )
        
        print_info(f"狀態碼: {response.status_code}")
        print_info(f"回應: {response.json()}")
        
        if response.status_code == 200:
            print_success("OTP 發送成功！")
            return True
        else:
            print_error("OTP 發送失敗")
            return False
            
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        return False


def test_rate_limiting():
    """測試 Rate Limiting"""
    print_section("測試 2: Rate Limiting（60 秒限制）")
    
    url = f"{BASE_URL}/auth/phone/send-otp/"
    data = {
        "country_code": COUNTRY_CODE,
        "phone_number": PHONE_NUMBER
    }
    
    try:
        # 第一次請求（應該成功）
        print_info("發送第一次請求...")
        response1 = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
        print_info(f"第一次請求狀態碼: {response1.status_code}")
        
        # 立即發送第二次請求（應該被限制）
        print_info("立即發送第二次請求...")
        time.sleep(1)  # 稍微等待一下
        response2 = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
        print_info(f"第二次請求狀態碼: {response2.status_code}")
        print_info(f"回應: {response2.json()}")
        
        if response2.status_code == 429:
            print_success("Rate Limiting 運作正常！")
            retry_after = response2.json().get('retry_after', 60)
            print_warning(f"需要等待 {retry_after} 秒後才能再次發送")
            return True
        else:
            print_warning("Rate Limiting 可能未正常運作")
            return False
            
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        return False


def test_verify_otp_invalid():
    """測試驗證無效的 OTP（模擬錯誤次數限制）"""
    print_section("測試 3: 驗證無效的 OTP")
    
    url = f"{BASE_URL}/auth/phone/verify-otp/"
    
    print_info("這個測試會模擬輸入錯誤的驗證碼")
    print_warning("注意：連續錯誤 3 次後會被鎖定")
    
    for attempt in range(1, 4):
        print_info(f"\n嘗試 {attempt}/3：輸入錯誤的驗證碼...")
        
        data = {
            "verification_id": "test_invalid_id",
            "otp_code": "000000"  # 錯誤的驗證碼
        }
        
        try:
            response = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
            print_info(f"狀態碼: {response.status_code}")
            print_info(f"回應: {response.json()}")
            
            if response.status_code == 403:
                print_warning("帳號已被鎖定！")
                break
            elif response.status_code == 400:
                remaining = response.json().get('remaining_attempts', 0)
                print_warning(f"驗證失敗，剩餘 {remaining} 次機會")
            
            time.sleep(1)  # 避免請求過快
            
        except Exception as e:
            print_error(f"發生錯誤: {str(e)}")
            break
    
    print_info("\n測試完成")
    print_warning("如果帳號被鎖定，需要重新發送 OTP 來解鎖")
    return True


def test_resend_otp():
    """測試重新發送 OTP"""
    print_section("測試 4: 重新發送 OTP")
    
    url = f"{BASE_URL}/auth/phone/resend-otp/"
    full_phone = f"{COUNTRY_CODE}{PHONE_NUMBER}"
    data = {
        "phone_number": full_phone
    }
    
    try:
        response = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
        
        print_info(f"狀態碼: {response.status_code}")
        print_info(f"回應: {response.json()}")
        
        if response.status_code == 200:
            print_success("OTP 重新發送成功！")
            print_info("錯誤次數已重置，帳號已解鎖")
            return True
        elif response.status_code == 429:
            retry_after = response.json().get('retry_after', 60)
            print_warning(f"請求過於頻繁，需等待 {retry_after} 秒")
            return False
        else:
            print_error("重新發送失敗")
            return False
            
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        return False


def test_invalid_phone_format():
    """測試無效的手機號碼格式"""
    print_section("測試 5: 無效的手機號碼格式")
    
    url = f"{BASE_URL}/auth/phone/send-otp/"
    
    invalid_cases = [
        {"country_code": "886", "phone_number": "987654321", "reason": "缺少 + 號"},
        {"country_code": "+886", "phone_number": "abc", "reason": "包含字母"},
        {"country_code": "+886", "phone_number": "123", "reason": "號碼太短"},
    ]
    
    for case in invalid_cases:
        print_info(f"\n測試案例: {case['reason']}")
        print_info(f"資料: {case['country_code']} {case['phone_number']}")
        
        data = {
            "country_code": case["country_code"],
            "phone_number": case["phone_number"]
        }
        
        try:
            response = requests.post(url, json=data, auth=(USERNAME, PASSWORD))
            print_info(f"狀態碼: {response.status_code}")
            
            if response.status_code == 400:
                print_success("正確拒絕了無效格式")
                print_info(f"錯誤訊息: {response.json().get('message', '')}")
            else:
                print_warning("未正確驗證格式")
                
        except Exception as e:
            print_error(f"發生錯誤: {str(e)}")
    
    return True


def check_api_availability():
    """檢查 API 是否可用"""
    print_section("前置檢查: API 可用性")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs/", timeout=5)
        if response.status_code == 200:
            print_success("API 伺服器正在運行")
            return True
        else:
            print_error("API 伺服器回應異常")
            return False
    except requests.exceptions.ConnectionError:
        print_error("無法連接到 API 伺服器")
        print_warning("請確認伺服器正在運行：python manage.py runserver")
        return False
    except Exception as e:
        print_error(f"發生錯誤: {str(e)}")
        return False


# ===== 主程式 =====

def main():
    """執行所有測試"""
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print("手機驗證 API 測試程式")
    print(f"{'=' * 60}{Colors.END}\n")
    
    print_info(f"目標 API: {BASE_URL}")
    print_info(f"測試使用者: {USERNAME}")
    print_info(f"測試手機: {COUNTRY_CODE}{PHONE_NUMBER}\n")
    
    # 檢查 API 是否可用
    if not check_api_availability():
        print_error("\n測試中止：API 伺服器未運行")
        return
    
    # 執行測試
    tests = [
        ("發送 OTP", test_send_otp),
        ("Rate Limiting", test_rate_limiting),
        ("驗證錯誤處理", test_verify_otp_invalid),
        ("重新發送 OTP", test_resend_otp),
        ("無效格式驗證", test_invalid_phone_format),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(2)  # 測試之間稍微暫停
        except KeyboardInterrupt:
            print_warning("\n\n測試被使用者中斷")
            break
        except Exception as e:
            print_error(f"測試 '{test_name}' 發生未預期的錯誤: {str(e)}")
            results.append((test_name, False))
    
    # 顯示測試摘要
    print_section("測試摘要")
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: 通過")
        else:
            print_error(f"{test_name}: 失敗")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{Colors.BLUE}總計: {passed}/{total} 個測試通過{Colors.END}\n")
    
    # 重要提示
    print_section("重要提示")
    print_warning("1. 此測試使用 Basic Authentication，請確保使用者帳號存在")
    print_warning("2. 連續錯誤測試後帳號會被鎖定，需重新發送 OTP 解鎖")
    print_warning("3. Rate Limiting 測試之間需要等待 60 秒")
    print_info("4. 建議使用 Firebase 測試號碼來避免真實 SMS 費用")
    print_info("5. 查看完整文件：README.md")


if __name__ == "__main__":
    main()


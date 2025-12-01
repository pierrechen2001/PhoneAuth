#!/usr/bin/env python3
"""
Phone Auth API 測試腳本

此腳本用於測試手機認證 API 的各項功能。
使用前請先確保已登入並取得 session。

使用方式：
    python test_phone_auth_api.py --url https://ai.akira-dialog.com
"""

import requests
import argparse
import json
from datetime import datetime


class PhoneAuthTester:
    """手機認證 API 測試器"""
    
    def __init__(self, base_url, session_id=None, csrf_token=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # 設定認證
        if session_id:
            self.session.cookies.set('sessionid', session_id)
        if csrf_token:
            self.session.cookies.set('csrftoken', csrf_token)
            self.session.headers.update({'X-CSRFToken': csrf_token})
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def log(self, message, level='INFO'):
        """輸出日誌"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_send_otp(self, country_code='+886', phone_number='987654321'):
        """測試發送 OTP"""
        self.log("測試 send-otp API")
        
        url = f"{self.base_url}/auth/phone/send-otp/"
        data = {
            "country_code": country_code,
            "phone_number": phone_number
        }
        
        try:
            response = self.session.post(url, json=data)
            self.log(f"狀態碼: {response.status_code}")
            self.log(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            return response.status_code == 200, response.json()
        except Exception as e:
            self.log(f"錯誤: {str(e)}", 'ERROR')
            return False, {'error': str(e)}
    
    def test_verify_otp(self, verification_id, otp_code):
        """測試驗證 OTP"""
        self.log("測試 verify-otp API")
        
        url = f"{self.base_url}/auth/phone/verify-otp/"
        data = {
            "verification_id": verification_id,
            "otp_code": otp_code
        }
        
        try:
            response = self.session.post(url, json=data)
            self.log(f"狀態碼: {response.status_code}")
            self.log(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            return response.status_code == 200, response.json()
        except Exception as e:
            self.log(f"錯誤: {str(e)}", 'ERROR')
            return False, {'error': str(e)}
    
    def test_resend_otp(self, phone_number):
        """測試重新發送 OTP"""
        self.log("測試 resend-otp API")
        
        url = f"{self.base_url}/auth/phone/resend-otp/"
        data = {
            "phone_number": phone_number
        }
        
        try:
            response = self.session.post(url, json=data)
            self.log(f"狀態碼: {response.status_code}")
            self.log(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            return response.status_code == 200, response.json()
        except Exception as e:
            self.log(f"錯誤: {str(e)}", 'ERROR')
            return False, {'error': str(e)}
    
    def test_locked_scenario(self):
        """測試鎖定情境（連續失敗 3 次）"""
        self.log("=== 測試鎖定情境 ===", 'TEST')
        
        # 發送 OTP
        success, _ = self.test_send_otp()
        if not success:
            self.log("發送 OTP 失敗，跳過測試", 'WARN')
            return
        
        print("\n")
        
        # 嘗試錯誤驗證 3 次
        for i in range(3):
            self.log(f"第 {i+1} 次錯誤嘗試", 'TEST')
            self.test_verify_otp('fake-token', f'{111111 + i}')
            print("\n")
        
        # 第 4 次應該被鎖定
        self.log("第 4 次嘗試（應該被鎖定）", 'TEST')
        success, response = self.test_verify_otp('fake-token', '444444')
        
        if not success and response.get('status') == 'LOCKED':
            self.log("✅ 鎖定機制正常", 'SUCCESS')
            if 'retry_after' in response:
                self.log(f"✅ retry_after 欄位存在: {response['retry_after']}", 'SUCCESS')
            else:
                self.log("❌ retry_after 欄位不存在", 'ERROR')
        else:
            self.log("❌ 鎖定機制異常", 'ERROR')
    
    def test_rate_limiting(self):
        """測試頻率限制"""
        self.log("=== 測試頻率限制 ===", 'TEST')
        
        # 第一次發送
        self.log("第 1 次發送", 'TEST')
        success1, _ = self.test_send_otp()
        print("\n")
        
        # 立即第二次發送
        self.log("第 2 次發送（應該被限制）", 'TEST')
        success2, response = self.test_send_otp()
        
        if not success2 and response.get('status') == 'TOO_MANY_REQUESTS':
            self.log("✅ 頻率限制正常", 'SUCCESS')
            if 'retry_after' in response:
                self.log(f"✅ retry_after 欄位存在: {response['retry_after']}", 'SUCCESS')
            else:
                self.log("❌ retry_after 欄位不存在", 'ERROR')
        else:
            self.log("❌ 頻率限制異常", 'ERROR')
    
    def test_invalid_phone_format(self):
        """測試錯誤的手機號碼格式"""
        self.log("=== 測試錯誤格式 ===", 'TEST')
        
        # 測試缺少國碼
        self.log("測試：缺少 + 號的國碼", 'TEST')
        self.test_send_otp('886', '987654321')
        print("\n")
        
        # 測試太短的號碼
        self.log("測試：號碼太短", 'TEST')
        self.test_send_otp('+886', '123')
        print("\n")
    
    def interactive_test(self):
        """互動式測試模式"""
        self.log("=== 互動式測試模式 ===", 'TEST')
        
        while True:
            print("\n" + "="*50)
            print("1. 發送 OTP (send-otp)")
            print("2. 驗證 OTP (verify-otp)")
            print("3. 重新發送 OTP (resend-otp)")
            print("4. 測試鎖定情境")
            print("5. 測試頻率限制")
            print("6. 測試錯誤格式")
            print("0. 退出")
            print("="*50)
            
            choice = input("\n請選擇測試項目 (0-6): ").strip()
            
            if choice == '0':
                self.log("退出測試", 'INFO')
                break
            elif choice == '1':
                country_code = input("請輸入國碼 (預設 +886): ").strip() or '+886'
                phone_number = input("請輸入手機號碼 (預設 987654321): ").strip() or '987654321'
                self.test_send_otp(country_code, phone_number)
            elif choice == '2':
                verification_id = input("請輸入 verification_id (idToken): ").strip()
                otp_code = input("請輸入 OTP 代碼: ").strip()
                if verification_id and otp_code:
                    self.test_verify_otp(verification_id, otp_code)
                else:
                    self.log("參數不能為空", 'ERROR')
            elif choice == '3':
                phone_number = input("請輸入完整手機號碼 (例如 +886987654321): ").strip()
                if phone_number:
                    self.test_resend_otp(phone_number)
                else:
                    self.log("手機號碼不能為空", 'ERROR')
            elif choice == '4':
                self.test_locked_scenario()
            elif choice == '5':
                self.test_rate_limiting()
            elif choice == '6':
                self.test_invalid_phone_format()
            else:
                self.log("無效的選項", 'WARN')


def main():
    parser = argparse.ArgumentParser(
        description='Phone Auth API 測試工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  # 互動式測試（推薦）
  python test_phone_auth_api.py --url https://ai.akira-dialog.com --session YOUR_SESSION_ID --csrf YOUR_CSRF_TOKEN
  
  # 快速測試
  python test_phone_auth_api.py --url https://ai.akira-dialog.com --session YOUR_SESSION_ID --csrf YOUR_CSRF_TOKEN --quick
        """
    )
    
    parser.add_argument(
        '--url',
        default='http://127.0.0.1:8000',
        help='API base URL (預設: http://127.0.0.1:8000)'
    )
    parser.add_argument(
        '--session',
        help='Session ID (從瀏覽器 Cookie 取得)'
    )
    parser.add_argument(
        '--csrf',
        help='CSRF Token (從瀏覽器 Cookie 取得)'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='快速測試模式（自動執行所有測試）'
    )
    
    args = parser.parse_args()
    
    # 建立測試器
    tester = PhoneAuthTester(args.url, args.session, args.csrf)
    
    print("=" * 70)
    print(" Phone Auth API 測試工具")
    print("=" * 70)
    print(f"API URL: {args.url}")
    print(f"Session ID: {'已設定' if args.session else '未設定（可能會遇到認證錯誤）'}")
    print(f"CSRF Token: {'已設定' if args.csrf else '未設定'}")
    print("=" * 70)
    print()
    
    if args.quick:
        # 快速測試模式
        tester.log("=== 快速測試模式 ===", 'TEST')
        print("\n")
        
        tester.test_invalid_phone_format()
        print("\n")
        
        # 如果有 session，測試其他功能
        if args.session:
            tester.test_rate_limiting()
            print("\n")
    else:
        # 互動式模式
        tester.interactive_test()


if __name__ == '__main__':
    main()


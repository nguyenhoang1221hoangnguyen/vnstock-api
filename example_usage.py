"""
Ví dụ sử dụng VNStock API
"""
import requests
import json


def print_json(data, title=""):
    """In dữ liệu JSON đẹp"""
    if title:
        print(f"\n{'='*50}")
        print(f"{title}")
        print('='*50)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    base_url = "http://localhost:8000"

    print("VNStock API - Ví dụ sử dụng")
    print("="*50)

    # 1. Health check
    print("\n1. Kiểm tra trạng thái API...")
    response = requests.get(f"{base_url}/health")
    print_json(response.json())

    # 2. Lấy thông tin công ty
    print("\n2. Lấy thông tin công ty VNM...")
    response = requests.get(f"{base_url}/api/stock/VNM/company")
    if response.status_code == 200:
        print_json(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")

    # 3. Lấy dữ liệu giá
    print("\n3. Lấy dữ liệu giá VNM (30 ngày gần nhất)...")
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    response = requests.get(
        f"{base_url}/api/stock/VNM/price",
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Tổng số records: {data['total_records']}")
        print(f"Dữ liệu 3 ngày gần nhất:")
        print_json(data['data'][-3:])
    else:
        print(f"Error: {response.status_code} - {response.text}")

    # 4. Lấy chỉ số kỹ thuật
    print("\n4. Lấy chỉ số kỹ thuật VNM...")
    response = requests.get(
        f"{base_url}/api/stock/VNM/technical",
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    if response.status_code == 200:
        data = response.json()
        indicators = data['indicators']
        print(f"Các chỉ số có sẵn: {list(indicators.keys())}")

        # In RSI
        if 'RSI' in indicators and indicators['RSI']:
            rsi_values = indicators['RSI'].get('RSI', [])
            if rsi_values:
                print(f"\nRSI gần nhất: {rsi_values[-1]:.2f}")

        # In MACD
        if 'MACD' in indicators and indicators['MACD']:
            macd = indicators['MACD']
            if 'MACD' in macd and macd['MACD']:
                print(f"MACD gần nhất: {macd['MACD'][-1]:.2f}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

    # 5. Lấy chỉ số cơ bản
    print("\n5. Lấy chỉ số cơ bản VNM...")
    response = requests.get(f"{base_url}/api/stock/VNM/fundamental")
    if response.status_code == 200:
        data = response.json()
        indicators = data['indicators']
        print(f"\nGiá hiện tại: {data['current_price']:,.0f} VND")
        print(f"\nCác chỉ số cơ bản:")
        for key, value in indicators.items():
            if value is not None:
                print(f"  {key}: {value}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

    # 6. Lấy toàn bộ dữ liệu
    print("\n6. Lấy TOÀN BỘ dữ liệu VNM (30 ngày)...")
    print("(Có thể mất vài giây...)")

    response = requests.get(
        f"{base_url}/api/stock/VNM",
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\nSymbol: {data['symbol']}")
        print(f"Công ty: {data['company_info'].get('company_name', 'N/A')}")
        print(f"Tổng số records giá: {data['metadata']['total_records']}")
        print(f"Giá hiện tại: {data['metadata']['current_price']:,.0f} VND")
        print(f"\nCác chỉ số kỹ thuật có sẵn:")
        for indicator in data['technical_indicators'].keys():
            print(f"  - {indicator}")
        print(f"\nCác chỉ số cơ bản:")
        for key, value in data['fundamental_indicators'].items():
            if value is not None:
                print(f"  {key}: {value}")

        # Lưu toàn bộ dữ liệu vào file
        output_file = f"vnm_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nĐã lưu toàn bộ dữ liệu vào file: {output_file}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nLỗi: Không thể kết nối đến API server.")
        print("Vui lòng đảm bảo server đang chạy tại http://localhost:8000")
        print("\nĐể chạy server:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\nLỗi: {e}")

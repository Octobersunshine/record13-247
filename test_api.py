import requests
import json

BASE_URL = "http://localhost:5000"


def test_query_winning_code():
    """测试查询中签编码"""
    print("=" * 60)
    print("测试1: 查询中签编码")
    print("=" * 60)
    
    winning_codes = ["2024001001", "2024001002", "2024002001"]
    
    for code in winning_codes:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"code": code}
        )
        data = response.json()
        
        print(f"\n查询编码: {code}")
        print(f"状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        assert response.status_code == 200
        assert data["success"] == True
        assert data["won"] == True
        assert data["code"] == code
        assert data["info"] is not None
        assert data["info"]["code"] == code
        
        print(f"✅ 测试通过 - 编码 {code} 确认中签")


def test_query_non_winning_code():
    """测试查询未中签编码"""
    print("\n" + "=" * 60)
    print("测试2: 查询未中签编码")
    print("=" * 60)
    
    non_winning_codes = ["9999999999", "1234567890", "0000000000"]
    
    for code in non_winning_codes:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"code": code}
        )
        data = response.json()
        
        print(f"\n查询编码: {code}")
        print(f"状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        assert response.status_code == 200
        assert data["success"] == True
        assert data["won"] == False
        assert data["code"] == code
        assert data["info"] is None
        
        print(f"✅ 测试通过 - 编码 {code} 确认未中签")


def test_query_empty_code():
    """测试查询空编码"""
    print("\n" + "=" * 60)
    print("测试3: 查询空编码")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": ""}
    )
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    assert response.status_code == 400
    assert data["success"] == False
    
    print("✅ 测试通过 - 空编码正确返回错误")


def test_query_missing_code():
    """测试缺少code参数"""
    print("\n" + "=" * 60)
    print("测试4: 缺少code参数")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={}
    )
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    assert response.status_code == 400
    assert data["success"] == False
    
    print("✅ 测试通过 - 缺少参数正确返回错误")


def test_query_with_spaces():
    """测试带空格的编码"""
    print("\n" + "=" * 60)
    print("测试5: 带空格的编码")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": "  2024001001  "}
    )
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    assert response.status_code == 200
    assert data["success"] == True
    assert data["won"] == True
    assert data["code"] == "2024001001"
    
    print("✅ 测试通过 - 空格被正确去除")


def test_get_all_winners():
    """测试获取所有中签者列表"""
    print("\n" + "=" * 60)
    print("测试6: 获取所有中签者列表")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/winners")
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"中签人数: {data['count']}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    assert response.status_code == 200
    assert data["success"] == True
    assert data["count"] >= 5
    assert len(data["winners"]) == data["count"]
    
    print("✅ 测试通过 - 成功获取所有中签者列表")


def test_crud_winner():
    """测试添加和删除中签者"""
    print("\n" + "=" * 60)
    print("测试7: 添加和删除中签者")
    print("=" * 60)
    
    new_winner = {
        "code": "2024999999",
        "name": "测试用户",
        "plate_number": "京Z99999",
        "lottery_round": "2024年第99期",
        "win_date": "2024-12-15"
    }
    
    print("\n--- 添加新中签者 ---")
    response = requests.post(
        f"{BASE_URL}/api/winners",
        json=new_winner
    )
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    assert response.status_code == 200
    assert data["success"] == True
    
    print("\n--- 验证新中签者可查询 ---")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": "2024999999"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["won"] == True
    assert data["info"]["name"] == "测试用户"
    print("✅ 新中签者可正常查询")
    
    print("\n--- 删除中签者 ---")
    response = requests.delete(f"{BASE_URL}/api/winners/2024999999")
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    assert response.status_code == 200
    assert data["success"] == True
    
    print("\n--- 验证已删除 ---")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": "2024999999"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["won"] == False
    print("✅ 中签者已成功删除")
    
    print("✅ 测试通过 - CRUD操作正常")


def test_webpage():
    """测试网页是否可访问"""
    print("\n" + "=" * 60)
    print("测试8: 网页可访问性")
    print("=" * 60)
    
    response = requests.get(BASE_URL)
    
    print(f"状态码: {response.status_code}")
    print(f"页面标题包含: {'车牌摇号结果查询' in response.text}")
    
    assert response.status_code == 200
    assert "车牌摇号结果查询" in response.text
    
    print("✅ 测试通过 - 网页可正常访问")


if __name__ == "__main__":
    print("🚀 开始运行 API 测试...")
    print("请确保服务已启动: python app.py")
    print()
    
    try:
        test_webpage()
        test_query_winning_code()
        test_query_non_winning_code()
        test_query_empty_code()
        test_query_missing_code()
        test_query_with_spaces()
        test_get_all_winners()
        test_crud_winner()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请先运行: python app.py")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

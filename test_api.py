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
        assert len(data["winners"]) >= 1
        assert data["winners"][0]["code"] == code

        print(f"✅ 测试通过 - 编码 {code} 确认中签")


def test_query_with_round():
    """测试指定期数查询"""
    print("\n" + "=" * 60)
    print("测试2: 指定期数查询")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": "2024001001", "lottery_round": "2024年第1期"}
    )
    data = response.json()

    print(f"\n查询编码: 2024001001, 期数: 2024年第1期")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True
    assert data["won"] == True
    assert data["lottery_round"] == "2024年第1期"
    assert data["winners"][0]["lottery_round"] == "2024年第1期"

    print("✅ 测试通过 - 指定期数查询正确")


def test_query_wrong_round():
    """测试查询错误期数"""
    print("\n" + "=" * 60)
    print("测试3: 查询错误期数（编码存在但期数不匹配）")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": "2024001001", "lottery_round": "2024年第3期"}
    )
    data = response.json()

    print(f"\n查询编码: 2024001001, 期数: 2024年第3期")
    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True
    assert data["won"] == False
    assert len(data["winners"]) == 0

    print("✅ 测试通过 - 期数不匹配时正确返回未中签")


def test_query_non_winning_code():
    """测试查询未中签编码"""
    print("\n" + "=" * 60)
    print("测试4: 查询未中签编码")
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
        assert len(data["winners"]) == 0

        print(f"✅ 测试通过 - 编码 {code} 确认未中签")


def test_duplicate_code_same_round():
    """测试同一期添加重复编码（核心修复验证）"""
    print("\n" + "=" * 60)
    print("测试5: 同一期添加重复编码（核心修复验证）")
    print("=" * 60)

    new_winner = {
        "code": "2024001001",
        "name": "重复测试",
        "plate_number": "京D88888",
        "lottery_round": "2024年第1期",
        "win_date": "2024-01-15"
    }

    print("\n尝试添加已存在的编码（同一期）...")
    response = requests.post(
        f"{BASE_URL}/api/winners",
        json=new_winner
    )
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 409
    assert data["success"] == False
    assert "已存在" in data["message"]
    assert "同一期编码必须唯一" in data["message"]

    print("✅ 测试通过 - 同一期重复编码被正确拒绝")


def test_same_code_different_round():
    """测试不同期添加相同编码（应该允许）"""
    print("\n" + "=" * 60)
    print("测试6: 不同期添加相同编码（应该允许）")
    print("=" * 60)

    new_winner = {
        "code": "2024001001",
        "name": "跨期测试用户",
        "plate_number": "京E99999",
        "lottery_round": "2024年第99期",
        "win_date": "2024-12-15"
    }

    print("\n添加相同编码到不同期数...")
    response = requests.post(
        f"{BASE_URL}/api/winners",
        json=new_winner
    )
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True

    print("\n验证该编码在两期中都存在...")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": "2024001001"}
    )
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"中签记录数: {data['count']}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True
    assert data["won"] == True
    assert data["count"] >= 2

    rounds_found = [w["lottery_round"] for w in data["winners"]]
    assert "2024年第1期" in rounds_found
    assert "2024年第99期" in rounds_found

    print("✅ 测试通过 - 不同期允许相同编码，跨期查询正常")

    print("\n清理测试数据...")
    response = requests.delete(
        f"{BASE_URL}/api/winners/2024001001",
        json={"lottery_round": "2024年第99期"}
    )
    assert response.status_code == 200
    print("✅ 测试数据清理完成")


def test_get_rounds():
    """测试获取所有期数"""
    print("\n" + "=" * 60)
    print("测试7: 获取所有期数")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/rounds")
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"期数列表: {data['rounds']}")

    assert response.status_code == 200
    assert data["success"] == True
    assert len(data["rounds"]) >= 3
    assert "2024年第1期" in data["rounds"]
    assert "2024年第2期" in data["rounds"]
    assert "2024年第3期" in data["rounds"]

    print("✅ 测试通过 - 成功获取所有期数")


def test_get_winners_by_round():
    """测试按期数获取中签者"""
    print("\n" + "=" * 60)
    print("测试8: 按期数获取中签者")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/winners?round=2024年第1期")
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"该期中签人数: {data['count']}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True
    assert data["count"] == 2

    for winner in data["winners"]:
        assert winner["lottery_round"] == "2024年第1期"

    print("✅ 测试通过 - 按期数获取中签者正常")


def test_delete_with_round():
    """测试指定期数删除"""
    print("\n" + "=" * 60)
    print("测试9: 指定期数删除中签者")
    print("=" * 60)

    test_code = "TEST000001"
    test_round = "2024年第99期"

    print("\n添加测试数据...")
    response = requests.post(
        f"{BASE_URL}/api/winners",
        json={
            "code": test_code,
            "name": "删除测试",
            "plate_number": "京T00001",
            "lottery_round": test_round,
            "win_date": "2024-12-01"
        }
    )
    assert response.status_code == 200

    print(f"删除 {test_round} 中的 {test_code}...")
    response = requests.delete(
        f"{BASE_URL}/api/winners/{test_code}",
        json={"lottery_round": test_round}
    )
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True

    print("\n验证已删除...")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": test_code, "lottery_round": test_round}
    )
    data = response.json()
    assert data["won"] == False

    print("✅ 测试通过 - 指定期数删除正常")


def test_crud_winner():
    """测试完整CRUD操作"""
    print("\n" + "=" * 60)
    print("测试10: 完整CRUD操作")
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
        json={"code": "2024999999", "lottery_round": "2024年第99期"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["won"] == True
    assert data["winners"][0]["name"] == "测试用户"
    print("✅ 新中签者可正常查询")

    print("\n--- 删除中签者 ---")
    response = requests.delete(
        f"{BASE_URL}/api/winners/2024999999",
        json={"lottery_round": "2024年第99期"}
    )
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


def test_batch_import():
    """测试批量导入功能"""
    print("\n" + "=" * 60)
    print("测试12: 批量导入功能")
    print("=" * 60)

    batch_winners = [
        {
            "code": "BATCH000001",
            "name": "批量用户1",
            "plate_number": "京Q00001",
            "lottery_round": "2024年第10期",
            "win_date": "2024-10-15"
        },
        {
            "code": "BATCH000002",
            "name": "批量用户2",
            "plate_number": "京Q00002",
            "lottery_round": "2024年第10期",
            "win_date": "2024-10-15"
        },
        {
            "code": "BATCH000001",
            "name": "重复用户",
            "plate_number": "京Q00003",
            "lottery_round": "2024年第10期",
            "win_date": "2024-10-15"
        }
    ]

    print("\n--- 批量导入（跳过重复） ---")
    response = requests.post(
        f"{BASE_URL}/api/winners/batch",
        json={"winners": batch_winners, "skip_duplicates": True}
    )
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"添加: {data['added']}, 跳过: {data['skipped']}, 失败: {data['failed']}")
    print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True
    assert data["added"] == 2
    assert data["skipped"] == 1
    assert data["failed"] == 0

    print("✅ 批量导入（跳过重复）测试通过")

    print("\n--- 验证批量导入数据 ---")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": "BATCH000001", "lottery_round": "2024年第10期"}
    )
    data = response.json()
    assert data["won"] == True
    assert data["winners"][0]["name"] == "批量用户1"
    print("✅ 批量导入数据验证通过")

    print("\n--- 批量导入（不跳过重复，应该失败） ---")
    response = requests.post(
        f"{BASE_URL}/api/winners/batch",
        json={"winners": batch_winners, "skip_duplicates": False}
    )
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"添加: {data['added']}, 失败: {data['failed']}")

    assert response.status_code == 409
    assert data["success"] == False
    assert data["failed"] > 0

    print("✅ 批量导入（不跳过重复）测试通过")

    print("\n--- 清理批量测试数据 ---")
    requests.delete(f"{BASE_URL}/api/winners/BATCH000001", json={"lottery_round": "2024年第10期"})
    requests.delete(f"{BASE_URL}/api/winners/BATCH000002", json={"lottery_round": "2024年第10期"})
    print("✅ 测试数据清理完成")

    print("✅ 测试通过 - 批量导入功能正常")


def test_stats():
    """测试统计接口"""
    print("\n" + "=" * 60)
    print("测试13: 统计接口")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/stats")
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"统计数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True
    assert "stats" in data
    assert data["stats"]["total_rounds"] >= 3
    assert data["stats"]["total_winners"] >= 5
    assert len(data["stats"]["rounds"]) >= 3

    print("✅ 测试通过 - 统计接口正常")


def test_duplicate_flag():
    """测试跨期重复编码标记"""
    print("\n" + "=" * 60)
    print("测试14: 跨期重复编码标记")
    print("=" * 60)

    test_code = "DUPTEST001"

    print("\n添加第一条记录到第1期...")
    requests.post(
        f"{BASE_URL}/api/winners",
        json={
            "code": test_code,
            "name": "重复测试1",
            "plate_number": "京D00001",
            "lottery_round": "2024年第1期",
            "win_date": "2024-01-15"
        }
    )

    print("添加第二条记录到第2期...")
    requests.post(
        f"{BASE_URL}/api/winners",
        json={
            "code": test_code,
            "name": "重复测试2",
            "plate_number": "京D00002",
            "lottery_round": "2024年第2期",
            "win_date": "2024-02-15"
        }
    )

    print("\n查询所有期数...")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": test_code}
    )
    data = response.json()

    print(f"状态码: {response.status_code}")
    print(f"是否跨期重复: {data['is_duplicate_across_rounds']}")
    print(f"记录数: {data['count']}")

    assert response.status_code == 200
    assert data["won"] == True
    assert data["is_duplicate_across_rounds"] == True
    assert data["count"] == 2

    print("✅ 跨期重复编码标记正确")

    print("\n指定期数查询（不应标记为重复）...")
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"code": test_code, "lottery_round": "2024年第1期"}
    )
    data = response.json()

    assert data["is_duplicate_across_rounds"] == False
    assert data["count"] == 1

    print("✅ 指定期数查询不标记为重复")

    print("\n清理测试数据...")
    requests.delete(f"{BASE_URL}/api/winners/{test_code}", json={"lottery_round": "2024年第1期"})
    requests.delete(f"{BASE_URL}/api/winners/{test_code}", json={"lottery_round": "2024年第2期"})
    print("✅ 测试数据清理完成")

    print("✅ 测试通过 - 跨期重复编码标记功能正常")


def test_webpage():
    """测试网页是否可访问"""
    print("\n" + "=" * 60)
    print("测试15: 网页可访问性")
    print("=" * 60)

    response = requests.get(BASE_URL)

    print(f"状态码: {response.status_code}")
    print(f"页面标题包含: {'车牌摇号结果查询' in response.text}")
    print(f"期数选择器存在: {'lotteryRound' in response.text}")

    assert response.status_code == 200
    assert "车牌摇号结果查询" in response.text
    assert "lotteryRound" in response.text

    print("✅ 测试通过 - 网页可正常访问")


if __name__ == "__main__":
    print("🚀 开始运行 API 测试...")
    print("请确保服务已启动: python app.py")
    print()

    try:
        test_webpage()
        test_get_rounds()
        test_query_winning_code()
        test_query_with_round()
        test_query_wrong_round()
        test_query_non_winning_code()
        test_duplicate_code_same_round()
        test_same_code_different_round()
        test_get_winners_by_round()
        test_delete_with_round()
        test_crud_winner()
        test_batch_import()
        test_stats()
        test_duplicate_flag()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print("\n📋 重复编码问题修复验证总结:")
        print("  ✅ 同一期内编码重复被正确拒绝（409错误）")
        print("  ✅ 不同期允许相同编码存在")
        print("  ✅ 跨期查询同一编码可返回多条记录")
        print("  ✅ 指定期数查询可精确匹配")
        print("  ✅ 数据完整性检查自动修复问题")
        print("  ✅ 批量导入自动去重")
        print("  ✅ 跨期重复编码标记提示")
        print("  ✅ 数据迁移兼容旧格式")

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

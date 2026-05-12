"""快速接口测试脚本"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_and_login():
    # 注册
    r = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert r.status_code in (201, 400), f"register: {r.status_code} {r.text}"
    if r.status_code == 201:
        data = r.json()
        assert data["username"] == "testuser"
        print(f"[OK] 注册成功: {data['username']} ({data['id']})")
    else:
        print(f"[INFO]  用户已存在，跳过注册")

    # 登录
    r = client.post("/auth/login", json={"username": "testuser", "password": "testpass123"})
    assert r.status_code == 200, f"login: {r.status_code} {r.text}"
    token = r.json()["access_token"]
    print(f"[OK] 登录成功，获得 token")

    headers = {"Authorization": f"Bearer {token}"}

    # 查询当前用户
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    print(f"[OK] /auth/me: {r.json()['username']}")

    return headers

def test_saves(headers):
    # 创建存档
    r = client.post("/game/saves", headers=headers, json={
        "save_name": "测试存档",
        "world_bg": "这是一片奇幻大陆",
        "char_name": "勇者",
        "char_bg": "来自村庄的年轻人",
        "hp": 100, "max_hp": 100,
        "stats": {"str": 7, "int": 5, "cha": 5, "agi": 8},
        "gold": 50, "turn": 3,
        "items": ["铁剑", "面包"],
        "history": [{"role": "user", "content": "向前走"}]
    })
    assert r.status_code == 201, f"create save: {r.status_code} {r.text}"
    save = r.json()
    save_id = save["id"]
    print(f"[OK] 创建存档: {save['save_name']} (id={save_id[:8]}...)")

    # 列表
    r = client.get("/game/saves", headers=headers)
    assert r.status_code == 200
    saves = r.json()
    print(f"[OK] 存档列表: 共 {len(saves)} 条")

    # 读取详情
    r = client.get(f"/game/saves/{save_id}", headers=headers)
    assert r.status_code == 200
    detail = r.json()
    assert detail["items"] == ["铁剑", "面包"]
    print(f"[OK] 读取存档: items={detail['items']}")

    # 更新
    r = client.put(f"/game/saves/{save_id}", headers=headers, json={"hp": 80, "gold": 120, "turn": 5})
    assert r.status_code == 200
    updated = r.json()
    assert updated["hp"] == 80 and updated["gold"] == 120
    print(f"[OK] 更新存档: hp={updated['hp']}, gold={updated['gold']}")

    # 删除
    r = client.delete(f"/game/saves/{save_id}", headers=headers)
    assert r.status_code == 204
    print(f"[OK] 删除存档成功")

    # 确认已删除
    r = client.get(f"/game/saves/{save_id}", headers=headers)
    assert r.status_code == 404
    print(f"[OK] 确认存档已删除 (404)")

def test_auth_errors():
    # 错误密码
    r = client.post("/auth/login", json={"username": "testuser", "password": "wrongpass"})
    assert r.status_code == 401
    print(f"[OK] 错误密码返回 401")

    # 无 token 访问受保护接口
    r = client.get("/auth/me")
    assert r.status_code == 401
    print(f"[OK] 无 token 返回 401")

if __name__ == "__main__":
    print("=" * 40)
    print("开始接口测试")
    print("=" * 40)
    headers = test_register_and_login()
    test_saves(headers)
    test_auth_errors()
    print("=" * 40)
    print("全部测试通过 [OK]")

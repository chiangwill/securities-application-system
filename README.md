# 證券帳號申請系統

一個基於 Django 的證券帳號申請流程管理系統，提供完整的申請、審核、補件流程。

## 功能特色

- 🔐 **使用者身份驗證**：註冊、登入、登出
- 📝 **申請表單**：證券帳號申請表單，包含帳號名稱、手機號碼、地址驗證
- 📊 **申請狀態管理**：審核中、已通過、已拒絕、待補件四種狀態
- 🔄 **補件功能**：當狀態為「待補件」時，使用者可更新申請資料
- 👨‍💼 **管理後台**：管理員可透過 Django Admin 審核申請
- 🎉 **通過頁面**：申請通過後的專屬恭喜頁面
- 📱 **響應式設計**：使用 Bootstrap 5 的現代化介面

## 環境要求

- Python 3.13+
- uv (Python 套件管理工具)

## 快速開始

### 1. clone 專案並設置環境

```bash
# 克隆專案
git clone <your-repository-url>
cd securities-application-system

# 使用 uv 安裝依賴
uv sync
```

### 2. 資料庫設置

```bash
# 執行資料庫遷移
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### 3. 創建管理員帳號

```bash
# 使用自定義指令創建超級使用者（推薦）
uv run python manage.py create_superuser

# 或使用 Django 內建指令
uv run python manage.py createsuperuser
```

### 4. 啟動開發伺服器

```bash
# 啟動服務器
uv run python manage.py runserver
```

## 使用說明

### 用戶端功能

1. **首頁**：http://127.0.0.1:8000/
   - 未登入：顯示註冊/登入選項和申請流程說明
   - 已登入：自動導向申請狀態頁面

2. **使用者註冊**：http://127.0.0.1:8000/accounts/register/
   - 註冊新帳號開始申請流程

3. **申請流程**：
   - 登入後自動導向申請狀態頁面
   - 如無申請記錄，會引導至申請表單
   - 支援一人一帳戶的業務邏輯

4. **申請狀態查看**：http://127.0.0.1:8000/application/status/
   - 查看目前申請狀態和詳細資訊
   - 根據不同狀態顯示對應操作

### 管理端功能

1. **管理後台**：http://127.0.0.1:8000/admin/
   - 使用超級使用者帳號登入
   - 查看所有申請記錄
   - 進行審核操作（通過/拒絕/要求補件）
   - 支援批量操作

### 申請狀態說明

- **審核中 (PENDING)**：申請已提交，等待審核
- **已通過 (APPROVED)**：申請通過，可查看成功頁面
- **已拒絕 (REJECTED)**：申請被拒絕，顯示拒絕原因
- **待補件 (ADDITIONAL_REQUIRED)**：需要補充資料，可更新申請

## 測試

### 運行測試

```bash
# 運行所有測試
uv run python manage.py test applications

# 運行特定測試模組
uv run python manage.py test applications.tests.test_models
```

### 測試覆蓋率

```bash
# 運行測試並生成覆蓋率報告
uv run coverage run --source='.' manage.py test applications && uv run coverage report

# 生成 HTML 覆蓋率報告
uv run coverage html
```

HTML 報告會生成在 `htmlcov/` 目錄，可以用瀏覽器打開 `htmlcov/index.html` 查看詳細報告。

## 技術架構

### 後端技術
- **Django 5.2.3**：Web 框架
- **SQLite**：資料庫（開發環境）
- **Django Admin**：管理後台

### 開發工具
- **uv**：Python 套件管理
- **coverage**：測試覆蓋率工具

## 專案結構

```
securities-application-system/
├── applications/                 # 主要應用
│   ├── models.py                # 資料模型
│   ├── forms.py                 # 表單定義
│   ├── views.py                 # 視圖邏輯
│   ├── admin.py                 # 管理後台配置
│   ├── templates/               # HTML 模板
│   ├── tests/                   # 測試檔案
│   └── management/commands/     # 自定義管理指令
├── securities_system/           # Django 專案設定
├── manage.py                    # Django 管理腳本
├── pyproject.toml              # 專案配置
└── README.md                   # 專案說明
```

## 資料模型

### Application 模型
- `user`: 申請人（ForeignKey 到 User）
- `account_name`: 申請人帳號名稱（唯一）
- `phone_number`: 手機號碼（台灣格式驗證）
- `address`: 詳細地址
- `status`: 申請狀態
- `created_at`: 申請時間
- `reviewed_by`: 審核人員
- `rejection_reason`: 拒絕原因
- `additional_info_required`: 補件說明

## 表單驗證

- **帳號名稱**：3-20字符，英文數字底線短橫線，系統唯一
- **手機號碼**：台灣手機格式（09XXXXXXXX）
- **地址**：10-200字符，包含基本地址元素

## 故障排除

### 常見問題

1. **測試失敗**：確保已執行資料庫遷移
2. **CSS 樣式異常**：檢查網路連線（使用 CDN）
3. **權限錯誤**：確認檔案權限和虛擬環境

### 重置資料庫

```bash
# 刪除資料庫檔案
rm db.sqlite3

# 重新執行遷移
uv run python manage.py migrate

# 重新創建管理員
uv run python manage.py create_superuser
```

## 授權

此專案僅用於面試展示目的。

---

如有任何問題，請檢查控制台輸出或 Django 錯誤頁面獲取詳細錯誤訊息。
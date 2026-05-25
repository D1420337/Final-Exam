# 路由與 API 設計文件 (Flask Routes & API Design)

本文件描述「校園二手書交換平台」的所有 Flask URL 端點設計、HTTP 請求方法、輸入驗證、商業邏輯流轉、錯誤處理與 Jinja2 模板對照規範。

---

## 1. 路由總覽表格 (Route Overview)

本平台設計符合 RESTful 直覺的 URL 命名習慣，並因應傳統 HTML `<form>` 表單限制，以 `POST` 來模擬資料更新與刪除。

| 功能區塊 | 功能名稱 | HTTP 方法 | URL 路徑 | 對應 Jinja2 模板 | 邏輯說明 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **首頁** | 平台入口/首頁展示 | `GET` | `/` | `templates/index.html` | 展示最新上架的 Available 書籍，提供關鍵字與篩選按鈕。 |
| **驗證** | 註冊頁面 | `GET` | `/auth/register` | `templates/auth/register.html` | 顯示帳號註冊表單（要求學校 `.edu.tw` 信箱）。 |
| **驗證** | 執行註冊 | `POST` | `/auth/register` | — *(重導向至驗證)* | 建立未啟用帳號，將 6 碼驗證碼輸出至終端機日誌。 |
| **驗證** | 驗證頁面 | `GET` | `/auth/verify` | `templates/auth/verify.html` | 顯示輸入 6 位數信箱驗證碼之輸入框。 |
| **驗證** | 執行驗證 | `POST` | `/auth/verify` | — *(重導向至登入)* | 比對驗證碼。成功則啟用帳號並導向登入。 |
| **驗證** | 登入頁面 | `GET` | `/auth/login` | `templates/auth/login.html` | 顯示登入表單。 |
| **驗證** | 執行登入 | `POST` | `/auth/login` | — *(重導向至首頁)* | 驗證密碼 Hash，通過後寫入 Session。 |
| **驗證** | 帳號登出 | `GET` | `/auth/logout` | — *(重導向至首頁)* | 清除 Session，導向首頁。 |
| **書籍** | 分類與精確檢索 | `GET` | `/books/search` | `templates/books/search.html` | 組合查詢系所、科目與 ISBN，1 秒內展示卡片列表。 |
| **書籍** | 書籍上架表單 | `GET` | `/books/upload` | `templates/books/upload.html` | 登入限制，呈現書籍詳情、價格/交換與書況上傳表單。 |
| **書籍** | 執行書籍上架 | `POST` | `/books/upload` | — *(重導向至書櫃)* | 處理相片上傳、呼叫 DB 寫入，成功後重導向至個人書櫃。 |
| **書籍** | 書籍詳情與留言問答 | `GET` | `/books/<int:book_id>` | `templates/books/detail.html` | 顯示書籍詳情、聯絡資訊（若已媒合）與公開問答板。 |
| **書籍** | 發表留言/回覆 | `POST` | `/books/<int:book_id>/comment` | — *(重導向至詳情)* | 支援自參照 `parent_id` 兩層式子留言回覆，寫入後重導向。 |
| **書櫃** | 個人書櫃主控制台 | `GET` | `/cabinet` | `templates/cabinet/index.html` | 登入限制，依上架中/已預約/已成交狀態分類展示書籍。 |
| **書櫃** | 編輯書籍表單 | `GET` | `/cabinet/edit/<int:book_id>` | `templates/cabinet/edit.html` | 限制書主，加載並呈現該書籍的原有資訊供修改。 |
| **書櫃** | 執行書籍修改 | `POST` | `/cabinet/edit/<int:book_id>` | — *(重導向至書櫃)* | 限制書主，接收表單內容並更新 DB，隨後重新導向。 |
| **書櫃** | 下架/刪除書籍 | `POST` | `/cabinet/delete/<int:book_id>` | — *(重導向至書櫃)* | 限制書主，一鍵自 DB 刪除該書籍（留言與預約聯級清空）。 |
| **預約** | 送出預約請求 | `POST` | `/requests/create/<int:book_id>` | — *(重導向至詳情)* | 買家送出預約申請，將書籍暫時鎖定並通知書主。 |
| **預約** | 同意預約請求 | `POST` | `/requests/accept/<int:req_id>` | — *(重導向至書櫃)* | 書主接受預約。將書籍鎖定為 Reserved，顯示雙方聯絡方式。 |
| **預約** | 拒絕預約請求 | `POST` | `/requests/reject/<int:req_id>` | — *(重導向至書櫃)* | 書主拒絕預約。書籍釋放還原為 Available。 |
| **書櫃** | 確認交易成交 | `POST` | `/cabinet/complete/<int:book_id>`| — *(重導向至書櫃)* | 面交成功後，書主確認交易，書籍正式轉為 Sold 歸檔。 |

---

## 2. 路由詳細說明 (Route Details)

### 2.1 會員認證藍圖 (`/auth`)

#### `GET /auth/register` 與 `POST /auth/register`
*   **輸入**：表單欄位 `username`（字串，必填）、`email`（字串，必填）、`password`（字串，必填，最少 8 碼）、`contact_info`（字串，選填）。
*   **處理邏輯**：
    1. 檢驗 `email` 是否符合 `*.edu.tw` 結尾之學校信箱，非 edu.tw 信箱即擋下。
    2. 檢查 `email` 是否已被註冊（呼叫 `User.query.filter_by(email=email).first()`）。
    3. 生成 6 碼隨機數字驗證碼 `verification_code`。
    4. 密碼採用 `generate_password_hash` 加密。
    5. **開發模擬驗證**：將驗證碼以 `print(f"[Verification Code for {email}]: {code}")` 輸出至控制台，不寄送真實信件。
    6. 寫入 `User`（`is_verified=False`）。
*   **輸出**：重導向至 `/auth/verify?email=<email>`。
*   **錯誤處理**：驗證失敗或信箱重複時，使用 `flash()` 呈現錯誤訊息，並重新渲染註冊頁。

#### `POST /auth/verify`
*   **輸入**：表單欄位 `email`、`verification_code`。
*   **處理邏輯**：比對 User 的驗證碼。成功則將 `is_verified` 改為 `True`，清空 `verification_code`。
*   **輸出**：成功導向 `/auth/login`；失敗重導向 `/auth/verify`。

#### `POST /auth/login`
*   **輸入**：表單欄位 `email`、`password`。
*   **處理邏輯**：
    1. 查無用戶或 `is_verified == False`，返回錯誤。
    2. 使用 `check_password_hash` 比對密碼。
    3. 成功後將 `user_id` 與 `username` 寫入 `session`。
*   **輸出**：重導向至 `/`。

---

### 2.2 二手書籍藍圖 (`/books`)

#### `GET /books/search`
*   **輸入**：查詢參數 `dept`（系所篩選，選填）、`subject`（課程篩選，選填）、`isbn`（ISBN，選填）、`query`（關鍵字模糊搜尋，選填）。
*   **處理邏輯**：
    *   以 `Book.query.filter(Book.status == 'Available')` 為基礎。
    *   動態追加 `dept`、`subject`、`isbn` 等精確條件，與全域關鍵字模糊匹配。
    *   為確保搜尋在 **1 秒內** 完成，建立 `idx_books_search` 包含 `dept`、`subject`、`isbn` 聯合索引。
*   **輸出**：渲染 `books/search.html`，以卡片流呈現。

#### `POST /books/upload`
*   **輸入**：`title`、`author`、`publisher`、`isbn`、`price`、`is_exchange`、`exchange_item`、`condition`、`description`、`dept`、`subject`；相片檔案 `book_image`。
*   **處理邏輯**：驗證使用者登入。將相片以安全檔名儲存於 `static/uploads/`，隨後呼叫 `Book.create()` 寫入資料庫。
*   **輸出**：重導向至 `/cabinet`。

#### `GET /books/<int:book_id>`
*   **處理邏輯**：呼叫 `Book.get_by_id(book_id)`。取得所有與該書關聯的 `Comment` 留言列表。
*   *備註*：在留言板渲染中，區分 `parent_id IS NULL` 的主提問與 `parent_id` 指向主提問的賣家回覆，呈現乾淨的層級式問答。

---

### 2.3 個人書櫃藍圖 (`/cabinet`)

#### `GET /cabinet`
*   **邏輯**：
    *   驗證登入。
    *   查出 `Book.seller_id == session['user_id']` 的所有書籍，分類為：`Available` (上架中)、`Reserved` (已預約)、`Sold` (已成交)。
    *   查出與該書主所有上架書籍關聯的 `Reservation.status == 'Pending'` 的預約請求。
*   **輸出**：渲染 `cabinet/index.html`。若有待審核的預約，個人書櫃導覽列顯示紅點通知。

---

## 3. Jinja2 模板清單 (Jinja2 Templates)

前端模板皆置於 `app/templates/` 中，全部繼承自全域 Layout `base.html`：

1.  **`base.html`** (基礎版面)
    *   包含 RWD 導覽列（未登入顯示登入/註冊；已登入顯示上架、個人書櫃與紅點通知、登出）。
    *   包含 Flask `get_flashed_messages()` 的全域彈出或頂部提示樣式。
2.  **`index.html`** (首頁)
    *   繼承 `base.html`。首頁大橫幅 (Hero Banner)、精美搜尋區、以及最新上架二手書的**卡片流式**展示。
3.  **`auth/register.html`** & **`auth/verify.html`** & **`auth/login.html`** (會員系統)
    *   繼承 `base.html`。提供簡潔現代的卡片式輸入表單。
4.  **`books/search.html`** (檢索頁)
    *   繼承 `base.html`。左側/頂部為篩選面板（系所下拉選單、ISBN 與科目欄位），右側為搜尋結果的卡片網格。
5.  **`books/detail.html`** (詳情與問答)
    *   繼承 `base.html`。左側顯示書況照片與評級，右側顯示價格/交換詳情與「預約請求按鈕」；下方為層級式公開留言板。
6.  **`cabinet/index.html`** (個人書櫃)
    *   繼承 `base.html`。包含狀態分頁切換卡（Tab），並能查看收到的預約申請（接受/拒絕）及完成面交按鈕。

---

## 4. 路由骨架程式碼實作 (Skeleton Code)

路由骨架程式碼已依照 MVC 與架構規範，完整建立於專案的 `app/routes/` 檔案目錄中：
*   **會員控制骨架**：[app/routes/auth.py](file:///c:/Users/Administrator/Final-Exam/app/routes/auth.py)
*   **書籍檢索與上架骨架**：[app/routes/books.py](file:///c:/Users/Administrator/Final-Exam/app/routes/books.py)
*   **個人書櫃管理骨架**：[app/routes/cabinet.py](file:///c:/Users/Administrator/Final-Exam/app/routes/cabinet.py)
*   **預約媒合流程骨架**：[app/routes/requests.py](file:///c:/Users/Administrator/Final-Exam/app/routes/requests.py)
*   **路由匯總宣告**：[app/routes/__init__.py](file:///c:/Users/Administrator/Final-Exam/app/routes/__init__.py)

> [!TIP]
> 骨架中每個路由皆已完整標註對應的 HTTP Methods、邏輯處理步驟與對應模板之 Docstring，開發團隊可直接在此基礎上編寫商業邏輯，確保與架構設計 100% 契合。

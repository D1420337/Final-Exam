# 使用者流程圖與系統序列圖 (Flowcharts & Sequence Diagrams)

本文件描述「校園二手書交換平台」的使用者操作流程（User Flow）、系統資料互動序列圖（Sequence Diagram）以及對應的功能與路由對照表。

---

## 1. 使用者流程圖 (User Flow)

此圖描述使用者從進入網站開始，如何登入、搜尋書籍、進行上架、留言詢問，直至最後完成預約面交的操作路徑：

```mermaid
flowchart TD
    Start([使用者開啟網頁]) --> Home[首頁 - 最新書籍與搜尋入口]
    Home --> CheckLogin{是否已登入？}
    
    %% 未登入流程
    CheckLogin -- 否 --> AuthSelect{要註冊還是登入？}
    AuthSelect -- 註冊 --> Register[輸入 edu.tw 信箱]
    Register --> ValidateMail{信箱格式是否正確？}
    ValidateMail -- 否 --> Register
    ValidateMail -- 是 --> VerifyPage[輸入終端機 log 顯示的驗證碼]
    VerifyPage --> Login[進行帳號密碼登入]
    AuthSelect -- 登入 --> Login
    Login --> Home
    
    %% 已登入流程
    CheckLogin -- 是 --> ActionSelect{要執行什麼操作？}
    
    %% 尋書與交易流程
    ActionSelect -->|尋找書籍| Search[分類與精確篩選<br/>系所 / 科目 / ISBN]
    Search --> SearchResults[瀏覽書籍卡片列表]
    SearchResults --> BookDetail[查看書籍詳情頁]
    
    BookDetail --> DetailAction{需要詢問或購買？}
    DetailAction -->|有疑問| CommentBoard[在留言板公開提問/回覆]
    DetailAction -->|確定要| SendRequest[送出交換或購買預約請求]
    SendRequest --> WaitSeller[等待書主審核]
    
    %% 上架與書櫃流程
    ActionSelect -->|二手書上架| UploadBook[填寫書名、ISBN、價格/交換<br/>勾選書況評級與上傳照片]
    UploadBook --> CabinetList[個人書櫃 - 上架中]
    
    %% 書櫃管理
    ActionSelect -->|管理個人書櫃| Cabinet[進入個人書櫃面板]
    Cabinet --> CabinetTabs{查看哪種狀態的書籍？}
    CabinetTabs -->|上架中| CabinetActive[可編輯資料、下架書籍<br/>或查看留言]
    CabinetTabs -->|已預約| CabinetReserved[查看買家預約請求]
    CabinetReserved --> SellerDecision{接受預約？}
    SellerDecision -- 拒絕 --> CabinetActive
    SellerDecision -- 接受 --> CabinetMatch[雙方解除聯絡資訊限制<br/>約定校園面交時間地點]
    CabinetMatch --> FaceToFace[校園面交、付款/交換]
    FaceToFace --> MarkComplete[書主點擊「確認成交」]
    MarkComplete --> CabinetSold[書籍移入「已成交」分類]
```

---

## 2. 系統序列圖 (Sequence Diagrams)

### 2.1 書籍上架資料流 (F-01)

描述使用者填寫書籍表單並送出時，後端控制器、資料庫與頁面重導向的互動順序：

```mermaid
sequenceDiagram
    autonumber
    actor User as 賣家 (使用者)
    participant Browser as 瀏覽器
    participant Route as Flask Route (/books/upload)
    participant Model as SQLAlchemy (Book Model)
    participant DB as SQLite 資料庫

    User->>Browser: 填寫書籍資訊、價格、上傳照片並點擊上架
    Browser->>Route: POST /books/upload (Multipart Form Data)
    Note over Route: 1. 驗證欄位是否填寫<br/>2. 儲存上傳之書況照片至 static/uploads/
    Route->>Model: 實例化 Book 物件 (設定狀態為 Available)
    Route->>Model: db.session.add(new_book)
    Route->>DB: db.session.commit()
    DB-->>Route: 儲存成功 (產生 book_id)
    Route-->>Browser: HTTP 302 重導向至個人書櫃 (/cabinet)
    Browser->>User: 顯示最新上架之二手書卡片
```

### 2.2 預約請求與媒合流程 (F-03)

描述買家發送請求到雙方聯絡資訊揭露、面交完成的完整資料互動流：

```mermaid
sequenceDiagram
    autonumber
    actor Buyer as 買家 (學生)
    participant Browser as 買家瀏覽器
    participant Route as Flask Route
    participant DB as SQLite 資料庫
    actor Seller as 賣家 (書主)

    Buyer->>Browser: 於詳情頁填寫備註並點擊「發送預約請求」
    Browser->>Route: POST /requests/create/<book_id>
    Route->>DB: 1. 建立 ReservationRequest (Pending)<br/>2. 將 Book.status 標註為被預約中
    DB-->>Route: 寫入成功
    Route-->>Browser: 回傳成功提示
    
    Note over Seller: 賣家登入平台並開啟個人書櫃
    Seller->>Route: GET /cabinet
    Route->>DB: 查詢該用戶收到的 Pending 預約
    DB-->>Route: 回傳預約請求
    Route-->>Seller: 顯示「待審核預約卡片」 (包含買家信箱與說明)
    
    Seller->>Route: 點擊「同意交易」 (POST /requests/accept/<req_id>)
    Route->>DB: 1. Request 狀態變更為 Accepted<br/>2. Book 狀態正式變更為 Reserved (已預約)
    DB-->>Route: 更新成功
    Route-->>Seller: 揭露買家信箱與 Line ID，以便連繫面交
    Note over Buyer, Seller: 雙方在校園面交、付款確認
    Seller->>Route: 面交完成，點擊「確認成交」 (POST /cabinet/complete/<book_id>)
    Route->>DB: Book 狀態變更為 Sold (已成交)
    DB-->>Route: 更新成功
    Route-->>Seller: 書籍移入「已成交歷史」
```

---

## 3. 功能路由對照表

本表列出「校園二手書交換平台」的所有 Flask 路由、HTTP 方法、對應的 Jinja2 模板，以及實作的功能定義：

| 功能代號 | 功能模組 | HTTP 方法 | URL 路徑 | 對應 Jinja2 模板 | 邏輯處理與說明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **全域** | 首頁展示 | `GET` | `/` | `index.html` | 展示最新上架的書籍卡片，提供快捷搜尋欄。 |
| **會員** | 註冊頁面 | `GET` | `/auth/register` | `auth/register.html` | 呈現註冊表單。 |
| **會員** | 執行註冊 | `POST` | `/auth/register` | *(無，重新導向)* | 檢核 `.edu.tw` 信箱並寫入用戶，於 Terminal 輸出驗證碼。 |
| **會員** | 驗證頁面 | `GET` | `/auth/verify` | `auth/verify.html` | 呈現輸入驗證碼的畫面。 |
| **會員** | 執行驗證 | `POST` | `/auth/verify` | *(無，重新導向)* | 比對驗證碼，成功則啟用帳號並導向登入。 |
| **會員** | 登入頁面 | `GET` | `/auth/login` | `auth/login.html` | 呈現登入表單。 |
| **會員** | 執行登入 | `POST` | `/auth/login` | *(無，重新導向)* | 驗證密碼 Hash，成功後寫入 Session。 |
| **會員** | 登出帳號 | `GET` | `/auth/logout` | *(無，重新導向)* | 清除 Session，導向首頁。 |
| **F-01** | 書籍上架頁 | `GET` | `/books/upload` | `books/upload.html` | 限制已登入用戶，呈現上架填寫表單。 |
| **F-01** | 執行上架 | `POST` | `/books/upload` | *(無，重新導向)* | 處理相片上傳、寫入書籍 Model，導向個人書櫃。 |
| **F-02** | 分類與檢索 | `GET` | `/books/search` | `books/search.html` | 支援系所選單、科目、ISBN 之組合篩選，回傳卡片。 |
| **F-05** | 書籍詳情頁 | `GET` | `/books/<int:id>` | `books/detail.html` | 展示完整書況、留言問答板、預約按鈕。 |
| **F-05** | 公開留言/回覆 | `POST` | `/books/<int:id>/comment`| *(無，重新導向)* | 寫入問答（支援 `parent_id` 兩層式子留言回覆）。 |
| **F-03** | 建立預約請求 | `POST` | `/requests/create/<int:book_id>`| *(無，重新導向)* | 買家送出購買/交換意願書，標註書籍保留狀態。 |
| **F-04** | 個人書櫃頁 | `GET` | `/cabinet` | `cabinet/index.html` | 依「上架中/已預約/已成交」分頁卡片管理。 |
| **F-04** | 編輯書籍頁 | `GET` | `/cabinet/edit/<int:book_id>` | `cabinet/edit.html` | 限制書主，呈現修改表單。 |
| **F-04** | 執行修改 | `POST` | `/cabinet/edit/<int:book_id>` | *(無，重新導向)* | 更新書籍資訊，導回書櫃。 |
| **F-04** | 刪除/下架書籍 | `POST` | `/cabinet/delete/<int:book_id>`| *(無，重新導向)* | 書主一鍵刪除未交易之書籍。 |
| **F-03** | 接受預約 | `POST` | `/requests/accept/<int:req_id>`| *(無，重新導向)* | 書主接受預約，書籍變更為 Reserved，揭露聯繫方式。 |
| **F-03** | 拒絕預約 | `POST` | `/requests/reject/<int:req_id>`| *(無，重新導向)* | 書主拒絕預約，書籍狀態還原為 Available。 |
| **F-04** | 確認成交完成 | `POST` | `/cabinet/complete/<int:book_id>`| *(無，重新導向)* | 交易完成，狀態改為 Sold，正式關閉該次交易流程。 |

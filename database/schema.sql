-- SQLite Database Schema for Campus Second-hand Book Exchange Platform

-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    username TEXT NOT NULL,
    contact_info TEXT,
    is_verified INTEGER DEFAULT 0, -- 0: False, 1: True
    verification_code TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Books Table
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT,
    isbn TEXT,
    price INTEGER DEFAULT 0,
    is_exchange INTEGER DEFAULT 0, -- 0: False, 1: True
    exchange_item TEXT,
    condition TEXT NOT NULL, -- '全新', '接近全新', '輕微劃記', '劃記繁多', '書頁破損'
    description TEXT,
    image_url TEXT,
    status TEXT DEFAULT 'Available', -- 'Available', 'Reserved', 'Sold'
    dept TEXT,
    subject TEXT,
    publish_year TEXT NOT NULL,
    edition TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Reservations Table
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'Pending', -- 'Pending', 'Accepted', 'Rejected'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Comments Table
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    parent_id INTEGER,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
);

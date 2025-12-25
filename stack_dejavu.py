#!/usr/bin/env python3
"""StackOverflow Déjà Vu - Because you've definitely seen this error before."""

import json
import os
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
import sys

DB_FILE = "stack_memory.db"

class DéjàVu:
    """Remembers solutions so you don't have to (again)."""
    
    def __init__(self):
        """Initialize our tiny brain database."""
        self.conn = sqlite3.connect(DB_FILE)
        self._setup_db()
    
    def _setup_db(self):
        """Create table if it doesn't exist (like that answer you swear you saw)."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                solution TEXT,
                added_date TIMESTAMP,
                use_count INTEGER DEFAULT 0
            )
        """)
    
    def add_solution(self, url, title, solution):
        """Save a solution before you forget it (again)."""
        try:
            self.conn.execute(
                "INSERT INTO solutions (url, title, solution, added_date) VALUES (?, ?, ?, ?)",
                (url, title, solution, datetime.now())
            )
            self.conn.commit()
            print(f"✓ Saved: {title[:50]}...")
            return True
        except sqlite3.IntegrityError:
            print(f"✗ Already saved (you've been here before)")
            return False
    
    def find_solution(self, search_term):
        """Search for something you've definitely solved before."""
        cursor = self.conn.execute(
            "SELECT url, title, solution, use_count FROM solutions WHERE title LIKE ? OR solution LIKE ? ORDER BY use_count DESC",
            (f"%{search_term}%") * 2
        )
        results = cursor.fetchall()
        
        if results:
            print(f"\n🎉 Found {len(results)} déjà vu(s):")
            for i, (url, title, solution, count) in enumerate(results[:3], 1):
                print(f"{i}. {title[:60]}... (used {count} times)")
                print(f"   URL: {url}")
                print(f"   Solution: {solution[:80]}...\n")
                # Increment use count
                self.conn.execute("UPDATE solutions SET use_count = use_count + 1 WHERE url = ?", (url,))
            self.conn.commit()
            return True
        else:
            print(f"\n🤷 No déjà vu for '{search_term}' (this time it's new!)")
            return False
    
    def list_all(self):
        """Show all your past struggles (for nostalgia)."""
        cursor = self.conn.execute("SELECT title, url, use_count FROM solutions ORDER BY use_count DESC")
        results = cursor.fetchall()
        
        if results:
            print(f"\n📚 Your StackOverflow Memory ({len(results)} items):")
            for title, url, count in results:
                print(f"• {title[:50]}... (used {count}x)")
        else:
            print("\n🧠 Memory empty (like after reading complex regex)")
    
    def close(self):
        """Close the database (but the memories remain)."""
        self.conn.close()


def main():
    """Main function - because every script needs one."""
    dv = DéjàVu()
    
    if len(sys.argv) < 2:
        print("Usage:\n  python stack_dejavu.py add <url> <title> <solution>\n  python stack_dejavu.py find <search_term>\n  python stack_dejavu.py list")
        return
    
    command = sys.argv[1].lower()
    
    if command == "add" and len(sys.argv) >= 5:
        url = sys.argv[2]
        title = sys.argv[3]
        solution = " ".join(sys.argv[4:])
        dv.add_solution(url, title, solution)
    elif command == "find" and len(sys.argv) >= 3:
        search_term = sys.argv[2]
        dv.find_solution(search_term)
    elif command == "list":
        dv.list_all()
    else:
        print("Invalid command (RTFM, but there isn't one)")
    
    dv.close()

if __name__ == "__main__":
    main()

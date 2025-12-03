from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'mental_health.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                max_score INTEGER NOT NULL,
                category TEXT NOT NULL,
                note TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO history (name, score, max_score, category, note, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name', '-'),
            data.get('score', 0),
            data.get('max_score', 60),
            data.get('category', ''),
            data.get('note', ''),
            timestamp
        ))
        conn.commit()
        
        return jsonify({
            'success': True,
            'id': cursor.lastrowid,
            'message': 'Data berhasil disimpan'
        })

@app.route('/api/history', methods=['GET'])
def get_history():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT id, name, score, max_score, category, note, timestamp 
            FROM history 
            ORDER BY id DESC
        ''').fetchall()
        
        data = [{
            'id': row['id'],
            'name': row['name'],
            'score': row['score'],
            'max_score': row['max_score'],
            'category': row['category'],
            'note': row['note'],
            'timestamp': row['timestamp']
        } for row in rows]
        
        return jsonify({'success': True, 'data': data})

@app.route('/api/history/<int:id>', methods=['DELETE'])
def delete_one(id):
    with get_db() as conn:
        conn.execute('DELETE FROM history WHERE id = ?', (id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Data berhasil dihapus'})

@app.route('/api/history', methods=['DELETE'])
def delete_all():
    with get_db() as conn:
        conn.execute('DELETE FROM history')
        conn.commit()
        return jsonify({'success': True, 'message': 'Semua data berhasil dihapus'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    with get_db() as conn:
        rows = conn.execute('SELECT score FROM history').fetchall()
        
        if not rows:
            return jsonify({
                'success': True,
                'data': {
                    'total_entries': 0,
                    'min_score': None,
                    'max_score': None,
                    'avg_score': None
                }
            })
        
        scores = [row['score'] for row in rows]
        return jsonify({
            'success': True,
            'data': {
                'total_entries': len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'avg_score': round(sum(scores) / len(scores), 2)
            }
        })

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"Backend berjalan di port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

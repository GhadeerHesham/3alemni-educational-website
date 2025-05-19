const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');

const app = express();
const db = new sqlite3.Database('./3alemni.db');

// Allow CORS for frontend to fetch from backend
app.use(cors());
app.use(express.json());

app.get('/api/centers', (req, res) => {
  db.all('SELECT * FROM centers', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});
app.get('/api/courses', (req, res) => {
  db.all('SELECT * FROM courses', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});
app.get('/api/students', (req, res) => {
  db.all('SELECT * FROM students', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});
app.get('/api/teachers', (req, res) => {
  db.all('SELECT * FROM teachers', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});
app.get('/api/enrollments', (req, res) => {
  db.all('SELECT * FROM enrollments', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});
app.get('/api/users', (req, res) => {
  db.all('SELECT * FROM users', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});
app.get('/role', (req, res) => {
  db.all('SELECT DISTINCT role FROM users', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows.map(r => r.role));
    }
  });
});
app.post('/signup', (req, res) => {
  const { firstName, lastName, email, password, role } = req.body;

  // Validate input
  if (!firstName || !lastName || !email || !password || !role) {
    return res.status(400).json({ error: 'All fields are required.' });
  }

  // Optional: Check for existing email
  db.get('SELECT * FROM users WHERE email = ?', [email], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });

    if (row) {
      return res.status(400).json({ error: 'Email already exists.' });
    }

    // Insert new user
    const query = `INSERT INTO users (first_name, last_name, email, password, role) VALUES (?, ?, ?, ?, ?)`;
    const params = [firstName, lastName, email, password, role];

    db.run(query, params, function (err) {
      if (err) return res.status(500).json({ error: err.message });

      res.status(201).json({ message: 'User registered successfully!', userId: this.lastID });
    });
  });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});

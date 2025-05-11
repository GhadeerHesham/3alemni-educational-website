const sqlite3 = require('sqlite3').verbose();

// Connect to the database
let db = new sqlite3.Database('./3alemni.db', (err) => {
    if (err) {
        return console.error('❌ Connection error:', err.message);
    }
    console.log('✅ Connected to the 3alemni SQLite database.');
});

// Example: Fetch all centers
db.all(`SELECT * FROM centers`, [], (err, rows) => {
    if (err) {
        throw err;
    }
    console.log('📚 centers:');
    rows.forEach((row) => {
        console.log(row);
    });
});

// Always close the connection
db.close((err) => {
    if (err) {
        return console.error(err.message);
    }
    console.log('🔌 Database connection closed.');
});

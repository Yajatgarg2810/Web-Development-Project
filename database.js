const sqlite3 = require("sqlite3").verbose();
const db = new sqlite3.Database("./workers.db");

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        mobile TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        job_title TEXT NOT NULL,
        experience INTEGER NOT NULL,
        profile_image TEXT
    )`);
});

module.exports = db;

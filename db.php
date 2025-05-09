<?php
// Database connection details
$host = "switchback.proxy.rlwy.net";       // Server name (usually "localhost" in XAMPP)
$username = "root";        // Default username for MySQL in XAMPP
$password = "RfpNPskZPYVAtavflAVUVJzmyvahKHuC";            // Default password for MySQL in XAMPP (empty)
$dbname = "railway";   // Name of your database

// Enable error reporting for debugging (during development only)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Create a new connection
$conn = new mysqli($host, $username, $password, $dbname);

// Check the database connection
if ($conn->connect_error) {
    die("Database connection failed: " . $conn->connect_error);
} else {
    // Optional: Debugging output to confirm connection (remove in production)
    // echo "Database connection successful!";
}
?>
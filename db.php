<?php
// Database connection using Railway's environment variables
$host = getenv('MYSQLHOST') ?: 'mysql.railway.internal';
$username = getenv('MYSQLUSER') ?: 'root';
$password = getenv('MYSQLPASSWORD') ?: 'RfpNPskZPYVAtavflAVUVJzmyvahKHuC';
$dbname = getenv('MYSQLDATABASE') ?: 'railway';
$port = getenv('MYSQLPORT') ?: '3306';

// For external connections (like from localhost):
$public_host = 'switchback.proxy.rlwy.net';
$public_port = '25244';

// Error reporting (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

try {
    // Internal Railway connection (preferred within Railway network)
    $conn = new mysqli($host, $username, $password, $dbname, $port);
    
    // Alternative for external connections:
    // $conn = new mysqli($public_host, $username, $password, $dbname, $public_port);
    
    if ($conn->connect_error) {
        throw new Exception("Connection failed: " . $conn->connect_error);
    }
    
    $conn->set_charset("utf8mb4");
    
    // Uncomment for debugging (remove in production)
    // error_log("Successfully connected to Railway MySQL");
    
} catch (Exception $e) {
    // Secure error handling
    error_log($e->getMessage());
    die("Database connection error. Please try again later.");
}
?>
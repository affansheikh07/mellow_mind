<?php
// Enable error reporting for debugging (during development only)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Create connection using Railway's environment variables
$conn = new mysqli(
    getenv('MYSQLHOST'),     // Railway provides this
    getenv('MYSQLUSER'),     // Railway provides this
    getenv('MYSQLPASSWORD'), // Railway provides this
    getenv('MYSQLDATABASE'), // Railway provides this
    getenv('MYSQLPORT')      // Railway provides this
);

// Check the database connection
if ($conn->connect_error) {
    // Enhanced error message showing connection details
    $host = getenv('MYSQLHOST');
    $user = getenv('MYSQLUSER');
    $db = getenv('MYSQLDATABASE');
    $port = getenv('MYSQLPORT');
    
    die("Database connection failed: " . $conn->connect_error . 
        ". Trying to connect to: host=$host, user=$user, db=$db, port=$port");
}

// Optional: Debugging output to confirm connection (remove in production)
// echo "Database connection successful! Connected to " . getenv('MYSQLDATABASE') . " on " . getenv('MYSQLHOST');
?>
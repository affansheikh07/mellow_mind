<?php
// Include the database connection file
require '../db.php';

// Enable error reporting for debugging (remove in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Validate that the request method is POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(["status" => "error", "message" => "Invalid request method. Only POST is allowed."]);
    exit();
}

// Get POST data safely
$name = isset($_POST['name']) ? trim($_POST['name']) : '';
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$password = isset($_POST['password']) ? trim($_POST['password']) : '';
$confirm_password = isset($_POST['confirm_password']) ? trim($_POST['confirm_password']) : '';

// Validate input fields
if (empty($name) || empty($email) || empty($password) || empty($confirm_password)) {
    echo json_encode(["status" => "error", "message" => "All fields are required."]);
    exit();
}

// Validate email format
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(["status" => "error", "message" => "Invalid email format."]);
    exit();
}

// Check if password and confirm password match
if ($password !== $confirm_password) {
    echo json_encode(["status" => "error", "message" => "Passwords do not match."]);
    exit();
}

// Check if email already exists in the database
$query = "SELECT * FROM users WHERE email = ?";
$stmt = $conn->prepare($query);
if (!$stmt) {
    echo json_encode(["status" => "error", "message" => "Database query preparation failed."]);
    exit();
}
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows > 0) {
    echo json_encode(["status" => "error", "message" => "Email already registered."]);
    exit();
}

// Hash the password
$hashed_password = password_hash($password, PASSWORD_BCRYPT);

// Insert the user into the database
$query = "INSERT INTO users (name, email, password) VALUES (?, ?, ?)";
$stmt = $conn->prepare($query);
if (!$stmt) {
    echo json_encode(["status" => "error", "message" => "Failed to prepare database query."]);
    exit();
}
$stmt->bind_param("sss", $name, $email, $hashed_password);

if ($stmt->execute()) {
    echo json_encode(["status" => "success", "message" => "Signup successful."]);
} else {
    echo json_encode(["status" => "error", "message" => "Signup failed due to a database error."]);
}
?>

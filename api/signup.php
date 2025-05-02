<?php
require '../db.php';
header('Content-Type: application/json');
error_reporting(E_ALL);
ini_set('display_errors', 1);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["status" => "error", "message" => "Invalid request method. Only POST is allowed."]);
    exit();
}

$name = htmlspecialchars(trim($_POST['name'] ?? ''));
$email = trim($_POST['email'] ?? '');
$password = $_POST['password'] ?? '';
$confirm_password = $_POST['confirm_password'] ?? '';

if (empty($name) || empty($email) || empty($password) || empty($confirm_password)) {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "All fields are required."]);
    exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "Invalid email format."]);
    exit();
}

if ($password !== $confirm_password) {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "Passwords do not match."]);
    exit();
}

if (strlen($password) < 6) {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "Password must be at least 6 characters."]);
    exit();
}

$query = "SELECT id FROM users WHERE email = ?";
$stmt = $conn->prepare($query);
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows > 0) {
    http_response_code(409);
    echo json_encode(["status" => "error", "message" => "Email already registered."]);
    exit();
}

$hashed_password = password_hash($password, PASSWORD_BCRYPT);

$query = "INSERT INTO users (name, email, password) VALUES (?, ?, ?)";
$stmt = $conn->prepare($query);
$stmt->bind_param("sss", $name, $email, $hashed_password);

if ($stmt->execute()) {
    http_response_code(201);
    echo json_encode(["status" => "success", "message" => "Signup successful."]);
} else {
    http_response_code(500);
    echo json_encode(["status" => "error", "message" => "Signup failed due to a database error."]);
}

$stmt->close();
$conn->close();
?>

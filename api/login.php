<?php
// Enable error reporting for debugging (remove in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Include database connection file
// require '../db.php';
require __DIR__ . '/../db.php';  // Absolute path is safer
// Set content type for JSON response
header('Content-Type: application/json');

// Initialize response array
$response = [
    "status" => "error",
    "message" => "An unexpected error occurred."
];

// Validate that the request method is POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    $response['message'] = "Invalid request method. Only POST is allowed.";
    echo json_encode($response);
    exit();
}

// Get and sanitize POST data
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$password = isset($_POST['password']) ? trim($_POST['password']) : '';

// Validate input fields
if (empty($email) || empty($password)) {
    $response['message'] = "Email and password are required.";
    echo json_encode($response);
    exit();
}

// Validate email format
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $response['message'] = "Invalid email format.";
    echo json_encode($response);
    exit();
}

// Query to check if the user exists and fetch data
$query = "SELECT id, name, email, password, created_at FROM users WHERE email = ?";
$stmt = $conn->prepare($query);
if (!$stmt) {
    $response['message'] = "Database query preparation failed.";
    echo json_encode($response);
    exit();
}
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();

if ($result && $result->num_rows > 0) {
    $user = $result->fetch_assoc();

    // Verify the password
    if (password_verify($password, $user['password'])) {
        // Successful login
        $response['status'] = "success";
        $response['message'] = "Login successful.";
        $response['data'] = [
            "id" => $user['id'],
            "name" => $user['name'],
            "email" => $user['email'],
            "created_at" => $user['created_at']
        ];
    } else {
        // Invalid password
        $response['message'] = "Invalid password.";
    }
} else {
    // User not found
    $response['message'] = "User not found.";
}

// Send the JSON response
echo json_encode($response);
exit();
?>

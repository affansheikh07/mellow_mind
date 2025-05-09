<?php
// Include database connection
require '../db.php';

// Enable error reporting for debugging (remove in production)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Set content type for JSON response
header('Content-Type: application/json');

$response = [
    "status" => "error",
    "message" => "An unexpected error occurred."
];

// Validate the request method
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    $response['message'] = "Invalid request method. Only POST is allowed.";
    echo json_encode($response);
    exit();
}

// Get email and passwords from POST request
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$new_password = isset($_POST['password']) ? trim($_POST['password']) : '';
$confirm_password = isset($_POST['confirm_password']) ? trim($_POST['confirm_password']) : '';

// Validate input
if (empty($email) || empty($new_password) || empty($confirm_password)) {
    $response['message'] = "All fields are required.";
    echo json_encode($response);
    exit();
}

if ($new_password !== $confirm_password) {
    $response['message'] = "Passwords do not match.";
    echo json_encode($response);
    exit();
}

// ===== NEW: Check if email has a valid reset request =====
$query = "SELECT email FROM password_resets WHERE email = ? AND created_at > (NOW() - INTERVAL 1 HOUR)";
$stmt = $conn->prepare($query);
if (!$stmt) {
    $response['message'] = "Failed to prepare database query.";
    echo json_encode($response);
    exit();
}
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    $response['message'] = "No valid password reset request found for this email or it has expired.";
    echo json_encode($response);
    exit();
}

// Hash the new password
$hashed_password = password_hash($new_password, PASSWORD_BCRYPT);

// Update the password in the users table
$query = "UPDATE users SET password = ? WHERE email = ?";
$stmt = $conn->prepare($query);
if (!$stmt) {
    $response['message'] = "Failed to prepare database query.";
    echo json_encode($response);
    exit();
}
$stmt->bind_param("ss", $hashed_password, $email);

if ($stmt->execute()) {
    // Delete the reset entry after successful password reset
    $query = "DELETE FROM password_resets WHERE email = ?";
    $stmt = $conn->prepare($query);
    $stmt->bind_param("s", $email);
    $stmt->execute();

    $response['status'] = "success";
    $response['message'] = "Password reset successfully.";
} else {
    $response['message'] = "Failed to reset password.";
}

echo json_encode($response);
exit();
?>
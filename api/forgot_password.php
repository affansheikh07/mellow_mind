<?php
// Include database connection and mailer setup (if using PHPMailer)
require '../db.php'; // Ensure the path is correct
require '../mailer.php'; // Optional: PHPMailer setup for sending emails

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

// Get email from POST request
$email = isset($_POST['email']) ? trim($_POST['email']) : '';

// Validate email
if (empty($email)) {
    $response['message'] = "Email is required.";
    echo json_encode($response);
    exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $response['message'] = "Invalid email format.";
    echo json_encode($response);
    exit();
}

// Check if the email exists in the users table
$query = "SELECT * FROM users WHERE email = ?";
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
    $response['message'] = "No account found with that email.";
    echo json_encode($response);
    exit();
}

// Generate a reset token
$token = bin2hex(random_bytes(50));

// Insert the token into the password_resets table
$query = "INSERT INTO password_resets (email, token) VALUES (?, ?)
          ON DUPLICATE KEY UPDATE token = VALUES(token), created_at = CURRENT_TIMESTAMP";
$stmt = $conn->prepare($query);
if (!$stmt) {
    $response['message'] = "Failed to prepare database query.";
    echo json_encode($response);
    exit();
}
$stmt->bind_param("ss", $email, $token);

if ($stmt->execute()) {
    // Send the reset email (using PHPMailer or a similar library)
    $resetLink = "http://yourdomain.com/reset_password.php?token=$token";
    $subject = "Password Reset Request";
    $body = "Click the link below to reset your password: \n\n$resetLink";

    // Uncomment if using PHPMailer
    /*
    $mail->addAddress($email);
    $mail->Subject = $subject;
    $mail->Body = $body;

    if (!$mail->send()) {
        $response['message'] = "Failed to send reset email. Try again later.";
        echo json_encode($response);
        exit();
    }
    */

    // Simulate email sending for now
    $response['status'] = "success";
    $response['message'] = "Password reset email sent successfully.";
    $response['reset_link'] = $resetLink; // Only for debugging; remove in production
} else {
    $response['message'] = "Failed to generate reset token.";
}

echo json_encode($response);
exit();
?>

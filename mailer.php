<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

// Include Composer autoload
require_once __DIR__ . '/vendor/autoload.php'; // Ensure this file exists

function sendEmail($to, $subject, $body) {
    $mail = new PHPMailer(true);

    try {
        // Enable SMTP debugging (for troubleshooting, set to 0 for production)
        $mail->SMTPDebug = 2;
        $mail->Debugoutput = 'html';

        // SMTP Configuration
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com'; 
        $mail->SMTPAuth = true;
        $mail->Username = 'your_email@gmail.com'; // Replace with your Gmail
        $mail->Password = 'your_app_password'; // Use Gmail App Password
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port = 587;

        // Email sender and recipient
        $mail->setFrom('your_email@gmail.com', 'Mellow Mind');
        $mail->addAddress($to);

        // Email content
        $mail->isHTML(true);
        $mail->Subject = $subject;
        $mail->Body = $body;

        $mail->send();
        return true;
    } catch (Exception $e) {
        error_log('Mailer Error: ' . $mail->ErrorInfo);
        return false;
    }
}
?>

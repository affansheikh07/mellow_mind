<?php
require 'mailer.php';

$email = 'ayeshkhalid05@gmail.com'; // Replace with the recipient's email
$subject = 'Test Email from Mellow Mind';
$body = '<h1>Hello!</h1><p>This is a test email sent from your PHP app using PHPMailer.</p>';

if (sendEmail($email, $subject, $body)) {
    echo 'Email sent successfully!';
} else {
    echo 'Failed to send email.';
}
?>

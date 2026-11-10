<?php
/**
 * Rise Joe — enquiry handler
 * Receives every website form and delivers it by authenticated SMTP to the
 * agency inbox, then emails the visitor a confirmation with a reference number.
 *
 * ▸ SMTP settings live in includes/mail-config.php. Nothing needs editing here.
 */
define('RJ_MAIL', true);
require __DIR__ . '/includes/mailer.php';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

function respond(bool $ok, string $message, int $code = 200, array $extra = []): void {
    http_response_code($code);
    echo json_encode(['ok' => $ok, 'message' => $message] + $extra);
    exit;
}
function clean_line(string $v, int $max = 300): string {
    $v = trim(preg_replace('/[\r\n\t]+/', ' ', $v));
    return mb_substr($v, 0, $max);
}
function clean_text(string $v, int $max = 5000): string {
    return mb_substr(trim(str_replace("\0", '', $v)), 0, $max);
}
function label_for(string $key): string {
    return ucfirst(str_replace(['_', '-'], ' ', $key));
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    respond(false, 'Method not allowed.', 405);
}

$cfg = rj_config();
if (rj_config_incomplete($cfg)) {
    rj_log('Enquiry rejected: includes/mail-config.php still contains placeholder values.');
    respond(false, 'Our enquiry form is being set up.', 503);
}

// ---------- Spam protection: honeypot + minimum fill time + rate limit ----------
if (!empty($_POST['website'])) {
    respond(true, 'Thank you.');            // silently accept bots
}
$ts = isset($_POST['_ts']) ? (int) $_POST['_ts'] : 0;
if ($ts > 0 && (round(microtime(true) * 1000) - $ts) < 2500) {
    respond(false, 'That was quick! Please take a moment and submit again.', 429);
}
if (session_status() === PHP_SESSION_NONE) { @session_start(); }
$now = time();
$_SESSION['rj_sends'] = array_values(array_filter($_SESSION['rj_sends'] ?? [], function ($t) use ($now) { return $t > $now - 600; }));
if (count($_SESSION['rj_sends']) >= 6) {
    respond(false, 'Too many enquiries in a short time. Please try again in a few minutes.', 429);
}

// ---------- Required shared fields ----------
$name    = clean_line($_POST['name'] ?? '', 120);
$email   = clean_line($_POST['email'] ?? '', 160);
$service = clean_line($_POST['_service'] ?? 'General enquiry', 160);
$consent = !empty($_POST['consent']);

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(false, 'Please provide your name and a valid email address.', 422);
}
if (!$consent) {
    respond(false, 'Please accept the privacy consent to continue.', 422);
}

// ---------- Collect every other submitted field ----------
$skip = ['website', '_ts', '_service', 'consent'];
$rows = [];
foreach ($_POST as $key => $value) {
    if (in_array($key, $skip, true)) continue;
    $key = preg_replace('/[^a-zA-Z0-9_\-]/', '', (string) $key);
    if ($key === '') continue;
    if (is_array($value)) {
        $value = implode(', ', array_map(function ($v) { return clean_line((string) $v, 120); }, $value));
    } else {
        $value = clean_text((string) $value);
    }
    if ($value === '') continue;
    $rows[label_for($key)] = $value;
    if (count($rows) > 60) break;
}

$ref  = 'RJ-' . strtoupper(substr(bin2hex(random_bytes(4)), 0, 6));
$ip   = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$when = date('D, d M Y H:i');
$page = clean_line($_SERVER['HTTP_REFERER'] ?? '', 300);

// ---------- Email to agency ----------
$tableRows = '';
foreach ($rows as $label => $value) {
    $tableRows .= '<tr><td style="padding:10px 14px;border-bottom:1px solid #eee;color:#8a6a2a;font:600 13px Arial;vertical-align:top;width:200px">'
        . htmlspecialchars($label) . '</td><td style="padding:10px 14px;border-bottom:1px solid #eee;font:14px Arial;color:#222">'
        . nl2br(htmlspecialchars($value)) . '</td></tr>';
}
$html = '<div style="background:#f6f3ee;padding:30px"><div style="max-width:640px;margin:auto;background:#fff;border-radius:10px;overflow:hidden">'
    . '<div style="background:#0b0907;padding:24px 28px;color:#f1d28a;font:600 18px Arial;letter-spacing:2px">RISE JOE · NEW ENQUIRY</div>'
    . '<div style="padding:24px 28px"><p style="font:15px Arial;color:#333;margin:0 0 6px"><b>Service:</b> ' . htmlspecialchars($service) . '</p>'
    . '<p style="font:13px Arial;color:#888;margin:0 0 18px">Reference ' . $ref . ' · ' . $when . ' · IP ' . htmlspecialchars($ip)
    . ($page ? '<br>Sent from ' . htmlspecialchars($page) : '') . '</p>'
    . '<table style="width:100%;border-collapse:collapse">' . $tableRows . '</table>'
    . '<p style="font:13px Arial;color:#888;margin:22px 0 0">Reply to this email to respond directly to ' . htmlspecialchars($name) . '.</p></div></div></div>';

$sent = rj_send([
    'to'         => $cfg['to_email'],
    'to_name'    => $cfg['to_name'] ?? '',
    'cc'         => $cfg['cc'] ?? [],
    'bcc'        => $cfg['bcc'] ?? [],
    'reply_to'   => $email,
    'reply_name' => $name,
    'subject'    => "New enquiry: {$service} — {$name} [{$ref}]",
    'html'       => $html,
], $err);

if (!$sent) {
    rj_log("Enquiry {$ref} NOT delivered ({$service}, {$email}): {$err}");
    rj_save_failed($ref, ['service' => $service, 'name' => $name, 'email' => $email, 'fields' => $rows]);
    respond(false, 'Sorry, we couldn\'t send your enquiry just now.', 502);
}
$_SESSION['rj_sends'][] = $now;

// ---------- Confirmation to visitor ----------
if (!empty($cfg['send_autoreply'])) {
    $ackHtml = '<div style="background:#0b0907;padding:40px 20px"><div style="max-width:560px;margin:auto;background:#14110d;border:1px solid #3a2e1a;border-radius:14px;padding:36px;color:#e9e2d4;font:15px/1.6 Arial">'
        . '<div style="color:#f1d28a;font:600 16px Arial;letter-spacing:3px;margin-bottom:22px">RISE JOE</div>'
        . '<p>Hi ' . htmlspecialchars($name) . ',</p>'
        . '<p>Thank you for contacting Rise Joe E-Commerce Agency. We have received your enquiry about <b style="color:#f1d28a">' . htmlspecialchars($service) . '</b>.</p>'
        . '<p>Your reference number is <b style="color:#f1d28a">' . $ref . '</b>. A member of the relevant team will review your details and get back to you shortly.</p>'
        . '<p style="color:#9a907f;font-size:13px;margin-top:28px">For your security, we will never ask for your marketplace passwords, OTP codes or verification credentials.</p>'
        . '<p style="margin-top:28px">— Team Rise Joe<br><span style="color:#9a907f;font-size:13px">Plaza No. 26B, Pak Arab Housing Society, Lahore</span></p></div></div>';
    $ackOk = rj_send([
        'to'         => $email,
        'to_name'    => $name,
        'reply_to'   => $cfg['to_email'],
        'reply_name' => $cfg['from_name'],
        'subject'    => "We've received your enquiry [{$ref}]",
        'html'       => $ackHtml,
    ], $ackErr);
    if (!$ackOk) {
        rj_log("Confirmation for {$ref} to {$email} failed (enquiry itself was delivered): {$ackErr}");
    }
}

respond(true, 'Thank you — your enquiry has been sent.', 200, ['ref' => $ref]);

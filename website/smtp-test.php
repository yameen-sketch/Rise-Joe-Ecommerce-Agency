<?php
/**
 * Rise Joe — SMTP connection test
 * Disabled unless 'test_key' is set in includes/mail-config.php.
 * Usage:  https://yourdomain.com/smtp-test.php?key=YOUR-TEST-KEY
 * It connects to the SMTP server, logs in and sends one test email to
 * 'to_email', showing the full conversation (password hidden).
 */
define('RJ_MAIL', true);
require __DIR__ . '/includes/mailer.php';

header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');

$c   = rj_config();
$key = (string) ($c['test_key'] ?? '');
if (strlen($key) < 16 || !hash_equals($key, (string) ($_GET['key'] ?? ''))) {
    http_response_code(404);
    header('Content-Type: text/plain; charset=utf-8');
    exit('Not found');
}

header('Content-Type: text/html; charset=utf-8');

// Hide anything that could reveal the login, whichever AUTH method is used.
$secrets = array_filter([
    (string) $c['smtp_pass'],
    base64_encode((string) $c['smtp_pass']),
    base64_encode("\0" . $c['smtp_user'] . "\0" . $c['smtp_pass']),
]);
$log = [];
$debugOut = function ($str) use (&$log, $secrets) {
    $log[] = str_replace($secrets, '[hidden]', rtrim($str));
};

$ok = false; $error = '';
$started = microtime(true);
try {
    $m = rj_mailer($c, \PHPMailer\PHPMailer\SMTP::DEBUG_SERVER, $debugOut);
    $m->addAddress($c['to_email'], $c['to_name'] ?? '');
    $m->isHTML(true);
    $m->Subject = 'SMTP test — Rise Joe website (' . date('Y-m-d H:i:s') . ')';
    $m->Body = '<p>This is a test email from <b>smtp-test.php</b> on the Rise Joe website.</p>'
             . '<p>If you can read this, SMTP is working and website enquiries will be delivered to this inbox.</p>';
    $m->AltBody = rj_plain($m->Body);
    $m->send();
    $ok = true;
} catch (\Throwable $e) {
    $error = isset($m) && $m->ErrorInfo ? $m->ErrorInfo : $e->getMessage();
}
$secs = number_format(microtime(true) - $started, 2);
$e = function ($v) { return htmlspecialchars((string) $v, ENT_QUOTES, 'UTF-8'); };
?><!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SMTP test</title>
<style>
 body{margin:0;background:#070605;color:#e9e2d4;font:15px/1.6 system-ui,-apple-system,Segoe UI,Arial,sans-serif;padding:32px 16px}
 .w{max-width:860px;margin:auto} h1{font-weight:500;color:#f1d28a;margin:0 0 20px}
 .s{padding:16px 20px;border-radius:10px;margin-bottom:20px;font-weight:600}
 .ok{background:#123a20;color:#9be7b0;border:1px solid #2b6b3e} .bad{background:#3a1212;color:#f3a6a6;border:1px solid #6b2b2b}
 table{border-collapse:collapse;margin-bottom:20px} td{padding:4px 18px 4px 0;vertical-align:top} td:first-child{color:#9a907f}
 pre{background:#14110d;border:1px solid #3a2e1a;border-radius:10px;padding:16px;overflow:auto;font-size:12.5px;line-height:1.5;white-space:pre-wrap;word-break:break-all}
 .n{color:#9a907f;font-size:13px}
</style></head><body><div class="w">
<h1>SMTP connection test</h1>
<?php if ($ok): ?>
  <div class="s ok">✓ Success. A test email was sent to <?= $e($c['to_email']) ?> in <?= $secs ?>s. Check that inbox (and spam folder).</div>
<?php else: ?>
  <div class="s bad">✗ Failed: <?= $e($error) ?></div>
<?php endif; ?>
<table>
 <tr><td>Server</td><td><?= $e($c['smtp_host']) ?>:<?= $e($c['smtp_port']) ?> (<?= $e(strtoupper($c['smtp_secure'] ?: 'none')) ?>)</td></tr>
 <tr><td>Login</td><td><?= $e($c['smtp_user']) ?></td></tr>
 <tr><td>From</td><td><?= $e($c['from_email']) ?></td></tr>
 <tr><td>Deliver to</td><td><?= $e($c['to_email']) ?></td></tr>
 <tr><td>PHP</td><td><?= $e(PHP_VERSION) ?> · OpenSSL <?= extension_loaded('openssl') ? 'yes' : 'NO' ?></td></tr>
</table>
<pre><?= $e(implode("\n", $log)) ?: 'No SMTP conversation recorded.' ?></pre>
<p class="n">When you have finished testing, set <code>'test_key' =&gt; ''</code> in includes/mail-config.php to disable this page.</p>
</div></body></html>

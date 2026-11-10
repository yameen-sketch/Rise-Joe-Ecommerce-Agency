<?php
/**
 * Rise Joe — SMTP mailer (PHPMailer wrapper)
 */
defined('RJ_MAIL') or exit;

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception as MailException;

require_once __DIR__ . '/PHPMailer/Exception.php';
require_once __DIR__ . '/PHPMailer/PHPMailer.php';
require_once __DIR__ . '/PHPMailer/SMTP.php';

/** Load settings. RJ_MAIL_CONFIG env var lets a test environment point to another file. */
function rj_config(): array {
    static $cfg = null;
    if ($cfg === null) {
        $path = getenv('RJ_MAIL_CONFIG') ?: __DIR__ . '/mail-config.php';
        $cfg = require $path;
    }
    return $cfg;
}

/** True when the config still holds the shipped placeholder values. */
function rj_config_incomplete(array $c): bool {
    return $c['smtp_pass'] === 'YOUR-MAILBOX-PASSWORD'
        || strpos($c['smtp_user'], 'yourdomain.com') !== false
        || strpos($c['to_email'], 'yourdomain.com') !== false;
}

/** Build a configured PHPMailer instance. */
function rj_mailer(array $c, int $debug = 0, ?callable $debugOut = null): PHPMailer {
    $m = new PHPMailer(true);
    $m->isSMTP();
    $m->Host       = $c['smtp_host'];
    $m->Port       = (int) $c['smtp_port'];
    $m->SMTPAuth   = (bool) $c['smtp_auth'];
    $m->Username   = $c['smtp_user'];
    $m->Password   = $c['smtp_pass'];
    $m->Timeout    = (int) ($c['timeout'] ?? 20);
    $m->CharSet    = PHPMailer::CHARSET_UTF8;
    $m->Encoding   = PHPMailer::ENCODING_BASE64;
    $m->XMailer    = ' ';                                   // don't advertise the library
    $secure = strtolower((string) $c['smtp_secure']);
    if ($secure === 'ssl') {
        $m->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;
    } elseif ($secure === 'tls') {
        $m->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    } else {
        $m->SMTPSecure = '';
        $m->SMTPAutoTLS = false;
    }
    $m->setFrom($c['from_email'], $c['from_name']);
    $m->Sender = $c['from_email'];                          // envelope sender / Return-Path
    if ($debug) {
        $m->SMTPDebug = $debug;
        $m->Debugoutput = $debugOut ?? 'echo';
    }
    return $m;
}

/** Turn HTML email into a readable plain-text alternative. */
function rj_plain(string $html): string {
    $t = preg_replace(['~<br\s*/?>~i', '~</(p|div|tr|h\d)>~i', '~</td>~i'], ["\n", "\n\n", "  "], $html);
    $t = html_entity_decode(strip_tags($t), ENT_QUOTES | ENT_HTML5, 'UTF-8');
    return trim(preg_replace("/\n{3,}/", "\n\n", preg_replace('/[ \t]+/', ' ', $t)));
}

/**
 * Send one email. Returns true on success; on failure returns false and sets $error.
 * $opts: to, to_name, subject, html, reply_to, reply_name, cc[], bcc[]
 */
function rj_send(array $opts, ?string &$error = null): bool {
    $c = rj_config();
    $error = null;
    $m = null;
    try {
        $m = rj_mailer($c);
        $m->addAddress($opts['to'], $opts['to_name'] ?? '');
        foreach ($opts['cc'] ?? [] as $a)  { if ($a) $m->addCC($a); }
        foreach ($opts['bcc'] ?? [] as $a) { if ($a) $m->addBCC($a); }
        if (!empty($opts['reply_to'])) $m->addReplyTo($opts['reply_to'], $opts['reply_name'] ?? '');
        $m->isHTML(true);
        $m->Subject = $opts['subject'];
        $m->Body    = $opts['html'];
        $m->AltBody = rj_plain($opts['html']);
        $m->send();
        return true;
    } catch (MailException $e) {
        $error = 'SMTP: ' . (($m && $m->ErrorInfo) ? $m->ErrorInfo : $e->getMessage());
    } catch (\Throwable $e) {
        $error = 'Mailer: ' . $e->getMessage();
    }

    // Optional last resort: PHP mail()
    if (!empty($c['fallback_to_mail'])) {
        $headers = [
            'MIME-Version: 1.0',
            'Content-Type: text/html; charset=UTF-8',
            'From: =?UTF-8?B?' . base64_encode($c['from_name']) . '?= <' . $c['from_email'] . '>',
        ];
        if (!empty($opts['reply_to'])) $headers[] = 'Reply-To: ' . $opts['reply_to'];
        $subject = '=?UTF-8?B?' . base64_encode($opts['subject']) . '?=';
        if (@mail($opts['to'], $subject, $opts['html'], implode("\r\n", $headers), '-f' . $c['from_email'])) {
            rj_log('SMTP failed, delivered with mail() fallback. ' . $error);
            $error = null;
            return true;
        }
        $error .= ' | mail() fallback also failed';
    }
    return false;
}

/** Append a line to the private error log (never logs passwords). */
function rj_log(string $line): void {
    $c = rj_config();
    $line = str_replace((string) $c['smtp_pass'], '[hidden]', $line);
    @file_put_contents(__DIR__ . '/mail-errors.log', '[' . date('Y-m-d H:i:s') . '] ' . $line . PHP_EOL, FILE_APPEND | LOCK_EX);
}

/** Keep a private copy of an enquiry that could not be emailed, so nothing is lost. */
function rj_save_failed(string $ref, array $data): void {
    if (empty(rj_config()['save_failed'])) return;
    $row = json_encode(['time' => date('c'), 'ref' => $ref] + $data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    @file_put_contents(__DIR__ . '/failed-enquiries.log', $row . PHP_EOL, FILE_APPEND | LOCK_EX);
}

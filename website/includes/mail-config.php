<?php
/**
 * Rise Joe — email / SMTP settings
 * ------------------------------------------------------------------
 * ▸ EDIT THE VALUES MARKED "CHANGE ME" BEFORE GOING LIVE.
 *
 * Hostinger setup (hPanel → Emails → Email Accounts):
 *   1. Create a mailbox on your domain, e.g. no-reply@yourdomain.com
 *   2. Put that address and its password in smtp_user / smtp_pass below.
 *   3. Leave host / port / encryption as they are: these are Hostinger's
 *      official SMTP settings.
 *
 * This folder is blocked from the web by includes/.htaccess, so the
 * password is never served to visitors.
 */
defined('RJ_MAIL') or exit;

return [
    // ---- SMTP server (Hostinger defaults) ----
    'smtp_host'   => 'smtp.hostinger.com',
    'smtp_port'   => 465,          // 465 = SSL (recommended) · 587 = TLS
    'smtp_secure' => 'ssl',        // 'ssl' for port 465 · 'tls' for port 587
    'smtp_auth'   => true,

    // ---- Mailbox used to send (must be on your own domain) ----
    'smtp_user'   => 'admin@risejoe.com',
    'smtp_pass'   => 'Yaseen@786$$',

    // "From" address. On Hostinger this MUST be the same as smtp_user.
    'from_email'  => 'admin@risejoe.com',
    'from_name'   => 'Rise Joe E-Commerce Agency',

    // ---- Where enquiries are delivered ----
    'to_email'    => 'admin@risejoe.com',            // the inbox you check
    'to_name'     => 'Rise Joe Enquiries',
    'cc'          => [],           // e.g. ['manager@yourdomain.com']
    'bcc'         => [],

    // ---- Behaviour ----
    'send_autoreply'   => true,    // email the visitor a confirmation with reference no.
    'fallback_to_mail' => false,   // if SMTP fails, try PHP mail() as a last resort
    'save_failed'      => true,    // keep a private copy of any enquiry that could not be emailed
    'timeout'          => 20,      // seconds

    // ---- SMTP connection test (smtp-test.php) ----
    // Set a long random string (16+ characters) to enable the test page, then open
    //   https://yourdomain.com/smtp-test.php?key=THAT-STRING
    // Set it back to '' when you have finished testing.
    'test_key'    => '',
];

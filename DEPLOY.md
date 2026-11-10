# Rise Joe Website — Deploying to Hostinger

## 1. Before uploading: replace the placeholders

These details weren't in the project files, so they are placeholders for now:

| What | Where to change it |
|---|---|
| Domain | `CONFIG` at the top of `build.py`, then run `python3 build.py` |
| SMTP login, the inbox that receives enquiries | `website/includes/mail-config.php` (see section 2) |

If you can't run Python, send the details to your developer, or find and replace them in the `.html` files:
- `https://yourdomain.com`

## 2. Email (SMTP) setup

All 14 website forms send email through **authenticated SMTP**, using PHPMailer (bundled, no install needed). This is far more reliable than PHP `mail()`: messages are signed by Hostinger's mail server, so they reach the inbox instead of spam.

1. In **hPanel → Emails → Email Accounts**, create a mailbox for sending, e.g. `no-reply@yourdomain.com`, and note its password.
2. Open `website/includes/mail-config.php` (in File Manager, right-click → Edit) and fill in:
   - `smtp_user` and `from_email`: that mailbox (the two must be the same on Hostinger)
   - `smtp_pass`: its password
   - `to_email`: the inbox where enquiries should arrive (any address, e.g. Gmail is fine)
   - optional: `cc` / `bcc` for extra recipients
3. Leave `smtp_host` = `smtp.hostinger.com`, port `465`, `ssl`. These are Hostinger's settings. If port 465 is blocked, use `587` with `tls`.
4. **Test the connection:** set `test_key` to a long random string (e.g. `rj-test-8f3k2m9q7x1z`), then open `https://yourdomain.com/smtp-test.php?key=rj-test-8f3k2m9q7x1z`. It logs in, sends a test email to `to_email` and shows the full SMTP conversation (password hidden). **When it says Success, set `test_key` back to `''`.**
5. Submit one real form on the site and check you receive both the enquiry and the visitor confirmation.

Until the placeholders are replaced, the forms politely refuse to send (they never fail silently).

**If something goes wrong:**
- "SMTP Error: Could not authenticate": wrong password, or `smtp_user` is not a full email address.
- "Could not connect": try port `587` with `tls`.
- Every failure is written to `includes/mail-errors.log`. Any enquiry that could not be emailed is saved in `includes/failed-enquiries.log`, so nothing is lost. Both files are blocked from the web.
- Emails landing in spam: in hPanel → Emails → your domain, make sure SPF, DKIM and DMARC show as active (Hostinger sets these up when the domain uses its nameservers).

## 3. Upload with File Manager

1. Log in to Hostinger and open **hPanel → Websites → Manage → File Manager**.
2. Open the `public_html` folder. Delete Hostinger's default `default.php` or `index.php` if there is one.
3. Upload `Rise-Joe-Website.zip`, right-click it and choose **Extract**, then delete the zip.
4. Check that `index.html`, `send.php`, `.htaccess` and the `assets/` folder sit **directly inside** `public_html`, not inside a subfolder.
5. In **hPanel → Security → SSL**, make sure SSL is active. The site redirects to HTTPS automatically.

## 4. Test

- Open your domain. You should see the preloader, then the animated hero.
- Run `smtp-test.php` as described in section 2, then submit a form on any page and check that the email arrives in `to_email`.

## What's included

- 20 pages: Home, About, Students, Clients, Investors, a Services hub, 10 service pages, Contact, Privacy, Terms and a 404 page.
- `send.php` delivers every enquiry by SMTP (PHPMailer 6.9.3 in `includes/`) and sends the visitor a confirmation with a reference number. Reply-To is set to the visitor, so you can reply straight from your inbox.
- Spam protection: hidden honeypot field, minimum fill time and a limit of 6 enquiries per visitor per 10 minutes.
- `.htaccess` handles HTTPS, clean URLs with no `.html` (`/about`, `/services/vps-services`, with old `.html` links 301-redirected), caching, compression and security headers.
- No database, no build tools and no external libraries. GSAP and Lenis are bundled in `assets/vendor/`.

## Local preview

Run `python3 preview_server.py` and open http://localhost:8765/. It mirrors the clean-URL rules in `.htaccess`. It does not run PHP, so forms don't send from it.

To test the forms locally (real emails through Hostinger SMTP), run the PHP preview with Docker instead:

```
docker run -d --name risejoe-preview -p 8765:80 -v "$PWD/website":/var/www/html php:8.2-apache sh -c "a2enmod rewrite headers expires >/dev/null && sed -i 's/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf && apache2-foreground"
```

Stop it with `docker rm -f risejoe-preview`.

## SEO after launch

1. **Set your real domain first.** Change `site_url` in `CONFIG` in `build.py`, then run `python3 build.py`. Canonical tags, the sitemap, robots.txt, social previews and schema markup all use it. While it still says `https://yourdomain.com`, Google will index the wrong addresses.
2. **Social links** are set in `CONFIG` (Instagram, Facebook, TikTok, LinkedIn). They appear in every footer and in the schema (`sameAs`).
3. **Google Search Console.** Add and verify your domain, then submit `https://yourdomain.com/sitemap.xml`.
4. **Google Business Profile.** Create or claim one for the head office address. For local "e-commerce agency Lahore" searches, it matters more than anything on the site.
5. **Test the markup** at https://search.google.com/test/rich-results and https://validator.schema.org.
6. Page titles and descriptions live in the `SEO` dictionary in `build.py`. Edit them there.

# Deploy without SSH/pem

If the `.pem` key or SSH username is not available, the bot cannot be pushed from this computer directly. Use one of these server-side options instead:

1. Open the server with AWS Systems Manager Session Manager, EC2 Serial Console, hosting web terminal, or any existing browser console.
2. Upload `prohub-bot-release.zip` to `/tmp/prohub-bot-release.zip`.
3. Run:

```bash
sudo unzip -q /tmp/prohub-bot-release.zip -d /tmp/prohub-src
sudo bash /tmp/prohub-src/deploy/install.sh /tmp/prohub-bot-release.zip
sudo BOT_TOKEN='token' ADMIN_ID='your_telegram_id' REQUIRED_CHANNEL='@premiumilova202' CHANNEL_ID='-1003825980145' bash /tmp/prohub-src/deploy/write-env.sh
sudo systemctl restart prohub-bot prohub-api
```

Useful checks:

```bash
sudo systemctl status prohub-bot prohub-api
sudo journalctl -u prohub-bot -f
curl http://127.0.0.1:5000/health
```

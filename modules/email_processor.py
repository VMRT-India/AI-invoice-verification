"""
Email integration for automatic invoice processing
"""
import imaplib
import email
from email.header import decode_header
import os
from pathlib import Path
import config


class EmailProcessor:
    def __init__(self):
        self.server = config.EMAIL_SERVER
        self.port = config.EMAIL_PORT
        self.username = config.EMAIL_USERNAME
        self.password = config.EMAIL_PASSWORD

    def connect(self):
        """Connect to email server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.server, self.port)
            self.mail.login(self.username, self.password)
            return True
        except Exception as e:
            print(f"Failed to connect to email: {e}")
            return False

    def fetch_invoice_emails(self, folder='INBOX', days=7):
        """
        Fetch emails containing invoice attachments
        """
        if not self.connect():
            return []

        try:
            self.mail.select(folder)

            # Search for emails with attachments from last N days
            status, messages = self.mail.search(None, f'(SINCE {days}) (HEADER Content-Type "application/pdf")')

            if status != 'OK':
                return []

            email_ids = messages[0].split()
            invoices = []

            for email_id in email_ids:
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')

                if status != 'OK':
                    continue

                msg = email.message_from_bytes(msg_data[0][1])

                # Extract subject and sender
                subject = self._decode_header(msg['Subject'])
                sender = self._decode_header(msg['From'])

                # Check if email contains "invoice" keywords
                if 'invoice' in subject.lower() or 'bill' in subject.lower():
                    # Process attachments
                    attachments = self._extract_attachments(msg, email_id.decode())

                    if attachments:
                        invoices.append({
                            'email_id': email_id.decode(),
                            'subject': subject,
                            'sender': sender,
                            'attachments': attachments
                        })

            self.mail.close()
            self.mail.logout()

            return invoices

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def _extract_attachments(self, msg, email_id):
        """Extract PDF attachments from email"""
        attachments = []

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            if filename and filename.lower().endswith('.pdf'):
                # Save attachment
                filepath = config.INVOICE_DIR / f"{email_id}_{filename}"

                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))

                attachments.append({
                    'filename': filename,
                    'filepath': str(filepath)
                })

        return attachments

    @staticmethod
    def _decode_header(header):
        """Decode email header"""
        if header is None:
            return ""

        decoded = decode_header(header)
        header_text = ""

        for text, encoding in decoded:
            if isinstance(text, bytes):
                header_text += text.decode(encoding or 'utf-8')
            else:
                header_text += text

        return header_text

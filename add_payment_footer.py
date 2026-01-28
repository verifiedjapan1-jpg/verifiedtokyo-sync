#!/usr/bin/env python3
"""Add payment methods logos to footer"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find </body> tag and add footer before it
footer_html = '''
    <!-- Footer -->
    <footer style="background: #f5f5f5; padding: 40px 0; margin-top: 80px;">
        <div style="max-width: 1400px; margin: 0 auto; padding: 0 40px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 40px; margin-bottom: 30px;">
                <div>
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #1a1a1a;">Verified Tokyo</h3>
                    <p style="font-size: 14px; color: #666; line-height: 1.8;">We offer high-quality secondhand brand bags<br>at trustworthy prices.</p>
                </div>
                <div>
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #1a1a1a;">Contact</h3>
                    <p style="font-size: 14px; color: #666; line-height: 1.8;">Email: info@t-family.jp<br>Phone: 03-1234-5678</p>
                </div>
                <div>
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #1a1a1a;">Payment Methods</h3>
                    <img src="images/payment-methods.png" alt="Accepted Payment Methods" style="max-width: 300px; height: auto; margin-top: 10px;">
                </div>
            </div>
            <div style="text-align: center; padding-top: 20px; border-top: 1px solid #ddd;">
                <p style="font-size: 14px; color: #666;">&copy; 2026 Verified Tokyo. All rights reserved.</p>
            </div>
        </div>
    </footer>
</body>
</html>'''

# Remove existing footer if present
if '<!-- Footer -->' in content:
    footer_start = content.find('<!-- Footer -->')
    content = content[:footer_start]

# Remove </body></html> if present
content = content.replace('</body>', '').replace('</html>', '')

# Add new footer
new_content = content + footer_html

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Payment methods added to footer!")
